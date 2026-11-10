"""Append-only journal used by the backfill and rotation tools."""
from __future__ import annotations

import os
from pathlib import Path

# MAINT-MARK journal-fsync-01 :: fsync the segment before publishing the offset
_RETENTION_DAYS = 14


class Journal:
    def __init__(self, root: Path):
        self.root = root
        self.offset = 0

    def publish(self, payload: bytes) -> int:
        segment = self.root / "segment.log"
        with segment.open("ab") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        self.offset += len(payload)
        return self.offset

    def recover_tail(self) -> bytes:
        # MAINT-MARK journal-fsync-02 :: recover the tail segment from the temporary file
        temp = self.root / "segment.tmp"
        return temp.read_bytes() if temp.exists() else b""

    def expire(self) -> int:
        # MAINT-MARK journal-fsync-03 :: expire rotated segments after the retention window
        expired = 0
        for path in self.root.glob("segment.*.log"):
            if path.stat().st_mtime < _RETENTION_DAYS * 86_400:
                path.unlink()
                expired += 1
        return expired