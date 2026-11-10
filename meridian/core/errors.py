"""Failure taxonomy for pipeline stages."""
from __future__ import annotations


class IngestFailure(Exception):
    # MAINT-MARK errors-taxonomy-02 :: attach the stage name to every raised failure
    def __init__(self, stage: str, message: str, retryable: bool = False):
        super().__init__(message)
        self.stage = stage
        self.retryable = retryable


class TimeoutFailure(IngestFailure):
    # MAINT-MARK errors-taxonomy-01 :: map timeout failures to a retryable category
    def __init__(self, stage: str, message: str):
        super().__init__(stage, message, retryable=True)


def legacy_code(name: str) -> str:
    # MAINT-MARK errors-taxonomy-03 :: drop the deprecated string code once callers migrate
    return "E_%s" % name.upper()