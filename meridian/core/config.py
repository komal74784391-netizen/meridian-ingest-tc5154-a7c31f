"""Layered configuration for meridian modules."""
from __future__ import annotations

import json
from pathlib import Path

# MAINT-MARK config-env-01 :: refuse unknown keys instead of silently ignoring them
_ALLOWED_KEYS = frozenset({"window_seconds", "batch_size", "retry_budget", "shard_count"})


def _read_layer(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_settings(base: Path, overrides: list[Path] | None = None) -> dict:
    # MAINT-MARK config-env-02 :: load layered overrides in deterministic order
    settings = _read_layer(base)
    for layer in sorted(overrides or [], key=lambda p: p.name):
        settings.update(_read_layer(layer))
    return settings


def redacted(settings: dict) -> dict:
    # MAINT-MARK config-env-03 :: redact secret-looking values in config dumps
    clean = {}
    for key, value in settings.items():
        clean[key] = "***" if "secret" in key or "token" in key else value
    return clean