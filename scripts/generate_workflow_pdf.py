"""Generate English PROJECT_WORKFLOW.pdf (requires pandoc + xelatex)."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SOURCE = ROOT / "scripts" / "workflow_source.md"
OUTPUT = ROOT / "docs" / "PROJECT_WORKFLOW.pdf"
DESKTOP_NAMES = [
    Path.home() / "Desktop" / "Tesla_Financial_Analysis_Project_Workflow.pdf",
    Path(r"f:\桌面") / "Tesla_Financial_Analysis_Project_Workflow.pdf",
    ROOT / "Tesla_Financial_Analysis_Project_Workflow.pdf",
]


def _ascii_tree(text: str) -> str:
    replacements = {
        "├──": "|--",
        "└──": "`--",
        "│": "|",
        "≥": ">=",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def generate() -> Path:
    if not SOURCE.exists():
        raise FileNotFoundError(f"Source not found: {SOURCE}")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    tmp = OUTPUT.parent / "_workflow_build.md"
    tmp.write_text(_ascii_tree(SOURCE.read_text(encoding="utf-8")), encoding="utf-8")

    cmd = [
        "pandoc",
        str(tmp),
        "-o",
        str(OUTPUT),
        "--pdf-engine=xelatex",
        "-V",
        "geometry:margin=1in",
        "-V",
        "mainfont=Segoe UI",
        "-V",
        "monofont=Consolas",
    ]
    subprocess.run(cmd, check=True)
    tmp.unlink(missing_ok=True)

    for target in DESKTOP_NAMES:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(OUTPUT, target)

    print("PDF saved:", str(OUTPUT))
    return OUTPUT


if __name__ == "__main__":
    try:
        generate()
    except FileNotFoundError as e:
        print(e, file=sys.stderr)
        sys.exit(1)
