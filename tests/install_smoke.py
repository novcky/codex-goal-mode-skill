#!/usr/bin/env python3
"""Smoke test that the installable skill package can be copied cleanly."""

from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "goal-mode"
EXPECTED_FILES = {
    Path("SKILL.md"),
    Path("agents/openai.yaml"),
    Path("references/goal-workflow.md"),
}


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    if not SKILL_DIR.is_dir():
        fail("skills/goal-mode is missing")

    with tempfile.TemporaryDirectory(prefix="goal-mode-install-") as tmp:
        install_root = Path(tmp)
        installed = install_root / "goal-mode"
        shutil.copytree(SKILL_DIR, installed)

        actual_files = {path.relative_to(installed) for path in installed.rglob("*") if path.is_file()}
        if actual_files != EXPECTED_FILES:
            unexpected = ", ".join(str(path) for path in sorted(actual_files - EXPECTED_FILES))
            missing = ", ".join(str(path) for path in sorted(EXPECTED_FILES - actual_files))
            fail(f"installed file set mismatch; unexpected: {unexpected or 'none'}; missing: {missing or 'none'}")

        skill_md = (installed / "SKILL.md").read_text(encoding="utf-8")
        if "name: goal-mode" not in skill_md:
            fail("installed SKILL.md does not declare name: goal-mode")
        if "references/goal-workflow.md" not in skill_md:
            fail("installed SKILL.md does not reference the workflow file")

    print("goal-mode install smoke test passed")


if __name__ == "__main__":
    main()
