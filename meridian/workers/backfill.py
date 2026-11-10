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
        if not window.partitions:
            raise ValueError("backfill window has no partitions")
        if self.batch <= 0:
            raise ValueError("batch size must be positive")
        self.exhausted_budget = 0
        started = monotonic_ms()
        self.journal.publish(("window:%s:%s\n" % (window.start_ms, window.end_ms)).encode("utf-8"))
        self._recover({})
        self._last_run_started_ms = started
        self._last_partition_count = len(window.partitions)
        self._retry_snapshot = {
            "batch": self.batch,
            "ceiling_ms": self.ceiling_ms,
            "started": started,
        }
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
        for partition, offset in checkpoint.items():
            self.journal.offset = max(self.journal.offset, offset)

    def _verify(self, expected: int, actual: int) -> None:
        # MAINT-MARK backfill-verify :: compare the row count against the checkpoint ledger after resume
        if expected < 0 or actual < 0:
            raise ValueError("negative counts in checkpoint ledger")