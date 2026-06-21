"""
Supabase-backed accounts and credit ledger for authenticated scans.
Uses Supabase REST directly (requests) for reliability on Render.
"""
import os
from typing import Any, Dict, Optional

import requests
from fastapi import HTTPException

TRIAL_CREDITS = 20
REQUEST_TIMEOUT = 10


def _supabase_url() -> str:
    return os.environ["SUPABASE_URL"].rstrip("/")


def billing_enabled() -> bool:
    return bool(
        os.getenv("SUPABASE_URL")
        and os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        and _publishable_key()
    )


def _publishable_key() -> str:
    return (
        os.getenv("SUPABASE_ANON_KEY")
        or os.getenv("SUPABASE_PUBLISHABLE_KEY")
        or ""
    )


def _secret_key() -> str:
    return (
        os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        or os.getenv("SUPABASE_SECRET_KEY")
        or ""
    )


def _service_headers(*, prefer: str = "return=representation") -> Dict[str, str]:
    key = _secret_key()
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": prefer,
    }


def verify_access_token(token: str) -> Dict[str, Any]:
    if not billing_enabled():
        raise HTTPException(
            status_code=503,
            detail={
                "code": "BILLING_UNAVAILABLE",
                "message": "Account billing is not configured on this server.",
            },
        )

    publishable = _publishable_key()
    if not publishable:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "BILLING_UNAVAILABLE",
                "message": "Server missing Supabase publishable key configuration.",
            },
        )

    try:
        response = requests.get(
            f"{_supabase_url()}/auth/v1/user",
            headers={
                "apikey": publishable,
                "Authorization": f"Bearer {token}",
            },
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException as exc:
        print(f"Auth verification request failed: {exc}")
        raise HTTPException(
            status_code=503,
            detail={
                "code": "AUTH_UNAVAILABLE",
                "message": "Could not verify sign-in. Please try again.",
            },
        ) from exc

    if response.status_code != 200:
        print(f"Auth verification failed: {response.status_code} {response.text}")
        raise HTTPException(
            status_code=401,
            detail={
                "code": "INVALID_SESSION",
                "message": "Your sign-in session is invalid or expired. Please sign in again.",
            },
        )

    user = response.json()
    user_id = user.get("id")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail={
                "code": "INVALID_SESSION",
                "message": "Your sign-in session is invalid or expired. Please sign in again.",
            },
        )

    return {"id": user_id, "email": user.get("email") or ""}


def get_account(user_id: str) -> Optional[Dict[str, Any]]:
    response = requests.get(
        f"{_supabase_url()}/rest/v1/accounts",
        params={"id": f"eq.{user_id}", "select": "*"},
        headers=_service_headers(),
        timeout=REQUEST_TIMEOUT,
    )
    if response.status_code != 200:
        print(f"get_account failed: {response.status_code} {response.text}")
        message = "Could not load your account. Please try again."
        try:
            body = response.json()
            if body.get("code") == "42501" or "permission denied" in (body.get("message") or "").lower():
                message = (
                    "Billing tables are not exposed to the Supabase API yet. "
                    "Run grant_billing_api_access.sql in the Supabase SQL Editor."
                )
        except ValueError:
            pass
        raise HTTPException(
            status_code=503,
            detail={
                "code": "ACCOUNT_ERROR",
                "message": message,
            },
        )

    rows = response.json()
    return rows[0] if rows else None


def grant_trial_credits(user_id: str) -> None:
    account = get_account(user_id)
    if not account or account.get("free_trial_granted"):
        return

    new_balance = account["credit_balance"] + TRIAL_CREDITS

    txn = requests.post(
        f"{_supabase_url()}/rest/v1/credit_transactions",
        headers=_service_headers(),
        json={
            "account_id": user_id,
            "delta": TRIAL_CREDITS,
            "reason": "trial_grant",
        },
        timeout=REQUEST_TIMEOUT,
    )
    if txn.status_code not in (200, 201):
        print(f"trial grant txn failed: {txn.status_code} {txn.text}")
        raise HTTPException(
            status_code=503,
            detail={
                "code": "ACCOUNT_ERROR",
                "message": "Could not grant trial credits. Please try again.",
            },
        )

    updated = requests.patch(
        f"{_supabase_url()}/rest/v1/accounts",
        params={"id": f"eq.{user_id}", "free_trial_granted": "eq.false"},
        headers=_service_headers(),
        json={
            "credit_balance": new_balance,
            "free_trial_granted": True,
        },
        timeout=REQUEST_TIMEOUT,
    )
    if updated.status_code != 200:
        print(f"trial grant update failed: {updated.status_code} {updated.text}")


def ensure_account(user_id: str, email: str) -> Dict[str, Any]:
    account = get_account(user_id)
    if account is None:
        created = requests.post(
            f"{_supabase_url()}/rest/v1/accounts",
            headers=_service_headers(),
            json={
                "id": user_id,
                "email": email,
                "account_type": "consumer",
            },
            timeout=REQUEST_TIMEOUT,
        )
        if created.status_code not in (200, 201):
            print(f"create account failed: {created.status_code} {created.text}")
            raise HTTPException(
                status_code=503,
                detail={
                    "code": "ACCOUNT_ERROR",
                    "message": "Could not create your account. Please try again.",
                },
            )
        grant_trial_credits(user_id)
        account = get_account(user_id)

    if account and not account.get("free_trial_granted"):
        grant_trial_credits(user_id)
        account = get_account(user_id)

    if not account:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "ACCOUNT_ERROR",
                "message": "Could not load your account. Please try again.",
            },
        )

    return account


def load_account_from_token(token: str) -> Dict[str, Any]:
    user = verify_access_token(token)
    return ensure_account(user["id"], user["email"])


def require_credits(account: Dict[str, Any]) -> None:
    if account.get("credit_balance", 0) <= 0:
        raise HTTPException(
            status_code=402,
            detail={
                "code": "INSUFFICIENT_CREDIT",
                "message": "You have no scans left. Purchase credits to continue (coming soon).",
            },
        )


def debit_scan_credit(user_id: str) -> int:
    account = get_account(user_id)
    if not account or account.get("credit_balance", 0) <= 0:
        raise HTTPException(
            status_code=402,
            detail={
                "code": "INSUFFICIENT_CREDIT",
                "message": "You have no scans left. Purchase credits to continue (coming soon).",
            },
        )

    new_balance = account["credit_balance"] - 1

    txn = requests.post(
        f"{_supabase_url()}/rest/v1/credit_transactions",
        headers=_service_headers(),
        json={
            "account_id": user_id,
            "delta": -1,
            "reason": "scan_usage",
        },
        timeout=REQUEST_TIMEOUT,
    )
    if txn.status_code not in (200, 201):
        print(f"debit txn failed: {txn.status_code} {txn.text}")
        raise HTTPException(
            status_code=503,
            detail={
                "code": "ACCOUNT_ERROR",
                "message": "Could not update your balance. Please try again.",
            },
        )

    updated = requests.patch(
        f"{_supabase_url()}/rest/v1/accounts",
        params={"id": f"eq.{user_id}"},
        headers=_service_headers(),
        json={"credit_balance": new_balance},
        timeout=REQUEST_TIMEOUT,
    )
    if updated.status_code != 200:
        print(f"debit update failed: {updated.status_code} {updated.text}")

    return new_balance
