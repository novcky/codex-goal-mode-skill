#!/usr/bin/env python3
"""Run the pinned official OpenAI skill validator."""

from __future__ import annotations

import hashlib
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
VALIDATOR_SHA256 = "6cc9dc3199c935916cf6f73fcbbbb0e3bb1b58c8f5109fefa499978908164f51"
DOWNLOAD_TIMEOUT_SECONDS = 20
RUN_TIMEOUT_SECONDS = 30


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
            with urllib.request.urlopen(VALIDATOR_URL, timeout=DOWNLOAD_TIMEOUT_SECONDS) as response:
                data = response.read()
        except Exception as exc:  # pragma: no cover - network failure detail
            fail(f"failed to download official validator: {exc}")

        digest = hashlib.sha256(data).hexdigest()
        if digest != VALIDATOR_SHA256:
            fail(f"official validator sha256 mismatch: {digest}")
        validator.write_bytes(data)

        try:
            result = subprocess.run(
                [sys.executable, str(validator), str(SKILL_DIR)],
                check=False,
                timeout=RUN_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired:
            fail(f"official validator timed out after {RUN_TIMEOUT_SECONDS} seconds")
        if result.returncode != 0:
            raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
