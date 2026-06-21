"""
Stripe Checkout, Billing Portal, and webhook credit grants.
Test mode first — set STRIPE_SECRET_KEY and price IDs from Stripe Dashboard.
"""
import os
from typing import Any, Dict, List, Optional

import stripe
from fastapi import HTTPException

from billing import (
    REQUEST_TIMEOUT,
    get_account,
    get_account_by_stripe_customer,
    grant_credits,
    update_account_fields,
    webhook_event_processed,
)

# Step 1 consumer tiers (spec 10_monetization.md)
PRODUCTS: Dict[str, Dict[str, Any]] = {
    "starter_pack": {
        "price_env": "STRIPE_PRICE_STARTER_PACK",
        "credits": 50,
        "mode": "payment",
        "name": "Starter",
        "description": "50 scans, one-time",
        "amount_display": "$8",
    },
    "casual_sub": {
        "price_env": "STRIPE_PRICE_CASUAL_SUB",
        "credits": 60,
        "mode": "subscription",
        "name": "Casual",
        "description": "60 scans per month",
        "amount_display": "$9/mo",
    },
}


def stripe_enabled() -> bool:
    return bool(os.getenv("STRIPE_SECRET_KEY"))


def _stripe() -> None:
    key = os.getenv("STRIPE_SECRET_KEY")
    if not key:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "STRIPE_UNAVAILABLE",
                "message": "Payments are not configured on this server yet.",
            },
        )
    stripe.api_key = key


def site_url() -> str:
    return os.getenv("SITE_URL", "https://igiari.us").rstrip("/")


def _price_id(product_key: str) -> str:
    product = PRODUCTS.get(product_key)
    if not product:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_PRODUCT",
                "message": "Unknown product.",
            },
        )
    price_id = os.getenv(product["price_env"], "").strip()
    if not price_id:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "STRIPE_UNAVAILABLE",
                "message": f"Product {product_key} is not configured yet.",
            },
        )
    return price_id


def list_public_products() -> List[Dict[str, Any]]:
    if not stripe_enabled():
        return []
    items = []
    for key, product in PRODUCTS.items():
        if os.getenv(product["price_env"], "").strip():
            items.append(
                {
                    "key": key,
                    "name": product["name"],
                    "description": product["description"],
                    "amount_display": product["amount_display"],
                    "credits": product["credits"],
                    "mode": product["mode"],
                }
            )
    return items


def get_or_create_stripe_customer(account: Dict[str, Any]) -> str:
    _stripe()
    existing = account.get("stripe_customer_id")
    if existing:
        return existing

    customer = stripe.Customer.create(
        email=account.get("email") or None,
        metadata={"account_id": account["id"]},
    )
    update_account_fields(account["id"], {"stripe_customer_id": customer.id})
    return customer.id


def create_checkout_session(
    account: Dict[str, Any],
    product_key: str,
) -> str:
    _stripe()
    product = PRODUCTS.get(product_key)
    if not product:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_PRODUCT",
                "message": "Unknown product.",
            },
        )
    price_id = _price_id(product_key)
    customer_id = get_or_create_stripe_customer(account)
    base = site_url()

    params: Dict[str, Any] = {
        "customer": customer_id,
        "mode": product["mode"],
        "line_items": [{"price": price_id, "quantity": 1}],
        "success_url": f"{base}/?checkout=success",
        "cancel_url": f"{base}/?checkout=cancel",
        "metadata": {
            "account_id": account["id"],
            "product_key": product_key,
            "credits": str(product["credits"]),
        },
    }

    if product["mode"] == "subscription":
        params["subscription_data"] = {
            "metadata": {
                "account_id": account["id"],
                "product_key": product_key,
                "credits": str(product["credits"]),
            },
        }

    session = stripe.checkout.Session.create(**params)
    if not session.url:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "STRIPE_ERROR",
                "message": "Could not start checkout. Please try again.",
            },
        )
    return session.url


def create_portal_session(account: Dict[str, Any]) -> str:
    _stripe()
    customer_id = account.get("stripe_customer_id")
    if not customer_id:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "NO_SUBSCRIPTION",
                "message": "No billing history yet. Purchase a plan first.",
            },
        )

    session = stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=site_url(),
    )
    return session.url


def _credits_for_price(price_id: Optional[str]) -> int:
    if not price_id:
        return 0
    for product in PRODUCTS.values():
        env_price = os.getenv(product["price_env"], "").strip()
        if env_price == price_id:
            return int(product["credits"])
    return 0


def _handle_checkout_completed(session: Dict[str, Any], event_id: str) -> None:
    metadata = session.get("metadata") or {}
    account_id = metadata.get("account_id")
    if not account_id:
        print(f"checkout.session.completed missing account_id: {session.get('id')}")
        return

    updates: Dict[str, Any] = {}
    customer_id = session.get("customer")
    if customer_id:
        updates["stripe_customer_id"] = customer_id

    if session.get("mode") == "subscription":
        updates["subscription_status"] = "active"
        update_account_fields(account_id, updates)
        return

    credits = int(metadata.get("credits") or 0)
    if credits <= 0:
        product_key = metadata.get("product_key")
        if product_key and product_key in PRODUCTS:
            credits = int(PRODUCTS[product_key]["credits"])

    if updates:
        update_account_fields(account_id, updates)
    if credits > 0:
        grant_credits(account_id, credits, "pack_purchase", event_id)


def _handle_invoice_paid(invoice: Dict[str, Any], event_id: str) -> None:
    if invoice.get("billing_reason") not in (
        "subscription_create",
        "subscription_cycle",
    ):
        return

    customer_id = invoice.get("customer")
    if not customer_id:
        return

    account = get_account_by_stripe_customer(customer_id)
    if not account:
        print(f"invoice.paid: no account for customer {customer_id}")
        return

    credits = 0
    subscription_id = invoice.get("subscription")
    sub_metadata: Dict[str, Any] = {}

    if subscription_id:
        try:
            _stripe()
            subscription = stripe.Subscription.retrieve(subscription_id)
            sub_metadata = subscription.get("metadata") or {}
        except stripe.error.StripeError as exc:
            print(f"Could not load subscription {subscription_id}: {exc}")

    if sub_metadata.get("credits"):
        credits = int(sub_metadata["credits"])
    else:
        lines = invoice.get("lines", {}).get("data") or []
        if lines:
            price = lines[0].get("price") or {}
            price_id = price.get("id") if isinstance(price, dict) else price
            credits = _credits_for_price(price_id)

    if credits <= 0:
        product_key = sub_metadata.get("product_key")
        if product_key and product_key in PRODUCTS:
            credits = int(PRODUCTS[product_key]["credits"])

    if credits > 0:
        grant_credits(
            account["id"],
            credits,
            "subscription_renewal",
            event_id,
        )

    update_account_fields(account["id"], {"subscription_status": "active"})


def _handle_subscription_deleted(subscription: Dict[str, Any]) -> None:
    customer_id = subscription.get("customer")
    if not customer_id:
        return
    account = get_account_by_stripe_customer(customer_id)
    if account:
        update_account_fields(account["id"], {"subscription_status": "canceled"})


def handle_webhook_payload(payload: bytes, signature: Optional[str]) -> None:
    secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    if not secret:
        raise HTTPException(status_code=503, detail="Webhook not configured")

    _stripe()
    try:
        event = stripe.Webhook.construct_event(payload, signature, secret)
    except stripe.error.SignatureVerificationError as exc:
        print(f"Stripe webhook signature failed: {exc}")
        raise HTTPException(status_code=400, detail="Invalid signature") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid payload") from exc

    event_id = event["id"]
    if webhook_event_processed(event_id):
        print(f"Stripe webhook duplicate ignored: {event_id}")
        return

    event_type = event["type"]
    data = event["data"]["object"]

    if event_type == "checkout.session.completed":
        _handle_checkout_completed(data, event_id)
    elif event_type == "invoice.paid":
        _handle_invoice_paid(data, event_id)
    elif event_type == "customer.subscription.deleted":
        _handle_subscription_deleted(data)
    elif event_type == "invoice.payment_failed":
        customer_id = data.get("customer")
        account = get_account_by_stripe_customer(customer_id) if customer_id else None
        if account:
            update_account_fields(account["id"], {"subscription_status": "canceled"})
    else:
        print(f"Stripe webhook unhandled type: {event_type}")
