"""Sentry error tracking setup. No-op unless SENTRY_DSN is configured."""
from __future__ import annotations

import os

import sentry_sdk


def init_error_tracking() -> None:
    dsn = os.getenv("SENTRY_DSN")
    if not dsn:
        return
    sentry_sdk.init(
        dsn=dsn,
        environment=os.getenv("SENTRY_ENVIRONMENT", os.getenv("ENVIRONMENT", "production")),
        traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0")),
    )
