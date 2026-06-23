"""
Sync Igiari fallacy-detection source files to the Cursor skill port.

Canonical sources (igiari/backend):
  - prompt_template.txt
  - fallacy_reference/fallacies.json
  - fallacy_reference/eval_set.json
  - fallacy_reference/examples.json

Skill targets (logical-fallacy-detection skill):
  - reference/prompt.txt
  - reference/taxonomy.md
  - reference/eval_set.json
  - reference/examples.md

Usage:
  python scripts/sync_cursor_skill.py
  python scripts/sync_cursor_skill.py --skill-root "C:/path/to/logical-fallacy-detection"
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = BACKEND_ROOT.parents[1]
DEFAULT_SKILL_ROOT = (
    WORKSPACE_ROOT
    / "AIDevTools"
    / "Claude"
    / "cursor-skills"
    / "logical-fallacy-detection"
)

sys.path.insert(0, str(BACKEND_ROOT))
from examples_format import format_examples_text  # noqa: E402
from taxonomy_format import format_taxonomy_text  # noqa: E402


def sync(skill_root: Path) -> None:
    ref_dir = skill_root / "reference"
    ref_dir.mkdir(parents=True, exist_ok=True)

    prompt_src = BACKEND_ROOT / "prompt_template.txt"
    prompt_dst = ref_dir / "prompt.txt"
    shutil.copy2(prompt_src, prompt_dst)
    print(f"Copied prompt -> {prompt_dst}")

    fallacies_path = BACKEND_ROOT / "fallacy_reference" / "fallacies.json"
    fallacies = json.loads(fallacies_path.read_text(encoding="utf-8"))
    taxonomy_dst = ref_dir / "taxonomy.md"
    taxonomy_dst.write_text(format_taxonomy_text(fallacies) + "\n", encoding="utf-8")
    print(f"Wrote {len(fallacies)} fallacies -> {taxonomy_dst}")

    eval_src = BACKEND_ROOT / "fallacy_reference" / "eval_set.json"
    eval_dst = ref_dir / "eval_set.json"
    shutil.copy2(eval_src, eval_dst)
    print(f"Copied eval set -> {eval_dst}")

    examples_path = BACKEND_ROOT / "fallacy_reference" / "examples.json"
    examples = json.loads(examples_path.read_text(encoding="utf-8"))
    examples_dst = ref_dir / "examples.md"
    examples_dst.write_text(format_examples_text(examples), encoding="utf-8")
    print(f"Wrote {len(examples)} examples -> {examples_dst}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync Igiari fallacy detection sources to Cursor skill.")
    parser.add_argument(
        "--skill-root",
        type=Path,
        default=DEFAULT_SKILL_ROOT,
        help="Path to logical-fallacy-detection skill directory",
    )
    args = parser.parse_args()

    if not args.skill_root.is_dir():
        parser.error(f"Skill root not found: {args.skill_root}")

    sync(args.skill_root.resolve())
    print("Done.")


if __name__ == "__main__":
    main()
