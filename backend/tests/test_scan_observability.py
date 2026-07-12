"""Tests for Phase 6 scan telemetry."""
import json
from unittest.mock import Mock

import scan_observability
from logging_config import request_id_var
from scan_observability import ScanTelemetry, log_scan_complete


def test_scan_telemetry_to_log_dict():
    telemetry = ScanTelemetry(
        input_length=120,
        finding_count=2,
        spans_dropped=1,
        parse_retries=0,
        latency_ms=842,
        cache_hit=False,
        raw_finding_count=3,
        model_latency_ms=790,
    )
    payload = telemetry.to_log_dict()
    assert payload["event"] == "scan_complete"
    assert payload["finding_count"] == 2
    assert payload["spans_dropped"] == 1
    assert payload["model_latency_ms"] == 790
    assert "request_id" not in payload


def test_scan_telemetry_to_log_dict_includes_request_id():
    token = request_id_var.set("req-abc")
    try:
        telemetry = ScanTelemetry(
            input_length=10,
            finding_count=0,
            spans_dropped=0,
            parse_retries=0,
            latency_ms=5,
            cache_hit=True,
        )
        payload = telemetry.to_log_dict()
    finally:
        request_id_var.reset(token)
    assert payload["request_id"] == "req-abc"


def test_log_scan_complete_emits_json_line(capsys):
    log_scan_complete(
        ScanTelemetry(
            input_length=50,
            finding_count=0,
            spans_dropped=0,
            parse_retries=0,
            latency_ms=12,
            cache_hit=True,
        )
    )
    line = capsys.readouterr().out.strip()
    payload = json.loads(line)
    assert payload["event"] == "scan_complete"
    assert payload["cache_hit"] is True


def test_log_scan_complete_does_not_alert_on_clean_scan(capsys, monkeypatch):
    capture_mock = Mock()
    monkeypatch.setattr(scan_observability.sentry_sdk, "capture_message", capture_mock)
    log_scan_complete(
        ScanTelemetry(
            input_length=50,
            finding_count=1,
            spans_dropped=0,
            parse_retries=0,
            latency_ms=12,
            cache_hit=False,
        )
    )
    capsys.readouterr()
    capture_mock.assert_not_called()


def test_log_scan_complete_alerts_on_dropped_spans(capsys, monkeypatch):
    capture_mock = Mock()
    monkeypatch.setattr(scan_observability.sentry_sdk, "capture_message", capture_mock)
    log_scan_complete(
        ScanTelemetry(
            input_length=50,
            finding_count=1,
            spans_dropped=1,
            parse_retries=0,
            latency_ms=12,
            cache_hit=False,
        )
    )
    capsys.readouterr()
    capture_mock.assert_called_once()
    args, kwargs = capture_mock.call_args
    assert args[0] == "scan_quality_degraded"
    assert kwargs["level"] == "warning"
    assert kwargs["extras"]["spans_dropped"] == 1


def test_log_scan_complete_alerts_on_parse_retries(capsys, monkeypatch):
    capture_mock = Mock()
    monkeypatch.setattr(scan_observability.sentry_sdk, "capture_message", capture_mock)
    log_scan_complete(
        ScanTelemetry(
            input_length=50,
            finding_count=1,
            spans_dropped=0,
            parse_retries=1,
            latency_ms=12,
            cache_hit=False,
        )
    )
    capsys.readouterr()
    capture_mock.assert_called_once()
