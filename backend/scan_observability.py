"""Structured per-scan telemetry for fallacy detection (Phase 6)."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any

import sentry_sdk

from logging_config import request_id_var


@dataclass
class ApiCallStats:
    """Metrics collected during a single Anthropic API call (across retries)."""

    latency_ms: int = 0
    parse_retries: int = 0
    input_tokens: int = 0
    output_tokens: int = 0


@dataclass
class ScanTelemetry:
    """One completed /api/scan request (cache hit or miss)."""

    input_length: int
    finding_count: int
    spans_dropped: int
    parse_retries: int
    latency_ms: int
    cache_hit: bool
    raw_finding_count: int = 0
    model_latency_ms: int | None = None
    model: str | None = None
    input_tokens: int = 0
    output_tokens: int = 0

    def to_log_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["event"] = "scan_complete"
        request_id = request_id_var.get()
        if request_id:
            payload["request_id"] = request_id
        return payload


def log_scan_complete(telemetry: ScanTelemetry) -> None:
    """Emit one JSON log line per scan for aggregation and alerting."""
    payload = telemetry.to_log_dict()
    print(json.dumps(payload, ensure_ascii=False), flush=True)

    if telemetry.spans_dropped > 0 or telemetry.parse_retries > 0:
        sentry_sdk.capture_message(
            "scan_quality_degraded",
            level="warning",
            extras=payload,
        )
