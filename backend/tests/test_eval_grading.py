"""Unit tests for eval_grading module."""
import pytest

from eval_grading import (
    MIN_F1,
    MIN_PRECISION,
    MIN_RECALL,
    MIN_TN_ACCURACY,
    assert_phase5_quality_gates,
    compute_format_summary,
    compute_span_fidelity_summary,
    grade,
    load_alias_map,
    normalize,
)


def test_normalize_uses_alias_map():
    alias_map = load_alias_map()
    assert normalize("Bandwagon Argument", alias_map) == "Argumentum ad Populum"


def test_grade_perfect_positive_case():
    predictions = [{"id": "eval_002", "predictions": [{"fallacy": "Straw Man"}]}]
    summary, results = grade(predictions)
    assert summary["positive_cases"]["true_positives"] == 1
    assert summary["positive_cases"]["false_positives"] == 0
    row = next(r for r in results if r["id"] == "eval_002")
    assert row["matched"] == ["Straw Man"]


def test_grade_counts_false_positive():
    predictions = [
        {
            "id": "eval_002",
            "predictions": [
                {"fallacy": "Straw Man"},
                {"fallacy": "False Dilemma"},
            ],
        }
    ]
    summary, results = grade(predictions)
    assert summary["positive_cases"]["true_positives"] == 1
    assert summary["positive_cases"]["false_positives"] == 1
    row = next(r for r in results if r["id"] == "eval_002")
    assert row["extra_unjustified"] == ["False Dilemma"]


def test_grade_true_negative_empty():
    predictions = [{"id": "eval_009", "predictions": []}]
    summary, results = grade(predictions)
    assert summary["true_negative_cases"]["correctly_flagged_clean"] >= 1
    tn = next(r for r in results if r["id"] == "eval_009")
    assert tn["correct"] is True


def test_grade_true_negative_false_alarm():
    predictions = [{"id": "eval_009", "predictions": [{"fallacy": "Straw Man"}]}]
    summary, results = grade(predictions)
    tn = next(r for r in results if r["id"] == "eval_009")
    assert tn["correct"] is False


def test_compute_format_summary():
    summary = compute_format_summary({"total": 40, "json_ok": 38, "format_errors": 2})
    assert summary["format_compliance_rate"] == 0.95


def test_compute_format_summary_empty():
    summary = compute_format_summary({"total": 0, "json_ok": 0, "format_errors": 0})
    assert summary["format_compliance_rate"] is None


def test_compute_span_fidelity_summary():
    summary = compute_span_fidelity_summary(
        {"findings_returned": 10, "spans_in_transcript": 10, "spans_not_in_transcript": 0}
    )
    assert summary["span_fidelity_rate"] == 1.0


def test_compute_span_fidelity_summary_empty():
    summary = compute_span_fidelity_summary(
        {"findings_returned": 0, "spans_in_transcript": 0, "spans_not_in_transcript": 0}
    )
    assert summary["span_fidelity_rate"] is None


def test_grade_missing_case_treated_as_empty_prediction():
    summary, results = grade([])
    assert len(results) == 40
    assert summary["positive_cases"]["false_negatives"] > 0


def test_assert_phase5_reports_each_failed_metric():
    failing = {
        "positive_cases": {"f1": MIN_F1 - 0.1, "precision": MIN_PRECISION - 0.1, "recall": MIN_RECALL - 0.1},
        "true_negative_cases": {"accuracy": MIN_TN_ACCURACY - 0.1},
    }
    with pytest.raises(AssertionError, match="F1"):
        assert_phase5_quality_gates(failing)

    with pytest.raises(AssertionError, match="precision"):
        assert_phase5_quality_gates(
            {
                "positive_cases": {"f1": MIN_F1, "precision": MIN_PRECISION - 0.01, "recall": MIN_RECALL},
                "true_negative_cases": {"accuracy": MIN_TN_ACCURACY},
            }
        )

    with pytest.raises(AssertionError, match="recall"):
        assert_phase5_quality_gates(
            {
                "positive_cases": {"f1": MIN_F1, "precision": MIN_PRECISION, "recall": MIN_RECALL - 0.01},
                "true_negative_cases": {"accuracy": MIN_TN_ACCURACY},
            }
        )

    with pytest.raises(AssertionError, match="true-negative"):
        assert_phase5_quality_gates(
            {
                "positive_cases": {"f1": MIN_F1, "precision": MIN_PRECISION, "recall": MIN_RECALL},
                "true_negative_cases": {"accuracy": MIN_TN_ACCURACY - 0.01},
            }
        )
