#!/usr/bin/env python3
"""Acquire only requested public YouTube assets through yt-dlp."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse


def public_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise argparse.ArgumentTypeError("expected an HTTP(S) video URL")
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Download selected public YouTube assets without cookies or playlists"
    )
    parser.add_argument("url", type=public_url)
    parser.add_argument("--output-dir", type=Path, default=Path("output/youtube"))
    parser.add_argument("--thumbnail", action="store_true", help="write original thumbnail")
    parser.add_argument("--captions", action="store_true", help="write manual and auto captions")
    parser.add_argument("--audio", action="store_true", help="extract compressed MP3 audio")
    parser.add_argument(
        "--language",
        default="ru.*,en.*",
        help="yt-dlp subtitle language expression",
    )
    return parser


def build_command(args: argparse.Namespace) -> list[str]:
    output_template = str(args.output_dir / "%(id)s.%(ext)s")
    command = [
        sys.executable,
        "-m",
        "yt_dlp",
        "--ignore-config",
        "--no-playlist",
        "--no-overwrites",
        "--write-info-json",
        "--output",
        output_template,
    ]
    if not args.audio:
        command.append("--skip-download")
    if args.thumbnail:
        command.extend(["--write-thumbnail", "--convert-thumbnails", "jpg"])
    if args.captions:
        command.extend(
            [
                "--write-subs",
                "--write-auto-subs",
                "--sub-langs",
                args.language,
                "--sub-format",
                "vtt/best",
            ]
        )
    if args.audio:
        command.extend(
            [
                "--extract-audio",
                "--audio-format",
                "mp3",
                "--audio-quality",
                "9",
            ]
        )
    command.append(args.url)
    return command


def main() -> int:
    args = build_parser().parse_args()
    if not any((args.thumbnail, args.captions, args.audio)):
        print(
            "ERROR: choose --thumbnail, --captions, --audio, or a combination",
            file=sys.stderr,
        )
        return 2
    args.output_dir.mkdir(parents=True, exist_ok=True)
    command = build_command(args)
    print(
        f"Preparing public assets without cookies or playlist expansion. Output: {args.output_dir}"
    )
    try:
        completed = subprocess.run(command, check=False)
    except OSError as exc:
        print(f"ERROR: could not start yt-dlp: {exc}", file=sys.stderr)
        return 1
    if completed.returncode:
        print(
            "ERROR: yt-dlp failed. Do not add cookies or bypass access controls "
            "without explicit authorization.",
            file=sys.stderr,
        )
        return completed.returncode
    files = sorted(path.name for path in args.output_dir.iterdir() if path.is_file())
    print("Created or retained:")
    for name in files:
        print(f"- {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
