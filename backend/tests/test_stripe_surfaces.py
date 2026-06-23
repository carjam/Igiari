"""Legal vs consumer billing surface behavior."""
from unittest.mock import MagicMock, patch

import stripe

from stripe_billing import (
    create_checkout_session,
    create_portal_session,
    list_public_products,
    normalize_surface,
)


def test_normalize_surface_defaults_unknown_to_consumer():
    assert normalize_surface(None) == "consumer"
    assert normalize_surface("") == "consumer"
    assert normalize_surface("LEGAL") == "legal"
    assert normalize_surface("developer") == "consumer"


def test_list_public_products_legal_interim_fallback(monkeypatch):
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_x")
    monkeypatch.setenv("STRIPE_PRICE_STARTER_PACK", "price_starter")
    monkeypatch.setenv("STRIPE_PRICE_CASUAL_SUB", "price_casual")

    result = list_public_products("legal")

    assert result["surface"] == "legal"
    assert result["interim_consumer_pricing"] is True
    assert result["legal_billing_ready"] is False
    assert {p["key"] for p in result["products"]} == {"starter_pack", "casual_sub"}
    assert all(p["surface"] == "consumer" for p in result["products"])


def test_list_public_products_legal_when_configured(monkeypatch):
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_x")
    monkeypatch.setenv("STRIPE_PRICE_LEGAL_STARTER", "price_legal_starter")
    monkeypatch.setenv("STRIPE_PRICE_LEGAL_SOLO_SUB", "price_legal_solo")

    result = list_public_products("legal")

    assert result["interim_consumer_pricing"] is False
    assert result["legal_billing_ready"] is True
    assert {p["key"] for p in result["products"]} == {"legal_starter", "legal_solo_sub"}


@patch("stripe_billing.stripe.checkout.Session.create")
@patch("stripe_billing.get_or_create_stripe_customer", return_value="cus_test")
def test_create_checkout_session_legal_urls(mock_customer, mock_create, monkeypatch):
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_x")
    monkeypatch.setenv("STRIPE_PRICE_LEGAL_STARTER", "price_legal_starter")
    monkeypatch.setenv("SITE_URL", "https://igiari.us")

    mock_create.return_value = MagicMock(url="https://checkout.stripe.test/session")

    create_checkout_session(
        {"id": "acct-1", "email": "solo@example.com"},
        "legal_starter",
        surface="legal",
    )

    params = mock_create.call_args.kwargs
    assert params["success_url"] == "https://igiari.us/legal/?checkout=success"
    assert params["cancel_url"] == "https://igiari.us/legal/?checkout=cancel"
    assert params["metadata"]["surface"] == "legal"


@patch("stripe_billing.get_or_create_stripe_customer", return_value="cus_test")
@patch("stripe_billing.stripe.billing_portal.Session.create")
def test_create_portal_session_legal_return_url(mock_create, mock_customer, monkeypatch):
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_x")
    monkeypatch.setenv("SITE_URL", "https://igiari.us")
    mock_create.return_value = MagicMock(url="https://billing.stripe.test/portal")

    create_portal_session(
        {"id": "acct-1", "stripe_customer_id": "cus_test"},
        surface="legal",
    )

    assert mock_create.call_args.kwargs["return_url"] == "https://igiari.us/legal/"


@patch("stripe_billing.grant_credits")
@patch("stripe_billing.update_account_fields")
def test_checkout_completed_tags_legal_account(mock_update, mock_grant):
    from stripe_billing import _handle_checkout_completed

    _handle_checkout_completed(
        {
            "mode": "payment",
            "customer": "cus_123",
            "metadata": {
                "account_id": "acct-legal",
                "product_key": "legal_starter",
                "credits": "25",
                "surface": "legal",
            },
        },
        "evt_checkout_1",
    )

    mock_update.assert_called()
    updates = mock_update.call_args[0][1]
    assert updates["account_type"] == "legal"
    mock_grant.assert_called_once_with(
        "acct-legal", 25, "pack_purchase", "evt_checkout_1"
    )


@patch("stripe_billing.update_account_fields")
@patch("stripe_billing.stripe.Customer.create")
@patch("stripe_billing.stripe.Customer.retrieve")
def test_get_or_create_stripe_customer_recreates_stale_id(
    mock_retrieve,
    mock_create,
    mock_update,
    monkeypatch,
):
    from stripe_billing import get_or_create_stripe_customer

    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_x")
    mock_retrieve.side_effect = stripe.error.InvalidRequestError(
        "No such customer: 'cus_test_stale'",
        param="id",
    )
    mock_create.return_value = MagicMock(id="cus_live_new")

    customer_id = get_or_create_stripe_customer(
        {
            "id": "acct-1",
            "email": "buyer@example.com",
            "stripe_customer_id": "cus_test_stale",
        }
    )

    assert customer_id == "cus_live_new"
    mock_create.assert_called_once()
    mock_update.assert_called_once_with("acct-1", {"stripe_customer_id": "cus_live_new"})
