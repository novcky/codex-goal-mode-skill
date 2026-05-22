#!/usr/bin/env python3
"""Run the pinned official OpenAI skill validator."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "goal-mode"
VALIDATOR_URL = (
    "https://raw.githubusercontent.com/openai/skills/"
    "e8acbcb5f86cef1e04b96eed7557148b719c5f6b/"
    "skills/.system/skill-creator/scripts/quick_validate.py"
)


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    try:
        import yaml  # noqa: F401
    except ModuleNotFoundError:
        fail("PyYAML is required; run `python -m pip install pyyaml` first")

    if not SKILL_DIR.is_dir():
        fail("skills/goal-mode is missing")

    with tempfile.TemporaryDirectory(prefix="goal-mode-official-validate-") as tmp:
        validator = Path(tmp) / "quick_validate.py"
        try:
            urllib.request.urlretrieve(VALIDATOR_URL, validator)
        except Exception as exc:  # pragma: no cover - network failure detail
            fail(f"failed to download official validator: {exc}")

        result = subprocess.run([sys.executable, str(validator), str(SKILL_DIR)], check=False)
        if result.returncode != 0:
            raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
