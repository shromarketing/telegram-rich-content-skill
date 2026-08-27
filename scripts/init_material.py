#!/usr/bin/env python3
"""Create a traceable working package for one source-to-post job."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

FILES = {
    "source.md": "# Source\n\n- Type:\n- URL or file:\n- Rights/access note:\n- Retrieved:\n\n## Raw material\n\n",
    "transcript.md": "# Transcript\n\n> Keep timestamps and speaker labels when they support verification.\n\n",
    "evidence-map.md": "# Evidence map\n\n| Claim or quote | Source | Timestamp/section | Confidence |\n|---|---|---|---|\n",
    "brief.md": "# Content brief\n\n- Audience:\n- Goal:\n- Main idea:\n- Desired action:\n- Format: plain / album / rich\n- Constraints:\n\n",
    "voice-profile-used.md": "# Voice profile used\n\n- Profile path/version:\n- Approved examples:\n- Deliberate deviations:\n\n",
    "post-plain.md": "# Plain Telegram fallback\n\n",
    "post-rich.html": "<h1>Draft title</h1>\n<p>Draft body.</p>\n",
    "validation-report.md": "# Validation report\n\n- Rich HTML validator:\n- Voice checks:\n- Links and credits:\n- Desktop review:\n- Mobile review:\n- Approved target:\n- Approval time:\n\n",
}


def slug(value: str) -> str:
    cleaned = re.sub(r"[^\w.-]+", "-", value.strip().lower(), flags=re.UNICODE)
    return cleaned.strip("-._")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a source-to-post material package")
    parser.add_argument("name", help="human-readable material name")
    parser.add_argument("--root", type=Path, default=Path("materials"))
    args = parser.parse_args()
    target = args.root / slug(args.name)
    if not target.name:
        print("ERROR: name does not produce a valid folder", file=sys.stderr)
        return 2
    if target.exists():
        print(f"ERROR: refusing to overwrite existing package: {target}", file=sys.stderr)
        return 1
    (target / "media").mkdir(parents=True)
    (target / "media" / ".gitkeep").touch()
    for name, content in FILES.items():
        (target / name).write_text(content, encoding="utf-8")
    print(f"Created material package: {target.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
