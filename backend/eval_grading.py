"""Offline eval grading and Phase 5 quality gates (no API calls)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

BACKEND_ROOT = Path(__file__).resolve().parent
EVAL_SET_PATH = BACKEND_ROOT / "fallacy_reference" / "eval_set.json"
TAXONOMY_PATH = BACKEND_ROOT / "fallacy_reference" / "fallacies.json"
EVAL_BASELINE_PATH = BACKEND_ROOT / "fallacy_reference" / "eval_baseline_predictions.json"

# Phase 5 regression gates — enforced in CI via tests/test_eval_quality_gate.py
MIN_F1 = 0.75
MIN_PRECISION = 0.65
MIN_RECALL = 0.80
MIN_TN_ACCURACY = 1.0


def load_alias_map() -> dict[str, str]:
    """Build a lowercase name/alias -> canonical name map for fuzzy matching."""
    with open(TAXONOMY_PATH, encoding="utf-8") as f:
        taxonomy = json.load(f)
    alias_map: dict[str, str] = {}
    for entry in taxonomy:
        canonical = entry["name"]
        alias_map[canonical.lower()] = canonical
        for alias in entry.get("aliases", []):
            alias_map[alias.lower()] = canonical
    return alias_map


def normalize(name: str, alias_map: dict[str, str]) -> str:
    """Normalize fallacy name using alias map."""
    return alias_map.get(name.strip().lower(), name.strip())


def grade(
    predictions: list[dict[str, Any]],
    eval_set_path: Path | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Grade predictions against ground truth."""
    path = eval_set_path or EVAL_SET_PATH
    with open(path, encoding="utf-8") as f:
        eval_set = {case["id"]: case for case in json.load(f)}

    predictions_dict = {p["id"]: p for p in predictions}
    alias_map = load_alias_map()

    results: list[dict[str, Any]] = []
    tp = fp = fn = 0
    tn_correct = tn_total = 0

    for case_id, case in eval_set.items():
        gt_fallacies = {normalize(g["fallacy"], alias_map) for g in case["ground_truth"]}
        pred = predictions_dict.get(case_id)
        pred_fallacies: set[str] = set()
        if pred:
            pred_fallacies = {
                normalize(p["fallacy"], alias_map) for p in pred.get("predictions", [])
            }

        is_true_negative_case = len(gt_fallacies) == 0

        if is_true_negative_case:
            tn_total += 1
            correct = len(pred_fallacies) == 0
            if correct:
                tn_correct += 1
            results.append(
                {
                    "id": case_id,
                    "type": "true_negative",
                    "correct": correct,
                    "ground_truth": [],
                    "predicted": sorted(pred_fallacies),
                }
            )
        else:
            matched = gt_fallacies & pred_fallacies
            missed = gt_fallacies - pred_fallacies
            extra = pred_fallacies - gt_fallacies
            tp += len(matched)
            fn += len(missed)
            fp += len(extra)
            results.append(
                {
                    "id": case_id,
                    "type": "positive",
                    "ground_truth": sorted(gt_fallacies),
                    "predicted": sorted(pred_fallacies),
                    "matched": sorted(matched),
                    "missed": sorted(missed),
                    "extra_unjustified": sorted(extra),
                }
            )

    precision = tp / (tp + fp) if (tp + fp) else float("nan")
    recall = tp / (tp + fn) if (tp + fn) else float("nan")
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else float("nan")
    tn_accuracy = tn_correct / tn_total if tn_total else float("nan")

    def _round_or_none(value: float) -> float | None:
        if isinstance(value, float) and value != value:
            return None
        return round(value, 3)

    summary = {
        "positive_cases": {
            "true_positives": tp,
            "false_positives": fp,
            "false_negatives": fn,
            "precision": _round_or_none(precision),
            "recall": _round_or_none(recall),
            "f1": _round_or_none(f1),
        },
        "true_negative_cases": {
            "total": tn_total,
            "correctly_flagged_clean": tn_correct,
            "accuracy": _round_or_none(tn_accuracy),
        },
    }

    return summary, results


def compute_span_fidelity_summary(span_metrics: dict[str, int]) -> dict[str, Any]:
    """Summarize span fidelity across returned findings."""
    total = span_metrics["findings_returned"]
    in_transcript = span_metrics["spans_in_transcript"]
    not_in_transcript = span_metrics["spans_not_in_transcript"]
    rate = in_transcript / total if total else float("nan")
    return {
        "findings_returned": total,
        "spans_in_transcript": in_transcript,
        "spans_not_in_transcript": not_in_transcript,
        "span_fidelity_rate": round(rate, 3) if total and rate == rate else None,
    }


def compute_format_summary(format_metrics: dict[str, int]) -> dict[str, Any]:
    """Summarize JSON/format compliance across eval cases."""
    total = format_metrics["total"]
    json_ok = format_metrics["json_ok"]
    format_errors = format_metrics["format_errors"]
    rate = json_ok / total if total else float("nan")
    return {
        "total_cases": total,
        "json_ok": json_ok,
        "format_errors": format_errors,
        "format_compliance_rate": round(rate, 3) if total and rate == rate else None,
    }


def load_baseline_predictions(path: Path | None = None) -> list[dict[str, Any]]:
    """Load frozen eval predictions used for CI regression."""
    baseline_path = path or EVAL_BASELINE_PATH
    with open(baseline_path, encoding="utf-8") as f:
        data = json.load(f)
    return data["predictions"]


def assert_phase5_quality_gates(summary: dict[str, Any]) -> None:
    """
    Raise AssertionError if Phase 5 detection quality regresses.
    Used by CI tests and optionally after live run_eval.py runs.
    """
    pos = summary["positive_cases"]
    tn = summary["true_negative_cases"]

    f1 = pos.get("f1")
    precision = pos.get("precision")
    recall = pos.get("recall")
    tn_accuracy = tn.get("accuracy")

    failures: list[str] = []
    if f1 is None or f1 < MIN_F1:
        failures.append(f"F1 {f1} < {MIN_F1}")
    if precision is None or precision < MIN_PRECISION:
        failures.append(f"precision {precision} < {MIN_PRECISION}")
    if recall is None or recall < MIN_RECALL:
        failures.append(f"recall {recall} < {MIN_RECALL}")
    if tn_accuracy is None or tn_accuracy < MIN_TN_ACCURACY:
        failures.append(f"true-negative accuracy {tn_accuracy} < {MIN_TN_ACCURACY}")

    if failures:
        raise AssertionError(
            "Phase 5 quality gate failed: " + "; ".join(failures)
        )


def quality_gate_status(summary: dict[str, Any]) -> dict[str, bool]:
    """Return pass/fail per metric for reporting."""
    pos = summary["positive_cases"]
    tn = summary["true_negative_cases"]
    return {
        "f1": pos.get("f1") is not None and pos["f1"] >= MIN_F1,
        "precision": pos.get("precision") is not None and pos["precision"] >= MIN_PRECISION,
        "recall": pos.get("recall") is not None and pos["recall"] >= MIN_RECALL,
        "true_negative_accuracy": tn.get("accuracy") is not None and tn["accuracy"] >= MIN_TN_ACCURACY,
    }
