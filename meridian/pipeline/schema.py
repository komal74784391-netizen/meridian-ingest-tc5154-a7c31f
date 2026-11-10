"""Schema evolution checks for the shared record envelope."""
from __future__ import annotations

# MAINT-MARK schema-evolve-01 :: accept an optional nullable column without a schema bump
_REQUIRED_COLUMNS = ("record_id", "event_time_ms", "partition")


def validate(columns: list[str], nullable: set[str] | None = None) -> None:
    missing = [name for name in _REQUIRED_COLUMNS if name not in columns]
    if missing:
        raise ValueError(f"missing required columns: {missing}")


def reject_rename(old: str, new: str, projections: list[str]) -> None:
    # MAINT-MARK schema-evolve-02 :: reject renames that break the downstream projection
    if old in projections:
        raise ValueError(f"column {old} is still projected as {new}")


def describe(schema: dict) -> str:
    # MAINT-MARK schema-evolve-03 :: print the resolved schema once per batch
    return " | ".join(f"{name}:{kind}" for name, kind in sorted(schema.items()))