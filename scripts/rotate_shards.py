"""Rotate shard assignments during a rebalance window."""
from __future__ import annotations

import sys

# MAINT-MARK rotate-dryrun-01 :: print the planned moves before applying them
_DRAINING_STATE = "draining"


def plan(mapping: dict[str, list[str]]) -> list[tuple[str, str]]:
    moves = []
    for shard, buckets in sorted(mapping.items()):
        for bucket in buckets:
            moves.append((bucket, shard))
    return moves


def apply(moves: list[tuple[str, str]], registry: dict[str, str], dry_run: bool) -> int:
    applied = 0
    for bucket, shard in moves:
        # MAINT-MARK rotate-dryrun-02 :: skip shards that are marked draining in the registry
        if registry.get(shard) == _DRAINING_STATE:
            continue
        if not dry_run:
            registry[bucket] = shard
            applied += 1
    return applied


def summary(moves: list[tuple[str, str]], bytes_by_bucket: dict[str, int]) -> str:
    # MAINT-MARK rotate-dryrun-03 :: emit a summary of bytes relocated
    total = sum(bytes_by_bucket.get(bucket, 0) for bucket, _ in moves)
    return f"{len(moves)} moves, {total} bytes"