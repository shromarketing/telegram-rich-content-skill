#!/usr/bin/env python3
"""Create an isolated environment and install selected feature groups."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FEATURES = {
    "publisher": "requirements.txt",
    "youtube": "requirements-youtube.txt",
    "transcription": "requirements-transcription.txt",
    "apple": "requirements-apple-silicon.txt",
}


def parse_features(raw: str) -> list[str]:
    values = [item.strip() for item in raw.split(",") if item.strip()]
    if "all" in values:
        values = ["publisher", "youtube", "transcription"]
    unknown = sorted(set(values) - FEATURES.keys())
    if unknown:
        raise argparse.ArgumentTypeError(f"unknown feature(s): {', '.join(unknown)}")
    return list(dict.fromkeys(values))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Plan or apply a local installation")
    parser.add_argument(
        "--features",
        type=parse_features,
        default=parse_features("all"),
        help="publisher,youtube,transcription,apple,all",
    )
    parser.add_argument("--venv", type=Path, default=ROOT / ".venv")
    parser.add_argument("--apply", action="store_true", help="create the environment and install")
    parser.add_argument(
        "--init-env",
        action="store_true",
        help="copy .env.example to .env only when .env does not exist",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    requirements = [ROOT / FEATURES[name] for name in args.features]
    print(f"Environment: {args.venv}")
    print(f"Features: {', '.join(args.features) or 'core only'}")
    for path in requirements:
        print(f"  - {path.name}")
    if not args.apply:
        print("Plan only. Re-run with --apply to install; existing .env is never overwritten.")
        return 0
    if sys.version_info < (3, 11):
        print("ERROR: Python 3.11+ is required", file=sys.stderr)
        return 2
    if not args.venv.exists():
        venv.EnvBuilder(with_pip=True).create(args.venv)
    python = args.venv / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
    try:
        for requirement in requirements:
            subprocess.run(
                [str(python), "-m", "pip", "install", "-r", str(requirement)],
                check=True,
            )
    except subprocess.CalledProcessError:
        print(
            "ERROR: dependency installation failed. The environment was kept so you "
            "can inspect it and retry after checking Python, network, and package index access.",
            file=sys.stderr,
        )
        return 1
    example = ROOT / ".env.example"
    target = ROOT / ".env"
    if args.init_env and example.is_file() and not target.exists():
        shutil.copyfile(example, target)
        print("Created .env from .env.example; add secrets locally.")
    elif target.exists():
        print("Kept existing .env unchanged.")
    else:
        print("No .env created. Add --init-env when publisher configuration is needed.")
    print(f"Installed. Run: {python} scripts/doctor.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
