"""
Supabase-backed accounts and credit ledger for authenticated scans.
"""
import os
from typing import Any, Dict, Optional

from fastapi import HTTPException

TRIAL_CREDITS = 20


def billing_enabled() -> bool:
    return bool(os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_SERVICE_ROLE_KEY"))


def get_supabase():
    from supabase import create_client

    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    return create_client(url, key)


def verify_access_token(token: str) -> Dict[str, Any]:
    if not billing_enabled():
        raise HTTPException(
            status_code=503,
            detail={
                "code": "BILLING_UNAVAILABLE",
                "message": "Account billing is not configured on this server.",
            },
        )

    try:
        client = get_supabase()
        response = client.auth.get_user(token)
        user = response.user
    except Exception as exc:
        print(f"Auth verification failed: {exc}")
        raise HTTPException(
            status_code=401,
            detail={
                "code": "INVALID_SESSION",
                "message": "Your sign-in session is invalid or expired. Please sign in again.",
            },
        ) from exc

    if not user or not user.id:
        raise HTTPException(
            status_code=401,
            detail={
                "code": "INVALID_SESSION",
                "message": "Your sign-in session is invalid or expired. Please sign in again.",
            },
        )

    email = user.email or ""
    return {"id": user.id, "email": email}


def get_account(user_id: str) -> Optional[Dict[str, Any]]:
    client = get_supabase()
    result = (
        client.table("accounts")
        .select("*")
        .eq("id", user_id)
        .maybe_single()
        .execute()
    )
    return result.data


def grant_trial_credits(user_id: str) -> None:
    account = get_account(user_id)
    if not account or account.get("free_trial_granted"):
        return

    new_balance = account["credit_balance"] + TRIAL_CREDITS
    client = get_supabase()
    client.table("credit_transactions").insert(
        {
            "account_id": user_id,
            "delta": TRIAL_CREDITS,
            "reason": "trial_grant",
        }
    ).execute()
    client.table("accounts").update(
        {
            "credit_balance": new_balance,
            "free_trial_granted": True,
        }
    ).eq("id", user_id).eq("free_trial_granted", False).execute()


def ensure_account(user_id: str, email: str) -> Dict[str, Any]:
    account = get_account(user_id)
    if account is None:
        client = get_supabase()
        client.table("accounts").insert(
            {
                "id": user_id,
                "email": email,
                "account_type": "consumer",
            }
        ).execute()
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
    client = get_supabase()
    client.table("credit_transactions").insert(
        {
            "account_id": user_id,
            "delta": -1,
            "reason": "scan_usage",
        }
    ).execute()
    client.table("accounts").update({"credit_balance": new_balance}).eq(
        "id", user_id
    ).execute()
    return new_balance
