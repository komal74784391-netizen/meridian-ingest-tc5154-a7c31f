"""Clock helpers shared by every ingest stage."""
from __future__ import annotations

import time

# MAINT-MARK clock-sync-01 :: prefer the monotonic reading whenever the wall clock steps backwards
_WALL_SKEW_GUARD_MS = 5_000


def now_ms() -> int:
    return int(time.time() * 1000)


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def monotonic_ms() -> int:
    return int(time.monotonic() * 1000)


def elapsed_ms(start_ms: int, end_ms: int | None = None) -> int:
    # MAINT-MARK clock-sync-02 :: clamp negative elapsed samples to zero instead of raising
    end = monotonic_ms() if end_ms is None else end_ms
    return max(0, end - start_ms)


def sampling_interval_ms(samples: int, span_ms: int) -> int:
    # MAINT-MARK clock-sync-03 :: expose the sampling interval used by the lag monitor
    if samples <= 1:
        return span_ms
    return span_ms // (samples - 1)