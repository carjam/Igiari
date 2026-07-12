"""Unit tests for eval_grading module."""
import json

import pytest

from eval_grading import (
    MIN_F1,
    MIN_PRECISION,
    MIN_RECALL,
    MIN_TN_ACCURACY,
    assert_phase5_quality_gates,
    compute_format_summary,
    compute_slice_metrics,
    compute_span_fidelity_summary,
    grade,
    load_alias_map,
    normalize,
)


def _write_mini_eval_set(tmp_path, cases: list[dict]) -> "object":
    path = tmp_path / "mini_eval_set.json"
    path.write_text(json.dumps(cases), encoding="utf-8")
    return path


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
    assert len(results) == 80
    assert summary["positive_cases"]["false_negatives"] > 0


def test_slice_metrics_true_positive_by_category_and_subcategory(tmp_path):
    mini_set = _write_mini_eval_set(
        tmp_path,
        [
            {
                "id": "case_1",
                "transcript": "x",
                "ground_truth": [
                    {"fallacy": "Appeal to Probability", "span": "x", "category": "Formal", "subcategory": "Formal Fallacy"}
                ],
            }
        ],
    )
    predictions = [{"id": "case_1", "predictions": [{"fallacy": "Appeal to Probability"}]}]
    slices = compute_slice_metrics(predictions, eval_set_path=mini_set)
    assert slices["by_category"]["Formal"]["true_positives"] == 1
    assert slices["by_subcategory"]["Formal Fallacy"]["true_positives"] == 1


def test_slice_metrics_false_negative_when_missed(tmp_path):
    mini_set = _write_mini_eval_set(
        tmp_path,
        [
            {
                "id": "case_1",
                "transcript": "x",
                "ground_truth": [
                    {"fallacy": "Appeal to Probability", "span": "x", "category": "Formal", "subcategory": "Formal Fallacy"}
                ],
            }
        ],
    )
    slices = compute_slice_metrics([{"id": "case_1", "predictions": []}], eval_set_path=mini_set)
    assert slices["by_category"]["Formal"]["false_negatives"] == 1
    assert slices["by_category"]["Formal"]["recall"] == 0.0


def test_slice_metrics_false_positive_attributed_to_predicted_fallacy(tmp_path):
    mini_set = _write_mini_eval_set(
        tmp_path,
        [
            {
                "id": "case_1",
                "transcript": "x",
                "ground_truth": [
                    {"fallacy": "Straw Man", "span": "x", "category": "Informal", "subcategory": "Other Informal Fallacy"}
                ],
            }
        ],
    )
    predictions = [{"id": "case_1", "predictions": [{"fallacy": "Affirming the Consequent"}]}]
    slices = compute_slice_metrics(predictions, eval_set_path=mini_set)
    # Ground truth (Straw Man) is missed, and the hallucinated "Affirming the
    # Consequent" (Formal/Propositional Fallacy) is a false positive.
    assert slices["by_subcategory"]["Propositional Fallacy"]["false_positives"] == 1
    assert slices["by_subcategory"]["Other Informal Fallacy"]["false_negatives"] == 1


def test_slice_metrics_ignores_true_negative_cases(tmp_path):
    mini_set = _write_mini_eval_set(
        tmp_path,
        [{"id": "case_1", "transcript": "x", "ground_truth": []}],
    )
    slices = compute_slice_metrics([{"id": "case_1", "predictions": []}], eval_set_path=mini_set)
    assert slices["by_category"] == {}
    assert slices["by_subcategory"] == {}


def test_slice_metrics_perfect_precision_when_no_false_positives(tmp_path):
    mini_set = _write_mini_eval_set(
        tmp_path,
        [
            {
                "id": "case_1",
                "transcript": "x",
                "ground_truth": [
                    {"fallacy": "Appeal to Probability", "span": "x", "category": "Formal", "subcategory": "Formal Fallacy"}
                ],
            }
        ],
    )
    predictions = [{"id": "case_1", "predictions": [{"fallacy": "Appeal to Probability"}]}]
    slices = compute_slice_metrics(predictions, eval_set_path=mini_set)
    assert slices["by_category"]["Formal"]["precision"] == 1.0


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
