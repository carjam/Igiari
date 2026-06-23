"""Tests for raw finding processing."""
from server import process_raw_findings


def test_process_raw_findings_keeps_valid_span():
    text = "everyone agrees this is correct"
    raw = [
        {
            "span": text,
            "fallacy": "Bandwagon",
            "category": "Informal",
            "subcategory": "Appeal to Popularity",
            "confidence": "high",
            "explanation": "Popularity as proof.",
        }
    ]
    findings, dropped = process_raw_findings(text, raw)
    assert len(findings) == 1
    assert dropped == 0
    assert findings[0].fallacy == "Bandwagon"


def test_process_raw_findings_drops_invalid_span():
    raw = [
        {
            "span": "not in transcript",
            "fallacy": "Straw Man",
            "category": "Informal",
            "subcategory": "Other Informal Fallacy",
            "confidence": "high",
            "explanation": "Should drop.",
        }
    ]
    findings, dropped = process_raw_findings("actual input text", raw)
    assert findings == []
    assert dropped == 1
