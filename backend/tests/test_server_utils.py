"""Server utility and scan validation tests."""
import time

import pytest

import server
from server import check_rate_limit, find_span_indices, hash_text


def test_hash_text_normalizes_whitespace_and_case():
    assert hash_text("  Hello World  ") == hash_text("hello world")


def test_find_span_indices_found():
    text = "alpha beta gamma"
    assert find_span_indices(text, "beta") == (6, 10)


def test_find_span_indices_not_found():
    assert find_span_indices("alpha beta", "missing") is None


def test_check_rate_limit_allows_under_cap(monkeypatch):
    monkeypatch.setattr(server, "RATE_LIMIT_DISABLED", False)
    monkeypatch.setattr(server, "RATE_LIMIT_REQUESTS", 3)
    server.rate_limit_store.clear()
    assert check_rate_limit("1.2.3.4") is True
    assert check_rate_limit("1.2.3.4") is True


def test_check_rate_limit_blocks_at_cap(monkeypatch):
    monkeypatch.setattr(server, "RATE_LIMIT_DISABLED", False)
    monkeypatch.setattr(server, "RATE_LIMIT_REQUESTS", 2)
    server.rate_limit_store.clear()
    assert check_rate_limit("9.9.9.9") is True
    assert check_rate_limit("9.9.9.9") is True
    assert check_rate_limit("9.9.9.9") is False


def test_check_rate_limit_disabled(monkeypatch):
    monkeypatch.setattr(server, "RATE_LIMIT_DISABLED", True)
    server.rate_limit_store.clear()
    for _ in range(20):
        assert check_rate_limit("127.0.0.1") is True


def test_check_rate_limit_expires_old_entries(monkeypatch):
    monkeypatch.setattr(server, "RATE_LIMIT_DISABLED", False)
    monkeypatch.setattr(server, "RATE_LIMIT_REQUESTS", 1)
    monkeypatch.setattr(server, "RATE_LIMIT_WINDOW", 60)
    server.rate_limit_store.clear()
    old = time.time() - 120
    server.rate_limit_store["client"] = [old]
    assert check_rate_limit("client") is True


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200


def test_scan_rejects_empty_text(client):
    response = client.post("/api/scan", json={"text": "   "})
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "EMPTY_TEXT"


def test_scan_rejects_text_too_long(client):
    response = client.post("/api/scan", json={"text": "x" * (server.MAX_INPUT_LENGTH + 1)})
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "TEXT_TOO_LONG"


def test_scan_rate_limited_when_billing_disabled(client, monkeypatch):
    monkeypatch.setattr(server, "RATE_LIMIT_DISABLED", False)
    monkeypatch.setattr(server, "RATE_LIMIT_REQUESTS", 1)
    server.rate_limit_store.clear()

    async def fake_api(_user_text, stats=None):
        return {"findings": []}

    monkeypatch.setattr(server, "call_anthropic_api", fake_api)

    first = client.post("/api/scan", json={"text": "first scan"})
    second = client.post("/api/scan", json={"text": "second scan"})
    assert first.status_code == 200
    assert second.status_code == 429
    assert second.json()["detail"]["code"] == "RATE_LIMITED"


def test_scan_requires_sign_in_when_billing_enabled(client, enable_billing_env, monkeypatch):
    monkeypatch.setattr(server, "billing_enabled", lambda: True)

    response = client.post("/api/scan", json={"text": "needs auth"})
    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "NOT_SIGNED_IN"
