"""Tests for Sentry error tracking setup (error_tracking.py)."""
from unittest.mock import Mock

import error_tracking


def test_init_error_tracking_noop_without_dsn(monkeypatch):
    monkeypatch.delenv("SENTRY_DSN", raising=False)
    init_mock = Mock()
    monkeypatch.setattr(error_tracking.sentry_sdk, "init", init_mock)
    error_tracking.init_error_tracking()
    init_mock.assert_not_called()


def test_init_error_tracking_initializes_with_dsn(monkeypatch):
    monkeypatch.setenv("SENTRY_DSN", "https://example@sentry.io/1")
    monkeypatch.setenv("SENTRY_ENVIRONMENT", "staging")
    init_mock = Mock()
    monkeypatch.setattr(error_tracking.sentry_sdk, "init", init_mock)
    error_tracking.init_error_tracking()
    init_mock.assert_called_once()
    _, kwargs = init_mock.call_args
    assert kwargs["dsn"] == "https://example@sentry.io/1"
    assert kwargs["environment"] == "staging"


def test_init_error_tracking_defaults_environment_to_production(monkeypatch):
    monkeypatch.setenv("SENTRY_DSN", "https://example@sentry.io/1")
    monkeypatch.delenv("SENTRY_ENVIRONMENT", raising=False)
    monkeypatch.delenv("ENVIRONMENT", raising=False)
    init_mock = Mock()
    monkeypatch.setattr(error_tracking.sentry_sdk, "init", init_mock)
    error_tracking.init_error_tracking()
    _, kwargs = init_mock.call_args
    assert kwargs["environment"] == "production"
