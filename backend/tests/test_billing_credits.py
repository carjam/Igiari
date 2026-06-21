"""Credit grants and Stripe webhook idempotency."""
from unittest.mock import MagicMock, patch

import pytest

from billing import grant_credits
from stripe_billing import handle_webhook_payload


def test_grant_credits_skips_when_event_already_processed(
    enable_billing_env, monkeypatch
):
    monkeypatch.setattr("billing.webhook_event_processed", lambda event_id: True)
    monkeypatch.setattr(
        "billing.get_account",
        lambda user_id: {"credit_balance": 10},
    )

    def fail_post(*_args, **_kwargs):
        pytest.fail("grant_credits should not write a duplicate transaction")

    monkeypatch.setattr("billing.requests.post", fail_post)

    balance = grant_credits("user-1", 50, "pack_purchase", "evt_duplicate")

    assert balance == 10


def test_grant_credits_applies_on_first_event(enable_billing_env, monkeypatch):
    monkeypatch.setattr("billing.webhook_event_processed", lambda _event_id: False)
    monkeypatch.setattr(
        "billing.get_account",
        lambda user_id: {"credit_balance": 5},
    )
    monkeypatch.setattr("billing.update_account_fields", lambda *_args: None)

    posts = []

    def fake_post(url, **kwargs):
        posts.append((url, kwargs.get("json")))
        response = MagicMock()
        response.status_code = 201
        return response

    monkeypatch.setattr("billing.requests.post", fake_post)

    balance = grant_credits("user-1", 50, "pack_purchase", "evt_new")

    assert balance == 55
    assert len(posts) == 1
    assert posts[0][1]["stripe_event_id"] == "evt_new"
    assert posts[0][1]["delta"] == 50


@patch("stripe_billing._handle_checkout_completed")
@patch("stripe_billing.webhook_event_processed", return_value=True)
@patch("stripe_billing.stripe.Webhook.construct_event")
def test_handle_webhook_payload_skips_duplicate_event(
    mock_construct, _mock_processed, mock_handler, monkeypatch
):
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_test")
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_x")

    mock_construct.return_value = {
        "id": "evt_dup",
        "type": "checkout.session.completed",
        "data": {"object": {"id": "cs_test"}},
    }

    handle_webhook_payload(b"{}", "sig_test")

    mock_handler.assert_not_called()


@patch("stripe_billing._handle_checkout_completed")
@patch("stripe_billing.webhook_event_processed", return_value=False)
@patch("stripe_billing.stripe.Webhook.construct_event")
def test_handle_webhook_payload_processes_new_event(
    mock_construct, _mock_processed, mock_handler, monkeypatch
):
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", "whsec_test")
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_x")

    session = {"id": "cs_test", "metadata": {"account_id": "acct-1"}}
    mock_construct.return_value = {
        "id": "evt_new",
        "type": "checkout.session.completed",
        "data": {"object": session},
    }

    handle_webhook_payload(b"{}", "sig_test")

    mock_handler.assert_called_once_with(session, "evt_new")
