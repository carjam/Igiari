"""Scan response shape and finding field handling."""
import server
from server import Finding


def test_finding_defaults_what_would_strengthen_this():
    finding = Finding(
        span="test",
        start_index=0,
        end_index=4,
        fallacy="Bandwagon",
        category="Informal",
        subcategory="Appeal to Popularity",
        confidence="high",
        explanation="Treats popularity as proof.",
    )
    assert finding.what_would_strengthen_this == ""


def test_finding_serializes_strengthen_field():
    finding = Finding(
        span="everyone agrees",
        start_index=0,
        end_index=15,
        fallacy="Bandwagon",
        category="Informal",
        subcategory="Appeal to Popularity",
        confidence="medium",
        explanation="Popularity is treated as evidence.",
        what_would_strengthen_this="A cited poll or study would be needed.",
    )
    data = finding.model_dump()
    assert data["what_would_strengthen_this"] == "A cited poll or study would be needed."


def test_scan_returns_what_would_strengthen_this(client, monkeypatch):
    sample = "everyone agrees this policy is correct"

    async def fake_api(_user_text):
        return {
            "findings": [
                {
                    "span": sample,
                    "fallacy": "Bandwagon",
                    "category": "Informal",
                    "subcategory": "Appeal to Popularity",
                    "confidence": "high",
                    "explanation": "Agreement is treated as proof of correctness.",
                    "what_would_strengthen_this": (
                        "This would need independent evidence, not consensus alone."
                    ),
                }
            ]
        }

    monkeypatch.setattr(server, "call_anthropic_api", fake_api)

    response = client.post("/api/scan", json={"text": sample})
    assert response.status_code == 200
    body = response.json()
    assert len(body["findings"]) == 1
    finding = body["findings"][0]
    assert finding["what_would_strengthen_this"] == (
        "This would need independent evidence, not consensus alone."
    )
    assert finding["start_index"] == 0
    assert finding["end_index"] == len(sample)


def test_scan_cache_legacy_findings_default_strengthen(client):
    text = "legacy cached finding without strengthen field"
    server.response_cache[server.hash_text(text)] = {
        "input_length": len(text),
        "findings": [
            {
                "span": text,
                "start_index": 0,
                "end_index": len(text),
                "fallacy": "Bandwagon",
                "category": "Informal",
                "subcategory": "Appeal to Popularity",
                "confidence": "low",
                "explanation": "Example explanation.",
            }
        ],
    }

    response = client.post("/api/scan", json={"text": text})
    assert response.status_code == 200
    assert response.json()["findings"][0]["what_would_strengthen_this"] == ""


def test_scan_drops_findings_with_unlocatable_span(client, monkeypatch):
    async def fake_api(_user_text):
        return {
            "findings": [
                {
                    "span": "this exact phrase is not in the input",
                    "fallacy": "Straw Man",
                    "category": "Informal",
                    "subcategory": "Other Informal Fallacy",
                    "confidence": "high",
                    "explanation": "Should be dropped.",
                    "what_would_strengthen_this": "N/A",
                }
            ]
        }

    monkeypatch.setattr(server, "call_anthropic_api", fake_api)

    response = client.post("/api/scan", json={"text": "completely different input text"})
    assert response.status_code == 200
    assert response.json()["findings"] == []


def test_scan_ignores_bearer_token_when_billing_disabled(client, monkeypatch):
    """Local dev: signed-in browser + backend without Supabase should still scan."""

    async def fake_api(_user_text):
        return {"findings": []}

    monkeypatch.setattr(server, "call_anthropic_api", fake_api)

    response = client.post(
        "/api/scan",
        json={"text": "local dev scan with prod session token"},
        headers={"Authorization": "Bearer fake-token"},
    )
    assert response.status_code == 200
