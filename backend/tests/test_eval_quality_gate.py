"""Phase 5 quality gate — offline regression against frozen baseline."""
import json

import pytest

from eval_grading import (
    EVAL_BASELINE_PATH,
    MIN_F1,
    MIN_PRECISION,
    MIN_RECALL,
    MIN_TN_ACCURACY,
    assert_phase5_quality_gates,
    grade,
    load_baseline_predictions,
    quality_gate_status,
)


def test_baseline_file_exists():
    assert EVAL_BASELINE_PATH.is_file(), (
        f"Missing {EVAL_BASELINE_PATH.name}. Run live eval, then: "
        "python scripts/export_eval_baseline.py"
    )


def test_baseline_covers_full_eval_set():
    baseline = json.loads(EVAL_BASELINE_PATH.read_text(encoding="utf-8"))
    predictions = baseline["predictions"]
    summary, _ = grade(predictions)
    assert len(predictions) == 40
    assert summary["positive_cases"]["f1"] is not None


def test_phase5_quality_gate_on_baseline():
    """CI gate: frozen predictions must meet Phase 5 thresholds."""
    predictions = load_baseline_predictions()
    summary, _ = grade(predictions)
    assert_phase5_quality_gates(summary)


def test_phase5_threshold_constants():
    assert MIN_F1 == 0.75
    assert MIN_PRECISION == 0.65
    assert MIN_RECALL == 0.80
    assert MIN_TN_ACCURACY == 1.0


def test_quality_gate_status_all_pass_on_baseline():
    predictions = load_baseline_predictions()
    summary, _ = grade(predictions)
    status = quality_gate_status(summary)
    assert all(status.values()), f"Regression detected: {status}"


def test_quality_gate_fails_when_degraded():
    predictions = load_baseline_predictions()
    degraded = [
        p if p["id"] != "eval_001" else {"id": p["id"], "predictions": []}
        for p in predictions
    ]
    summary, _ = grade(degraded)
    with pytest.raises(AssertionError, match="Phase 5 quality gate failed"):
        assert_phase5_quality_gates(summary)
