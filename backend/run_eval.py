"""
Phase 2: Run backend against eval set and compute quality metrics.

This script:
1. Assumes the backend server is running on localhost:8000
2. Sends each eval case to POST /api/scan
3. Collects predictions in the format grade_eval.py expects
4. Computes precision/recall/F1 and true-negative accuracy

Usage:
    python run_eval.py

Requires: backend server running (python server.py)
"""
import json
import sys
import time
from pathlib import Path
import requests

HERE = Path(__file__).parent
EVAL_SET_PATH = HERE / "fallacy_reference" / "eval_set.json"
TAXONOMY_PATH = HERE / "fallacy_reference" / "fallacies.json"
BACKEND_URL = "http://localhost:8000/api/scan"


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
    """Normalize fallacy name using alias map."""
    return alias_map.get(name.strip().lower(), name.strip())


def run_eval():
    """Run all eval cases through the backend and collect predictions."""
    with open(EVAL_SET_PATH) as f:
        eval_set = json.load(f)
    
    print(f"Loaded {len(eval_set)} eval cases")
    print(f"Backend URL: {BACKEND_URL}")
    print("=" * 60)
    
    predictions = []
    errors = []
    
    for i, case in enumerate(eval_set, 1):
        case_id = case["id"]
        text = case["transcript"]
        
        print(f"\n[{i}/{len(eval_set)}] Testing {case_id}...", end=" ")
        
        try:
            response = requests.post(
                BACKEND_URL,
                json={"text": text},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                findings = result.get("findings", [])
                
                # Convert to grader format
                predictions.append({
                    "id": case_id,
                    "predictions": [
                        {
                            "fallacy": f["fallacy"],
                            "span": f["span"],
                            "confidence": f["confidence"]
                        }
                        for f in findings
                    ]
                })
                
                print(f"✓ ({len(findings)} findings)")
            else:
                error_msg = f"HTTP {response.status_code}: {response.text[:100]}"
                errors.append({"id": case_id, "error": error_msg})
                print(f"✗ {error_msg}")
                predictions.append({"id": case_id, "predictions": []})
        
        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed: {str(e)[:100]}"
            errors.append({"id": case_id, "error": error_msg})
            print(f"✗ {error_msg}")
            predictions.append({"id": case_id, "predictions": []})
        
        # Small delay to avoid overwhelming the backend
        time.sleep(0.1)
    
    return predictions, errors


def grade(predictions):
    """Grade predictions against ground truth (adapted from grade_eval.py)."""
    with open(EVAL_SET_PATH) as f:
        eval_set = {case["id"]: case for case in json.load(f)}
    
    predictions_dict = {p["id"]: p for p in predictions}
    alias_map = load_alias_map()
    
    results = []
    tp = fp = fn = 0
    tn_correct = tn_total = 0
    
    for case_id, case in eval_set.items():
        gt_fallacies = {normalize(g["fallacy"], alias_map) for g in case["ground_truth"]}
        pred = predictions_dict.get(case_id)
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
            "precision": round(precision, 3) if not isinstance(precision, float) or not (precision != precision) else None,
            "recall": round(recall, 3) if not isinstance(recall, float) or not (recall != recall) else None,
            "f1": round(f1, 3) if not isinstance(f1, float) or not (f1 != f1) else None,
        },
        "true_negative_cases": {
            "total": tn_total,
            "correctly_flagged_clean": tn_correct,
            "accuracy": round(tn_accuracy, 3) if not isinstance(tn_accuracy, float) or not (tn_accuracy != tn_accuracy) else None,
        },
    }
    
    return summary, results


def print_results(summary, results, errors):
    """Print evaluation results."""
    print("\n" + "=" * 60)
    print("=== EVALUATION SUMMARY ===")
    print("=" * 60)
    
    print("\n📊 POSITIVE CASES (fallacies present):")
    pos = summary["positive_cases"]
    print(f"  True Positives:  {pos['true_positives']}")
    print(f"  False Positives: {pos['false_positives']}")
    print(f"  False Negatives: {pos['false_negatives']}")
    print(f"  Precision: {pos['precision']}")
    print(f"  Recall:    {pos['recall']}")
    print(f"  F1 Score:  {pos['f1']}")
    
    print("\n✅ TRUE NEGATIVE CASES (clean text):")
    tn = summary["true_negative_cases"]
    print(f"  Total: {tn['total']}")
    print(f"  Correctly identified as clean: {tn['correctly_flagged_clean']}")
    print(f"  Accuracy: {tn['accuracy']}")
    
    # Phase 2 quality gate check
    print("\n" + "=" * 60)
    print("=== PHASE 2 QUALITY GATE ===")
    print("=" * 60)
    
    issues = []
    
    if pos['recall'] is not None and pos['recall'] < 0.3:
        issues.append(f"⚠️  LOW RECALL ({pos['recall']}) - Missing most fallacies")
    
    if pos['precision'] is not None and pos['precision'] < 0.3:
        issues.append(f"⚠️  LOW PRECISION ({pos['precision']}) - Too many false positives")
    
    if tn['accuracy'] is not None and tn['accuracy'] < 0.6:
        issues.append(f"🚫 FAILING TRUE NEGATIVES ({tn['accuracy']}) - Hallucinating fallacies in clean text")
        issues.append("   This violates the 'no dark patterns' requirement (spec 01)")
    
    if errors:
        issues.append(f"⚠️  {len(errors)} API ERRORS occurred during evaluation")
    
    if issues:
        print("\n❌ QUALITY ISSUES DETECTED:\n")
        for issue in issues:
            print(issue)
        print("\n⛔ RECOMMENDATION: Fix prompt/calibration before proceeding to Phase 3")
        print("   (Per spec 04: 'Building a frontend on top of a backend that doesn't")
        print("    work is wasted effort')")
    else:
        print("\n✅ QUALITY GATE PASSED")
        print("   Backend quality is acceptable for MVP demand-test")
        print("   Ready to proceed to Phase 3 (Frontend build)")
    
    # Detailed per-case results
    print("\n" + "=" * 60)
    print("=== PER-CASE DETAIL ===")
    print("=" * 60)
    
    for r in results:
        flag = ""
        if r["type"] == "true_negative" and not r["correct"]:
            flag = "  🔴 FALSE ALARM on clean text"
        if r["type"] == "positive" and (r.get("missed") or r.get("extra_unjustified")):
            flag = "  ⚠️  mismatch"
        
        print(f"\n{r['id']} [{r['type']}]{flag}")
        if r["type"] == "positive":
            print(f"  ground truth: {r['ground_truth']}")
            print(f"  predicted:    {r['predicted']}")
            if r.get("missed"):
                print(f"  missed:       {r['missed']}")
            if r.get("extra_unjustified"):
                print(f"  extra:        {r['extra_unjustified']}")
        else:
            if r["predicted"]:
                print(f"  predicted:    {r['predicted']} (should be empty)")
    
    if errors:
        print("\n" + "=" * 60)
        print("=== ERRORS ===")
        print("=" * 60)
        for err in errors:
            print(f"{err['id']}: {err['error']}")


def main():
    print("=" * 60)
    print("Phase 2: Quality Validation Against Eval Set")
    print("=" * 60)
    
    # Check if backend is running
    print("\nChecking if backend is running...")
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        print("✓ Backend is running")
    except requests.exceptions.RequestException:
        print("✗ Backend is not running!")
        print("\nPlease start the backend first:")
        print("  cd backend")
        print("  python server.py")
        sys.exit(1)
    
    # Run evaluation
    predictions, errors = run_eval()
    
    # Grade results
    print("\nGrading predictions...")
    summary, results = grade(predictions)
    
    # Print results
    print_results(summary, results, errors)
    
    # Save results to file
    output = {
        "summary": summary,
        "results": results,
        "errors": errors,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    output_path = HERE / "eval_results.json"
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\n💾 Full results saved to: {output_path}")


if __name__ == "__main__":
    main()
