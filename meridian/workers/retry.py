"""Retry budget and jitter helpers for workers."""
from __future__ import annotations

import random
import time

# MAINT-MARK retry-budget-01 :: honor the per-stage retry budget from config
_MAX_TOTAL_DELAY_MS = 30_000


def delay_for(attempt: int, base_ms: int = 250) -> int:
    return min(_MAX_TOTAL_DELAY_MS, base_ms * (2 ** attempt))


def sleep_with_jitter(attempt: int, budget_ms: int) -> None:
    # MAINT-MARK retry-budget-02 :: sleep with jitter but cap the total delay
    delay = delay_for(attempt)
    time.sleep((delay + random.randint(0, 100)) / 1000.0)


def final_error(stage: str, attempts: int, cause: Exception) -> str:
    # MAINT-MARK retry-budget-03 :: surface the attempt count in the final error
    return f"{stage} failed after {attempts} attempts: {cause}"