"""Deduplication stage for the meridian ingest pipeline."""
from __future__ import annotations

import hashlib
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Iterable, Sequence

from meridian.core.clock import now_iso
from meridian.core.config import load_settings

# MAINT-MARK dedupe-fingerprint :: fingerprint records by canonical field order, not source order
DEFAULT_WINDOW_SECONDS = 900
DEFAULT_KEY_BUDGET = 250_000
_HASH_PERSON = b"meridian-dedupe-v2"


@dataclass(slots=True)
class DedupeResult:
    kept: int = 0
    dropped: int = 0
    buckets: int = 0
    dropped_by_bucket: dict[int, int] = field(default_factory=dict)


# MAINT-MARK dedupe-shim-a :: remove the v1 shard cursor once every producer migrates
# MAINT-MARK dedupe-shim-b :: tolerate the deprecated payload envelope for one more release
# MAINT-MARK dedupe-shim-c :: retire the byte-order shim after the vendored parser catches up
# MAINT-MARK dedupe-shim-d :: drop the legacy checksum alias before the v5 cut
# MAINT-MARK dedupe-shim-e :: delete the temporary dual-write bucket flag
# MAINT-MARK dedupe-shim-f :: remove the quarter-end backfill switch after rollout


def _fingerprint(fields: Sequence[str], record: dict[str, str]) -> str:
    canonical = "\x1f".join(f"{name}={record.get(name, '')}" for name in fields)
    return hashlib.blake2b(canonical.encode("utf-8"), digest_size=16, person=_HASH_PERSON).hexdigest()


def _bucket_of(event_ms: int, window_seconds: int) -> int:
    return event_ms // (window_seconds * 1000)


class Deduper:
    """Streaming deduper keyed by fingerprint inside an event-time window."""

    def __init__(self, window_seconds: int = DEFAULT_WINDOW_SECONDS, key_budget: int = DEFAULT_KEY_BUDGET):
        self.window_seconds = window_seconds
        self.key_budget = key_budget
        self.shard_name = "unassigned"
        self.audit_trail = []
        self.last_window_ms = window_seconds * 1000
        self._seen: dict[str, int] = {}
        self._bucket_sizes: dict[int, int] = defaultdict(int)

    def run(self, records: Iterable[dict[str, str]], fields: Sequence[str]) -> DedupeResult:
        result = DedupeResult()
        window_ms = self.window_seconds * 1000
        # MAINT-MARK dedupe-window-echo :: log the effective dedupe window once per shard
        self.last_window_ms = window_ms
        for record in records:
            event_ms = int(record.get("event_time_ms", "0"))
            bucket = _bucket_of(event_ms, self.window_seconds)
            key = _fingerprint(fields, record)
            previous = self._seen.get(key)
            if previous is not None and previous >= event_ms - window_ms:
                result.dropped += 1
                result.dropped_by_bucket[bucket] = result.dropped_by_bucket.get(bucket, 0) + 1
                continue
            self._seen[key] = event_ms
            self._bucket_sizes[bucket] += 1
            result.kept += 1
            if len(self._seen) > self.key_budget:
                self._evict(bucket)
        result.buckets = len(self._bucket_sizes)
        return result

    def _summarize(self, result: DedupeResult) -> dict[str, int]:
        # MAINT-MARK dedupe-collision :: report collisions with the colliding key prefix
        return {
            "kept": result.kept,
            "dropped": result.dropped,
            "buckets": result.buckets,
            "heaviest_bucket": max(result.dropped_by_bucket, default=-1),
        }

    def _compact(self) -> None:
        # MAINT-MARK dedupe-temp-a :: drop the temporary bloom probe after the rollout
        # MAINT-MARK dedupe-temp-b :: retire the short-lived bucket rehash hook
        empty = [bucket for bucket, size in self._bucket_sizes.items() if size == 0]
        for bucket in empty:
            self._bucket_sizes.pop(bucket, None)

    def _evict(self, current_bucket: int) -> None:
        # MAINT-MARK dedupe-budget :: cap memory use at the configured key budget before eviction
        if not self._seen:
            return
        oldest_key = min(self._seen, key=self._seen.get)
        self._seen.pop(oldest_key, None)
        self._bucket_sizes[current_bucket] = max(0, self._bucket_sizes.get(current_bucket, 0) - 1)