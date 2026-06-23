"""Eval set schema and ground-truth integrity checks."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
EVAL_SET_PATH = HERE / "fallacy_reference" / "eval_set.json"
TAXONOMY_PATH = HERE / "fallacy_reference" / "fallacies.json"


def _load_eval_set():
    with open(EVAL_SET_PATH, encoding="utf-8") as f:
        return json.load(f)


def _canonical_names():
    with open(TAXONOMY_PATH, encoding="utf-8") as f:
        taxonomy = json.load(f)
    names = set()
    for entry in taxonomy:
        names.add(entry["name"])
        for alias in entry.get("aliases", []):
            names.add(alias)
    return names


def test_eval_set_has_unique_ids():
    cases = _load_eval_set()
    ids = [case["id"] for case in cases]
    assert len(ids) == len(set(ids)), f"Duplicate eval ids: {ids}"


def test_eval_set_required_fields():
    cases = _load_eval_set()
    for case in cases:
        assert "id" in case
        assert "transcript" in case
        assert "ground_truth" in case
        assert isinstance(case["ground_truth"], list)
        for gt in case["ground_truth"]:
            assert "fallacy" in gt
            assert "span" in gt


def test_eval_set_ground_truth_spans_in_transcript():
    cases = _load_eval_set()
    for case in cases:
        transcript = case["transcript"]
        for gt in case["ground_truth"]:
            span = gt["span"]
            assert span in transcript, (
                f"{case['id']}: ground-truth span not found verbatim in transcript: {span[:60]!r}..."
            )


def test_eval_set_fallacy_names_in_taxonomy():
    canonical = _canonical_names()
    cases = _load_eval_set()
    for case in cases:
        for gt in case["ground_truth"]:
            assert gt["fallacy"] in canonical, (
                f"{case['id']}: unknown fallacy {gt['fallacy']!r}"
            )


def test_eval_set_includes_phase3_boundary_cases():
    cases = _load_eval_set()
    ids = {case["id"] for case in cases}
    phase3_ids = {
        "eval_031", "eval_032", "eval_033", "eval_034", "eval_035",
        "eval_036", "eval_037", "eval_038", "eval_039", "eval_040",
    }
    assert phase3_ids.issubset(ids)


def test_eval_baseline_matches_eval_set_ids():
    baseline_path = HERE / "fallacy_reference" / "eval_baseline_predictions.json"
    assert baseline_path.is_file()
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    eval_ids = {case["id"] for case in _load_eval_set()}
    baseline_ids = {row["id"] for row in baseline["predictions"]}
    assert baseline_ids == eval_ids
