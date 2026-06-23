"""Sync script smoke tests."""
import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT / "scripts"))

from sync_cursor_skill import sync  # noqa: E402


def test_sync_writes_all_reference_files(tmp_path):
    skill_root = tmp_path / "skill"
    sync(skill_root)

    ref = skill_root / "reference"
    assert (ref / "prompt.txt").is_file()
    assert (ref / "taxonomy.md").is_file()
    assert (ref / "eval_set.json").is_file()
    assert (ref / "examples.md").is_file()

    eval_set = json.loads((ref / "eval_set.json").read_text(encoding="utf-8"))
    assert len(eval_set) == 40
    assert "Pattern:" in (ref / "taxonomy.md").read_text(encoding="utf-8")
    assert "Golden Examples" in (ref / "examples.md").read_text(encoding="utf-8")
