"""Scan endpoint behavior when Supabase billing is enabled (production path)."""
import server


def test_scan_requires_sign_in_when_billing_enabled(client, enable_billing_env):
    response = client.post(
        "/api/scan",
        json={"text": "Everyone loves this product so it must be the best."},
    )

    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "NOT_SIGNED_IN"


def test_scan_rejects_zero_credits(client, enable_billing_env, monkeypatch):
    def fake_load_account(_token, account_type_hint=None):
        return {
            "id": "user-zero",
            "email": "zero@example.com",
            "credit_balance": 0,
        }

    monkeypatch.setattr(server, "load_account_from_token", fake_load_account)

    response = client.post(
        "/api/scan",
        headers={"Authorization": "Bearer test-token"},
        json={"text": "Everyone loves this product so it must be the best."},
    )

    assert response.status_code == 402
    assert response.json()["detail"]["code"] == "INSUFFICIENT_CREDIT"


def test_scan_success_debits_credit_and_returns_balance(
    client, enable_billing_env, monkeypatch
):
    async def fake_api(_user_text, stats=None):
        return {"findings": []}

    debited = []

    def fake_load_account(_token, account_type_hint=None):
        return {
            "id": "user-ok",
            "email": "ok@example.com",
            "credit_balance": 3,
        }

    def fake_debit(user_id):
        debited.append(user_id)
        return 2

    monkeypatch.setattr(server, "load_account_from_token", fake_load_account)
    monkeypatch.setattr(server, "debit_scan_credit", fake_debit)
    monkeypatch.setattr(server, "call_anthropic_api", fake_api)

    response = client.post(
        "/api/scan",
        headers={"Authorization": "Bearer test-token"},
        json={"text": "Everyone loves this product so it must be the best."},
    )

    assert response.status_code == 200
    assert response.json()["credits_remaining"] == 2
    assert debited == ["user-ok"]
