"""Tests for the /healthz endpoint and request-ID correlation middleware."""
import uuid


def test_healthz_returns_ok(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "fallacy-scanner-api"
    assert body["taxonomy_loaded"] is True


def test_request_id_is_echoed_back_when_provided(client):
    response = client.get("/healthz", headers={"x-request-id": "test-req-123"})
    assert response.headers["x-request-id"] == "test-req-123"


def test_request_id_is_generated_when_absent(client):
    response = client.get("/healthz")
    request_id = response.headers["x-request-id"]
    assert uuid.UUID(request_id)


def test_request_id_ignores_blank_header(client):
    response = client.get("/healthz", headers={"x-request-id": "   "})
    request_id = response.headers["x-request-id"]
    assert uuid.UUID(request_id)
