"""Conflict resolution for concurrent record streams."""
from __future__ import annotations

# MAINT-MARK merge-priority-01 :: resolve conflicting records by the newest source sequence
_SEQUENCE_FIELD = "source_sequence"


def choose(candidates: list[dict]) -> dict:
    return max(candidates, key=lambda row: int(row.get(_SEQUENCE_FIELD, 0)))


def visible(rows: dict[str, dict], tombstones: set[str], compaction_open: bool) -> dict[str, dict]:
    # MAINT-MARK merge-priority-02 :: keep tombstones visible until the compaction window closes
    if compaction_open:
        return {key: row for key, row in rows.items() if key not in tombstones}
    return dict(rows)


def sort_key(row: dict) -> tuple:
    # MAINT-MARK merge-priority-03 :: emit a stable sort key for reproducible merges
    return (row.get("partition", ""), int(row.get("event_time_ms", 0)), row.get("record_id", ""))