"""
Stripe Checkout, Billing Portal, and webhook credit grants.
Supports consumer and legal product surfaces (spec 10_monetization.md).
"""
import os
from typing import Any, Dict, List, Optional

import sentry_sdk
import stripe
from fastapi import HTTPException

from billing import (
    get_account,
    get_account_by_stripe_customer,
    grant_credits,
    update_account_fields,
    webhook_event_processed,
)
from logging_config import get_logger

logger = get_logger(__name__)

CONSUMER_PRODUCTS: Dict[str, Dict[str, Any]] = {
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

# Step 2 legal tier — enable by setting STRIPE_PRICE_LEGAL_* on Render (sandbox or live).
LEGAL_PRODUCTS: Dict[str, Dict[str, Any]] = {
    "legal_starter": {
        "price_env": "STRIPE_PRICE_LEGAL_STARTER",
        "credits": 25,
        "mode": "payment",
        "name": "Legal Starter",
        "description": "25 scans, one-time",
        "amount_display": "$29",
    },
    "legal_solo_sub": {
        "price_env": "STRIPE_PRICE_LEGAL_SOLO_SUB",
        "credits": 50,
        "mode": "subscription",
        "name": "Legal Solo",
        "description": "50 scans per month",
        "amount_display": "$39/mo",
    },
}

SURFACES: Dict[str, Dict[str, Dict[str, Any]]] = {
    "consumer": CONSUMER_PRODUCTS,
    "legal": LEGAL_PRODUCTS,
}

VALID_SURFACES = frozenset(SURFACES.keys())


def normalize_surface(surface: Optional[str]) -> str:
    value = (surface or "consumer").strip().lower()
    if value not in VALID_SURFACES:
        return "consumer"
    return value


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
    stripe.max_network_retries = 1


def _stripe_http_error(exc: stripe.error.StripeError) -> HTTPException:
    user_message = getattr(exc, "user_message", None) or str(exc)
    logger.error("Stripe API error [%s]: %s", exc.__class__.__name__, user_message)
    sentry_sdk.capture_exception(exc)
    return HTTPException(
        status_code=502,
        detail={
            "code": "STRIPE_ERROR",
            "message": "Could not connect to the payment provider. Please try again.",
        },
    )


def _stripe_customer_not_found(exc: stripe.error.StripeError) -> bool:
    """True only when Stripe confirms the stored customer ID does not exist."""
    if not isinstance(exc, stripe.error.InvalidRequestError):
        return False
    if getattr(exc, "code", None) == "resource_missing":
        return True
    if getattr(exc, "param", None) == "id":
        return True
    return "no such customer" in str(exc).lower()


def site_url() -> str:
    return os.getenv("SITE_URL", "https://igiari.us").rstrip("/")


def _catalog(surface: str) -> Dict[str, Dict[str, Any]]:
    return SURFACES[normalize_surface(surface)]


def _all_products() -> Dict[str, Dict[str, Any]]:
    merged: Dict[str, Dict[str, Any]] = {}
    for catalog in SURFACES.values():
        merged.update(catalog)
    return merged


def _price_id(product_key: str, surface: str) -> str:
    catalog = _catalog(surface)
    product = catalog.get(product_key)
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


def _products_for_surface(surface: str) -> List[Dict[str, Any]]:
    if not stripe_enabled():
        return []
    normalized = normalize_surface(surface)
    items: List[Dict[str, Any]] = []
    for key, product in _catalog(normalized).items():
        if os.getenv(product["price_env"], "").strip():
            items.append(
                {
                    "key": key,
                    "name": product["name"],
                    "description": product["description"],
                    "amount_display": product["amount_display"],
                    "credits": product["credits"],
                    "mode": product["mode"],
                    "surface": normalized,
                }
            )
    return items


def list_public_products(surface: str = "consumer") -> Dict[str, Any]:
    normalized = normalize_surface(surface)
    products = _products_for_surface(normalized)
    interim_consumer_pricing = False

    if normalized == "legal" and not products:
        products = _products_for_surface("consumer")
        for item in products:
            item["surface"] = "consumer"
        interim_consumer_pricing = True

    return {
        "surface": normalized,
        "products": products,
        "interim_consumer_pricing": interim_consumer_pricing,
        "legal_billing_ready": bool(_products_for_surface("legal")),
    }


def get_or_create_stripe_customer(account: Dict[str, Any]) -> str:
    _stripe()
    account_id = account["id"]
    existing = account.get("stripe_customer_id")
    if existing:
        try:
            stripe.Customer.retrieve(existing)
            return existing
        except stripe.error.StripeError as exc:
            if not _stripe_customer_not_found(exc):
                raise _stripe_http_error(exc) from exc
            logger.warning(
                "Replacing missing Stripe customer %s for account %s: %s",
                existing,
                account_id,
                exc,
            )

    try:
        customer = stripe.Customer.create(
            email=account.get("email") or None,
            metadata={"account_id": account_id},
        )
    except stripe.error.StripeError as exc:
        raise _stripe_http_error(exc) from exc
    update_account_fields(account_id, {"stripe_customer_id": customer.id})
    return customer.id


def create_checkout_session(
    account: Dict[str, Any],
    product_key: str,
    surface: str = "consumer",
) -> str:
    _stripe()
    normalized = normalize_surface(surface)
    catalog = _catalog(normalized)
    product = catalog.get(product_key)

    if not product and normalized == "legal":
        catalog = _catalog("consumer")
        product = catalog.get(product_key)
        normalized = "consumer"

    if not product:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_PRODUCT",
                "message": "Unknown product.",
            },
        )

    price_id = _price_id(product_key, normalized)
    customer_id = get_or_create_stripe_customer(account)
    base = site_url()

    if normalized == "legal":
        success_url = f"{base}/legal/?checkout=success"
        cancel_url = f"{base}/legal/?checkout=cancel"
    else:
        success_url = f"{base}/?checkout=success"
        cancel_url = f"{base}/?checkout=cancel"

    params: Dict[str, Any] = {
        "customer": customer_id,
        "mode": product["mode"],
        "line_items": [{"price": price_id, "quantity": 1}],
        "success_url": success_url,
        "cancel_url": cancel_url,
        "metadata": {
            "account_id": account["id"],
            "product_key": product_key,
            "credits": str(product["credits"]),
            "surface": normalized,
        },
    }

    if product["mode"] == "subscription":
        params["subscription_data"] = {
            "metadata": {
                "account_id": account["id"],
                "product_key": product_key,
                "credits": str(product["credits"]),
                "surface": normalized,
            },
        }

    try:
        session = stripe.checkout.Session.create(**params)
    except stripe.error.StripeError as exc:
        raise _stripe_http_error(exc) from exc
    if not session.url:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "STRIPE_ERROR",
                "message": "Could not start checkout. Please try again.",
            },
        )
    return session.url


def create_portal_session(account: Dict[str, Any], surface: str = "consumer") -> str:
    _stripe()
    has_billing = bool(account.get("stripe_customer_id")) or (
        account.get("subscription_status") == "active"
    )
    if not has_billing:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "NO_SUBSCRIPTION",
                "message": "No billing history yet. Purchase a plan first.",
            },
        )

    customer_id = get_or_create_stripe_customer(account)
    return_url = site_url()
    if normalize_surface(surface) == "legal":
        return_url = f"{return_url}/legal/"

    try:
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url,
        )
    except stripe.error.StripeError as exc:
        raise _stripe_http_error(exc) from exc
    return session.url


def _credits_for_price(price_id: Optional[str]) -> int:
    if not price_id:
        return 0
    for product in _all_products().values():
        env_price = os.getenv(product["price_env"], "").strip()
        if env_price == price_id:
            return int(product["credits"])
    return 0


def _credits_for_product_key(product_key: Optional[str]) -> int:
    if not product_key:
        return 0
    product = _all_products().get(product_key)
    return int(product["credits"]) if product else 0


def _handle_checkout_completed(session: Dict[str, Any], event_id: str) -> None:
    metadata = session.get("metadata") or {}
    account_id = metadata.get("account_id")
    if not account_id:
        logger.error(
            "checkout.session.completed missing account_id: %s", session.get("id")
        )
        return

    updates: Dict[str, Any] = {}
    customer_id = session.get("customer")
    if customer_id:
        updates["stripe_customer_id"] = customer_id

    surface = metadata.get("surface")
    if surface == "legal":
        updates["account_type"] = "legal"

    if session.get("mode") == "subscription":
        updates["subscription_status"] = "active"
        update_account_fields(account_id, updates)
        return

    credits = int(metadata.get("credits") or 0)
    if credits <= 0:
        credits = _credits_for_product_key(metadata.get("product_key"))

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
        logger.error("invoice.paid: no account for customer %s", customer_id)
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
            logger.warning("Could not load subscription %s: %s", subscription_id, exc)

    if sub_metadata.get("surface") == "legal":
        update_account_fields(account["id"], {"account_type": "legal"})

    if sub_metadata.get("credits"):
        credits = int(sub_metadata["credits"])
    else:
        lines = invoice.get("lines", {}).get("data") or []
        if lines:
            price = lines[0].get("price") or {}
            price_id = price.get("id") if isinstance(price, dict) else price
            credits = _credits_for_price(price_id)

    if credits <= 0:
        credits = _credits_for_product_key(sub_metadata.get("product_key"))

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
        logger.warning("Stripe webhook signature failed: %s", exc)
        raise HTTPException(status_code=400, detail="Invalid signature") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid payload") from exc

    event_id = event["id"]
    if webhook_event_processed(event_id):
        logger.info("Stripe webhook duplicate ignored: %s", event_id)
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
        logger.info("Stripe webhook unhandled type: %s", event_type)
