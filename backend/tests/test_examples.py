"""Golden examples schema and formatter checks."""
import json
from pathlib import Path

from examples_format import format_examples_text

HERE = Path(__file__).resolve().parents[1]
EXAMPLES_PATH = HERE / "fallacy_reference" / "examples.json"
TAXONOMY_PATH = HERE / "fallacy_reference" / "fallacies.json"

REQUIRED_PURPOSES = {
    "clear_positive",
    "true_negative",
    "borderline_low_confidence",
    "strengthen_anti_pattern",
}


def _load_examples():
    with open(EXAMPLES_PATH, encoding="utf-8") as f:
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


def test_examples_has_four_purposes():
    examples = _load_examples()
    purposes = {ex["purpose"] for ex in examples}
    assert REQUIRED_PURPOSES.issubset(purposes)


def test_examples_required_fields():
    examples = _load_examples()
    for example in examples:
        assert "id" in example
        assert "purpose" in example
        assert "title" in example
        assert "input" in example
        assert "output" in example
        assert "findings" in example["output"]
        assert isinstance(example["output"]["findings"], list)


def test_examples_spans_in_input():
    examples = _load_examples()
    for example in examples:
        text = example["input"]
        for finding in example["output"]["findings"]:
            assert finding["span"] in text, f"{example['id']}: span not in input"


def test_examples_fallacy_names_in_taxonomy():
    canonical = _canonical_names()
    examples = _load_examples()
    for example in examples:
        for finding in example["output"]["findings"]:
            assert finding["fallacy"] in canonical, (
                f"{example['id']}: unknown fallacy {finding['fallacy']!r}"
            )


def test_strengthen_anti_pattern_example_present():
    examples = _load_examples()
    anti = [ex for ex in examples if ex["purpose"] == "strengthen_anti_pattern"]
    assert len(anti) == 1
    assert "anti_pattern" in anti[0]
    assert "why_wrong" in anti[0]["anti_pattern"]


def test_format_examples_text_renders_all_blocks():
    examples = _load_examples()
    text = format_examples_text(examples)
    for example in examples:
        assert example["id"] in text
        assert example["title"] in text
    assert "Golden Examples" in text
    assert "Anti-pattern" in text
