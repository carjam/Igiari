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

For full eval runs (40 cases), disable the dev rate limit before starting the server:
  set IGIARI_DISABLE_RATE_LIMIT=1   (Windows cmd)
  $env:IGIARI_DISABLE_RATE_LIMIT="1"   (PowerShell)
  export IGIARI_DISABLE_RATE_LIMIT=1   (bash)
"""
import json
import sys
import time
from pathlib import Path
import requests

from eval_grading import (
    assert_phase5_quality_gates,
    compute_format_summary,
    compute_span_fidelity_summary,
    grade,
    quality_gate_status,
)

HERE = Path(__file__).parent
EVAL_SET_PATH = HERE / "fallacy_reference" / "eval_set.json"
BACKEND_URL = "http://localhost:8000/api/scan"
def run_eval():
    """Run all eval cases through the backend and collect predictions."""
    with open(EVAL_SET_PATH) as f:
        eval_set = json.load(f)
    
    print(f"Loaded {len(eval_set)} eval cases")
    print(f"Backend URL: {BACKEND_URL}")
    print("=" * 60)
    
    predictions = []
    errors = []
    format_metrics = {
        "total": len(eval_set),
        "json_ok": 0,
        "format_errors": 0,
    }
    span_metrics = {
        "findings_returned": 0,
        "spans_in_transcript": 0,
        "spans_not_in_transcript": 0,
    }
    
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
                try:
                    result = response.json()
                except json.JSONDecodeError:
                    format_metrics["format_errors"] += 1
                    error_msg = "HTTP 200 but response body is not valid JSON"
                    errors.append({"id": case_id, "error": error_msg, "type": "format_violation"})
                    print(f"ERROR: {error_msg}")
                    predictions.append({"id": case_id, "predictions": []})
                    continue

                if "findings" not in result or not isinstance(result["findings"], list):
                    format_metrics["format_errors"] += 1
                    error_msg = "Response missing findings array"
                    errors.append({"id": case_id, "error": error_msg, "type": "format_violation"})
                    print(f"ERROR: {error_msg}")
                    predictions.append({"id": case_id, "predictions": []})
                    continue

                format_metrics["json_ok"] += 1
                findings = result.get("findings", [])
                
                for finding in findings:
                    span = finding.get("span", "")
                    span_metrics["findings_returned"] += 1
                    if span and span in text:
                        span_metrics["spans_in_transcript"] += 1
                    elif span:
                        span_metrics["spans_not_in_transcript"] += 1
                
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
                
                print(f"OK ({len(findings)} findings)")
            elif response.status_code == 502:
                format_metrics["format_errors"] += 1
                error_msg = f"HTTP 502 (model JSON parse failure): {response.text[:100]}"
                errors.append({"id": case_id, "error": error_msg, "type": "format_violation"})
                print(f"ERROR: {error_msg}")
                predictions.append({"id": case_id, "predictions": []})
            else:
                error_msg = f"HTTP {response.status_code}: {response.text[:100]}"
                errors.append({"id": case_id, "error": error_msg, "type": "api_error"})
                print(f"ERROR: {error_msg}")
                predictions.append({"id": case_id, "predictions": []})
        
        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed: {str(e)[:100]}"
            errors.append({"id": case_id, "error": error_msg, "type": "request_error"})
            print(f"ERROR: {error_msg}")
            predictions.append({"id": case_id, "predictions": []})
        
        # Small delay to avoid overwhelming the backend
        time.sleep(0.1)
    
    return predictions, errors, format_metrics, span_metrics


def print_results(summary, results, errors, format_summary, span_summary):
    """Print evaluation results."""
    print("\n" + "=" * 60)
    print("=== EVALUATION SUMMARY ===")
    print("=" * 60)
    
    print("\n[POSITIVE CASES] (fallacies present):")
    pos = summary["positive_cases"]
    print(f"  True Positives:  {pos['true_positives']}")
    print(f"  False Positives: {pos['false_positives']}")
    print(f"  False Negatives: {pos['false_negatives']}")
    print(f"  Precision: {pos['precision']}")
    print(f"  Recall:    {pos['recall']}")
    print(f"  F1 Score:  {pos['f1']}")
    
    print("\n[TRUE NEGATIVE CASES] (clean text):")
    tn = summary["true_negative_cases"]
    print(f"  Total: {tn['total']}")
    print(f"  Correctly identified as clean: {tn['correctly_flagged_clean']}")
    print(f"  Accuracy: {tn['accuracy']}")

    print("\n[FORMAT COMPLIANCE]:")
    print(f"  JSON OK: {format_summary['json_ok']}/{format_summary['total_cases']}")
    print(f"  Format errors: {format_summary['format_errors']}")
    print(f"  Compliance rate: {format_summary['format_compliance_rate']}")

    print("\n[SPAN FIDELITY] (returned findings only):")
    print(f"  Findings returned: {span_summary['findings_returned']}")
    print(f"  Spans in transcript: {span_summary['spans_in_transcript']}")
    print(f"  Spans not in transcript: {span_summary['spans_not_in_transcript']}")
    print(f"  Fidelity rate: {span_summary['span_fidelity_rate']}")
    if span_summary["spans_not_in_transcript"]:
        print("  Note: backend drops invalid spans before responding; non-zero here indicates a bug.")
    
    # Phase 5 quality gate check
    print("\n" + "=" * 60)
    print("=== PHASE 5 QUALITY GATE ===")
    print("=" * 60)

    gate = quality_gate_status(summary)
    print(f"  F1 >= 0.75:              {'PASS' if gate['f1'] else 'FAIL'} ({pos['f1']})")
    print(f"  Precision >= 0.65:       {'PASS' if gate['precision'] else 'FAIL'} ({pos['precision']})")
    print(f"  Recall >= 0.80:          {'PASS' if gate['recall'] else 'FAIL'} ({pos['recall']})")
    print(f"  TN accuracy >= 1.0:      {'PASS' if gate['true_negative_accuracy'] else 'FAIL'} ({tn['accuracy']})")

    issues = []

    if not gate["f1"]:
        issues.append(f"CRITICAL: F1 ({pos['f1']}) below Phase 5 minimum (0.75)")
    if not gate["precision"]:
        issues.append(f"CRITICAL: PRECISION ({pos['precision']}) below Phase 5 minimum (0.65)")
    if not gate["recall"]:
        issues.append(f"WARNING: RECALL ({pos['recall']}) below minimum (0.80)")
    if not gate["true_negative_accuracy"]:
        issues.append(f"CRITICAL: TRUE NEGATIVE ACCURACY ({tn['accuracy']}) below minimum (1.0)")
    
    if pos['recall'] is not None and pos['recall'] < 0.3:
        issues.append(f"WARNING: LOW RECALL ({pos['recall']}) - Missing most fallacies")
    
    if pos['precision'] is not None and pos['precision'] < 0.3:
        issues.append(f"WARNING: LOW PRECISION ({pos['precision']}) - Too many false positives")
    
    if tn['accuracy'] is not None and tn['accuracy'] < 0.6:
        issues.append(f"CRITICAL: FAILING TRUE NEGATIVES ({tn['accuracy']}) - Hallucinating fallacies in clean text")
        issues.append("   This violates the 'no dark patterns' requirement (spec 01)")
    
    if errors:
        format_err_count = sum(1 for e in errors if e.get("type") == "format_violation")
        if format_err_count:
            issues.append(f"WARNING: {format_err_count} FORMAT VIOLATIONS (non-JSON or invalid schema)")

        other_errors = len(errors) - format_err_count
        if other_errors:
            issues.append(f"WARNING: {other_errors} API/REQUEST ERRORS occurred during evaluation")
    
    if issues:
        print("\n[QUALITY ISSUES DETECTED]\n")
        for issue in issues:
            print(issue)
        print("\n[RECOMMENDATION] Fix prompt/calibration before deploying.")
    else:
        print("\n[PHASE 5 QUALITY GATE PASSED]")
        print("   Detection quality meets regression thresholds.")
    
    # Detailed per-case results
    print("\n" + "=" * 60)
    print("=== PER-CASE DETAIL ===")
    print("=" * 60)
    
    for r in results:
        flag = ""
        if r["type"] == "true_negative" and not r["correct"]:
            flag = "  [FALSE ALARM] on clean text"
        if r["type"] == "positive" and (r.get("missed") or r.get("extra_unjustified")):
            flag = "  [MISMATCH]"
        
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
        print("OK - Backend is running")
    except requests.exceptions.RequestException:
        print("ERROR - Backend is not running!")
        print("\nPlease start the backend first:")
        print("  cd backend")
        print("  python server.py")
        sys.exit(1)
    
    # Run evaluation
    predictions, errors, format_metrics, span_metrics = run_eval()
    
    # Grade results
    print("\nGrading predictions...")
    summary, results = grade(predictions)
    format_summary = compute_format_summary(format_metrics)
    span_summary = compute_span_fidelity_summary(span_metrics)
    
    # Print results
    print_results(summary, results, errors, format_summary, span_summary)
    
    # Save results to file
    output = {
        "summary": summary,
        "format_compliance": format_summary,
        "span_fidelity": span_summary,
        "results": results,
        "errors": errors,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    output_path = HERE / "eval_results.json"
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\n[SAVED] Full results saved to: {output_path}")

    try:
        assert_phase5_quality_gates(summary)
    except AssertionError as exc:
        print(f"\n[PHASE 5 GATE FAILED] {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
