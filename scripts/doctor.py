#!/usr/bin/env python3
"""Offline-first diagnostics for Telegram Rich Content Skill."""

from __future__ import annotations

import argparse
import importlib.util
import json
import platform
import shutil
import sys
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODULES = {
    "aiogram": "publisher",
    "dotenv": "publisher",
    "yt_dlp": "YouTube",
    "faster_whisper": "local transcription",
    "mlx_whisper": "optional Apple Silicon transcription",
}


@dataclass
class Check:
    name: str
    status: str
    detail: str


def read_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def local_checks(env_file: Path) -> list[Check]:
    git = shutil.which("git")
    ffmpeg = shutil.which("ffmpeg")
    checks = [
        Check(
            "python",
            "pass" if sys.version_info >= (3, 11) else "fail",
            platform.python_version() + " (3.11+ required)",
        ),
        Check("git", "pass" if git else "warn", "available" if git else "not found"),
        Check(
            "ffmpeg",
            "pass" if ffmpeg else "info",
            "available" if ffmpeg else "optional; faster-whisper decodes through PyAV",
        ),
    ]
    for module, feature in MODULES.items():
        installed = importlib.util.find_spec(module) is not None
        optional = module == "mlx_whisper"
        checks.append(
            Check(
                module,
                "pass" if installed else ("info" if optional else "warn"),
                f"installed for {feature}" if installed else f"not installed ({feature})",
            )
        )
    env = read_env(env_file)
    checks.append(Check("env_file", "pass" if env_file.is_file() else "info", str(env_file)))
    for name in (
        "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_TEST_CHAT_ID",
        "TELEGRAM_PRODUCTION_CHAT_ID",
    ):
        checks.append(
            Check(
                name,
                "pass" if env.get(name) else "info",
                "configured" if env.get(name) else "not configured",
            )
        )
    return checks


def telegram_checks(env_file: Path) -> list[Check]:
    env = read_env(env_file)
    token = env.get("TELEGRAM_BOT_TOKEN", "")
    if not token:
        return [Check("telegram", "fail", "TELEGRAM_BOT_TOKEN is not configured")]
    results: list[Check] = []
    base = f"https://api.telegram.org/bot{token}"
    requests = [("getMe", {})]
    test_chat = env.get("TELEGRAM_TEST_CHAT_ID", "")
    if test_chat:
        requests.append(("getChat(test)", {"chat_id": test_chat}))
    for label, payload in requests:
        method = label.split("(", 1)[0]
        try:
            body = urllib.parse.urlencode(payload).encode() if payload else None
            with urllib.request.urlopen(f"{base}/{method}", data=body, timeout=15) as response:
                parsed = json.loads(response.read().decode("utf-8"))
            results.append(
                Check(
                    label,
                    "pass" if parsed.get("ok") else "fail",
                    "API reachable" if parsed.get("ok") else "API rejected request",
                )
            )
        except Exception as exc:  # noqa: BLE001
            results.append(Check(label, "fail", f"{type(exc).__name__}: request failed"))
    return results


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check installation without exposing secrets")
    parser.add_argument("--env-file", type=Path, default=ROOT / ".env")
    parser.add_argument(
        "--telegram", action="store_true", help="run read-only getMe/getChat API checks"
    )
    parser.add_argument("--json", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    checks = local_checks(args.env_file)
    if args.telegram:
        checks.extend(telegram_checks(args.env_file))
    if args.json:
        print(json.dumps([asdict(item) for item in checks], ensure_ascii=False, indent=2))
    else:
        for item in checks:
            print(f"{item.status.upper():4}  {item.name}: {item.detail}")
        print("\nNo secret values were printed.")
    return 1 if any(item.status == "fail" for item in checks) else 0


if __name__ == "__main__":
    raise SystemExit(main())
