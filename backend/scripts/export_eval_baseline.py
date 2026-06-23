"""Export eval_results.json predictions to the CI regression baseline."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RESULTS = BACKEND_ROOT / "eval_results.json"
DEFAULT_BASELINE = BACKEND_ROOT / "fallacy_reference" / "eval_baseline_predictions.json"


def export_baseline(results_path: Path, baseline_path: Path) -> None:
    results = json.loads(results_path.read_text(encoding="utf-8"))
    predictions = [
        {
            "id": row["id"],
            "predictions": [{"fallacy": name} for name in row.get("predicted", [])],
        }
        for row in results["results"]
    ]
    baseline = {
        "label": "phase5-calibration-v1",
        "source_timestamp": results.get("timestamp"),
        "summary": results["summary"],
        "predictions": predictions,
    }
    baseline_path.write_text(json.dumps(baseline, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(predictions)} cases -> {baseline_path}")
    print(f"F1={baseline['summary']['positive_cases']['f1']} "
          f"P={baseline['summary']['positive_cases']['precision']}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Export eval baseline for CI quality gate.")
    parser.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    args = parser.parse_args()
    export_baseline(args.results.resolve(), args.baseline.resolve())


if __name__ == "__main__":
    main()
