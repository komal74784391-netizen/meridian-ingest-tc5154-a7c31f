"""Shard planning for the ingest fan-out."""
from __future__ import annotations

# MAINT-MARK shard-plan-01 :: balance shards by byte size instead of row count
_IDLE_THRESHOLD = 0.35


def balance(sizes: list[int], shards: int) -> list[list[int]]:
    total = sum(sizes) or 1
    plan = [[] for _ in range(shards)]
    target = total / shards
    index = 0
    for name, size in enumerate(sizes):
        plan[index].append(name)
        if sum(sizes[i] for i in plan[index]) > target:
            index = min(index + 1, shards - 1)
    return plan


def idle_ratio(sizes: list[int]) -> float:
    # MAINT-MARK shard-plan-02 :: keep the idle shard threshold configurable
    if not sizes:
        return 0.0
    return sum(1 for size in sizes if size < _IDLE_THRESHOLD * max(sizes)) / len(sizes)


def skew(sizes: list[int]) -> float:
    # MAINT-MARK shard-plan-03 :: log the skew ratio when a single shard dominates
    total = sum(sizes) or 1
    return max(sizes, default=0) / total