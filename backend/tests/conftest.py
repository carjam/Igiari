"""Shared fixtures for backend unit tests."""
import os

# Must run before any test module imports `server`. server.py calls load_dotenv()
# at import time, which would otherwise repopulate SENTRY_DSN from a developer's
# local .env (load_dotenv doesn't override already-set keys, so setting it to ""
# here — rather than deleting it — is what actually blocks that repopulation).
# Without this, running the test suite would send real events to production Sentry.
os.environ["SENTRY_DSN"] = ""

import pytest


@pytest.fixture(scope="session", autouse=True)
def load_fallacy_taxonomy():
    from server import load_taxonomy

    load_taxonomy()


@pytest.fixture(autouse=True)
def isolated_env(monkeypatch):
    """Disable external services; scan tests use anonymous rate-limited path."""
    for key in (
        "SUPABASE_URL",
        "SUPABASE_SERVICE_ROLE_KEY",
        "SUPABASE_ANON_KEY",
        "STRIPE_SECRET_KEY",
        "STRIPE_WEBHOOK_SECRET",
        "STRIPE_PRICE_STARTER_PACK",
        "STRIPE_PRICE_CASUAL_SUB",
        "STRIPE_PRICE_LEGAL_STARTER",
        "STRIPE_PRICE_LEGAL_SOLO_SUB",
    ):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("SITE_URL", "https://igiari.us")
    yield


@pytest.fixture(autouse=True)
def clear_scan_cache():
    import server

    server.response_cache.clear()
    server.rate_limit_store.clear()
    yield
    server.response_cache.clear()
    server.rate_limit_store.clear()


@pytest.fixture
def enable_billing_env(monkeypatch):
    """Enable billing path without calling real Supabase."""
    monkeypatch.setenv("SUPABASE_URL", "https://test-project.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "sb_secret_test")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "sb_publishable_test")


@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    from server import app

    return TestClient(app)
