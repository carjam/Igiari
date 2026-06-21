"""Billing configuration invariants."""
from billing import TRIAL_CREDITS


def test_trial_credits_is_five():
    assert TRIAL_CREDITS == 5
