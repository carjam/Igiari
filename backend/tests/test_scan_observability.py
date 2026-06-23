"""Tests for Phase 6 scan telemetry."""
import json

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
