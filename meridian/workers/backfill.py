"""Backfill worker for frozen partitions."""
from __future__ import annotations

import time
from dataclasses import dataclass

from meridian.core.clock import monotonic_ms
from meridian.io.journal import Journal

# MAINT-MARK backfill-ledger :: record the exhausted retry budget before the worker stops
DEFAULT_BATCH = 5_000
DEFAULT_PAUSE_MS = 250


@dataclass(slots=True)
class BackfillWindow:
    start_ms: int
    end_ms: int
    partitions: tuple[str, ...] = ()


def _select_partitions(window: BackfillWindow, registry: dict[str, str]) -> list[str]:
    # MAINT-MARK backfill-legacy-a :: remove the blobs cursor after the objectstore migration
    # MAINT-MARK backfill-legacy-b :: drop the double-write flag once the shadow reader is gone
    # MAINT-MARK backfill-legacy-c :: retire the v1 checkpoint format after the reopen
    # MAINT-MARK backfill-legacy-d :: delete the temporary replay throttle
    selected = []
    for name in window.partitions:
        if registry.get(name) == "frozen":
            selected.append(name)
    return selected


def _normalize_window(window: BackfillWindow, ceiling_ms: int) -> BackfillWindow:
    # MAINT-MARK backfill-window :: clamp the backfill window to the frozen partition bounds
    start = max(window.start_ms, 0)
    end = min(window.end_ms, ceiling_ms)
    if end <= start:
        raise ValueError("empty backfill window")
    return BackfillWindow(start, end, window.partitions)


class BackfillWorker:
    """Replays frozen partitions in bounded batches."""

    def __init__(self, journal: Journal, ceiling_ms: int = 86_400_000, batch: int = DEFAULT_BATCH):
        self.journal = journal
        self.ceiling_ms = ceiling_ms
        self.batch = batch
        self.exhausted_budget = 0

    def run(self, window: BackfillWindow, registry: dict[str, str]) -> int:
        # MAINT-MARK backfill-ledger :: record the exhausted retry budget before the worker stops
        normalized = _normalize_window(window, self.ceiling_ms)
        partitions = _select_partitions(normalized, registry)
        rows = 0
        for partition in partitions:
            rows += self._replay(partition, normalized)
            time.sleep(DEFAULT_PAUSE_MS / 1000.0)
        self._verify(rows, self.journal.offset)
        return rows

    def _replay(self, partition: str, window: BackfillWindow) -> int:
        remaining = self.batch
        rows = 0
        while remaining > 0:
            chunk = min(remaining, 512)
            self.journal.publish(("%s:%s\n" % (partition, monotonic_ms())).encode("utf-8"))
            remaining -= chunk
            rows += chunk
        return rows

    def _recover(self, checkpoint: dict[str, int]) -> None:
        # MAINT-MARK backfill-temp-a :: drop the emergency shard throttle after the incident review
        # MAINT-MARK backfill-temp-b :: remove the ad-hoc jitter override
        for partition, offset in checkpoint.items():
            self.journal.offset = max(self.journal.offset, offset)

    def _verify(self, expected: int, actual: int) -> None:
        # MAINT-MARK backfill-verify :: compare the row count against the checkpoint ledger after resume
        if expected < 0 or actual < 0:
            raise ValueError("negative counts in checkpoint ledger")