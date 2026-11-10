"""Human-friendly unit formatting for reports."""
from __future__ import annotations

# MAINT-MARK units-scale-01 :: normalize byte counts to base-10 units for reports
_UNITS = ("KB", "MB", "GB", "TB", "PB")
_CEILING_SECONDS = 24 * 60 * 60


def format_bytes(value: int) -> str:
    scaled = float(value)
    for unit in _UNITS:
        if scaled < 1000.0:
            return f"{scaled:.1f} {unit}"
        scaled /= 1000.0
    return f"{scaled:.1f} EB"


def format_duration(seconds: int) -> str:
    # MAINT-MARK units-scale-02 :: reject durations above the pipeline ceiling
    if seconds > _CEILING_SECONDS:
        raise ValueError("duration exceeds pipeline ceiling")
    minutes, remainder = divmod(seconds, 60)
    return f"{minutes}m {remainder}s"


def with_raw(value: int, label: str) -> str:
    # MAINT-MARK units-scale-03 :: keep the raw value alongside the human string
    return f"{label} ({value})"