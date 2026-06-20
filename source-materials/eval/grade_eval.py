"""
Grade fallacy-detection predictions against the eval set ground truth.

Usage:
    python grade_eval.py predictions.json

predictions.json should be a list of objects shaped like:
    [
      {
        "id": "eval_001",
        "predictions": [
          {"fallacy": "Argument from Anecdote", "span": "...", "confidence": "high"}
        ]
      },
      ...
    ]

Matching is done by fallacy NAME (case-insensitive, alias-aware) per case, not
by exact span text, since span boundaries are inherently fuzzy. A case counts
as a true positive if at least one ground-truth fallacy name is matched by at
least one predicted fallacy name. This is a lenient first-pass grader meant
for quick iteration, not publication-grade scoring.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
EVAL_SET_PATH = HERE / "eval_set.json"
TAXONOMY_PATH = HERE.parent / "references" / "fallacies.json"


def load_alias_map():
    """Build a lowercase name/alias -> canonical name map for fuzzy matching."""
    with open(TAXONOMY_PATH) as f:
        taxonomy = json.load(f)
    alias_map = {}
    for entry in taxonomy:
        canonical = entry["name"]
        alias_map[canonical.lower()] = canonical
        for alias in entry.get("aliases", []):
            alias_map[alias.lower()] = canonical
    return alias_map


def normalize(name, alias_map):
    return alias_map.get(name.strip().lower(), name.strip())


def grade(predictions_path):
    with open(EVAL_SET_PATH) as f:
        eval_set = {case["id"]: case for case in json.load(f)}

    with open(predictions_path) as f:
        predictions = {p["id"]: p for p in json.load(f)}

    alias_map = load_alias_map()

    results = []
    tp = fp = fn = 0
    tn_correct = tn_total = 0

    for case_id, case in eval_set.items():
        gt_fallacies = {normalize(g["fallacy"], alias_map) for g in case["ground_truth"]}
        pred = predictions.get(case_id)
        pred_fallacies = set()
        if pred:
            pred_fallacies = {normalize(p["fallacy"], alias_map) for p in pred.get("predictions", [])}

        is_true_negative_case = len(gt_fallacies) == 0

        if is_true_negative_case:
            tn_total += 1
            correct = len(pred_fallacies) == 0
            if correct:
                tn_correct += 1
            results.append({
                "id": case_id,
                "type": "true_negative",
                "correct": correct,
                "ground_truth": [],
                "predicted": sorted(pred_fallacies),
            })
        else:
            matched = gt_fallacies & pred_fallacies
            missed = gt_fallacies - pred_fallacies
            extra = pred_fallacies - gt_fallacies
            tp += len(matched)
            fn += len(missed)
            fp += len(extra)
            results.append({
                "id": case_id,
                "type": "positive",
                "ground_truth": sorted(gt_fallacies),
                "predicted": sorted(pred_fallacies),
                "matched": sorted(matched),
                "missed": sorted(missed),
                "extra_unjustified": sorted(extra),
            })

    precision = tp / (tp + fp) if (tp + fp) else float("nan")
    recall = tp / (tp + fn) if (tp + fn) else float("nan")
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else float("nan")
    tn_accuracy = tn_correct / tn_total if tn_total else float("nan")

    summary = {
        "positive_cases": {
            "true_positives": tp,
            "false_positives": fp,
            "false_negatives": fn,
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "f1": round(f1, 3),
        },
        "true_negative_cases": {
            "total": tn_total,
            "correctly_flagged_clean": tn_correct,
            "accuracy": round(tn_accuracy, 3),
        },
    }

    return summary, results


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python grade_eval.py predictions.json")
        sys.exit(1)

    summary, results = grade(sys.argv[1])

    print("=== SUMMARY ===")
    print(json.dumps(summary, indent=2))
    print("\n=== PER-CASE DETAIL ===")
    for r in results:
        flag = ""
        if r["type"] == "true_negative" and not r["correct"]:
            flag = "  <-- FALSE ALARM on clean text"
        if r["type"] == "positive" and (r.get("missed") or r.get("extra_unjustified")):
            flag = "  <-- mismatch"
        print(f"{r['id']} [{r['type']}]{flag}")
        if r["type"] == "positive":
            print(f"  ground truth: {r['ground_truth']}")
            print(f"  predicted:    {r['predicted']}")
        else:
            print(f"  predicted:    {r['predicted']}")
