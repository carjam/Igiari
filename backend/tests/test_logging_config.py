"""Tests for structured JSON logging (logging_config.py)."""
import io
import json
import logging

import pytest

from logging_config import JsonFormatter, configure_logging, get_logger, request_id_var


def _logger_with_string_handler(name: str) -> tuple[logging.Logger, io.StringIO]:
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JsonFormatter())
    logger = logging.getLogger(name)
    logger.handlers = [handler]
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    return logger, stream


@pytest.fixture(autouse=True)
def _reset_root_logger():
    root = logging.getLogger()
    original_handlers = list(root.handlers)
    original_level = root.level
    yield
    root.handlers = original_handlers
    root.setLevel(original_level)


def test_json_formatter_basic_fields():
    logger, stream = _logger_with_string_handler("test.basic")
    logger.info("hello world")
    payload = json.loads(stream.getvalue().strip())
    assert payload["level"] == "INFO"
    assert payload["logger"] == "test.basic"
    assert payload["message"] == "hello world"
    assert "request_id" not in payload


def test_json_formatter_includes_request_id_when_set():
    logger, stream = _logger_with_string_handler("test.request_id")
    token = request_id_var.set("req-123")
    try:
        logger.info("scanned")
    finally:
        request_id_var.reset(token)
    payload = json.loads(stream.getvalue().strip())
    assert payload["request_id"] == "req-123"


def test_json_formatter_merges_extra_fields():
    logger, stream = _logger_with_string_handler("test.extra")
    logger.info("scan_complete", extra={"event": "scan_complete", "finding_count": 2})
    payload = json.loads(stream.getvalue().strip())
    assert payload["event"] == "scan_complete"
    assert payload["finding_count"] == 2


def test_json_formatter_includes_exception_info():
    logger, stream = _logger_with_string_handler("test.exc")
    try:
        raise ValueError("boom")
    except ValueError:
        logger.error("failed", exc_info=True)
    payload = json.loads(stream.getvalue().strip())
    assert "ValueError: boom" in payload["exc_info"]


def test_configure_logging_sets_level_from_env(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    configure_logging()
    root = logging.getLogger()
    assert root.level == logging.DEBUG
    assert len(root.handlers) == 1
    assert isinstance(root.handlers[0].formatter, JsonFormatter)


def test_configure_logging_defaults_to_info(monkeypatch):
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    configure_logging()
    assert logging.getLogger().level == logging.INFO


def test_configure_logging_is_idempotent():
    configure_logging()
    configure_logging()
    assert len(logging.getLogger().handlers) == 1


def test_get_logger_returns_named_logger():
    assert get_logger("igiari.server") is logging.getLogger("igiari.server")
