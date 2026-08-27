#!/usr/bin/env python3
"""Transcribe local audio with OpenAI; split long files locally with ffmpeg."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAX_DIRECT_BYTES = 24 * 1024 * 1024
CHUNK_SECONDS = 600


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Transcribe a local audio file")
    parser.add_argument("audio", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--language", help="ISO-639-1 hint, for example ru or en")
    parser.add_argument("--model", default="gpt-4o-mini-transcribe")
    parser.add_argument("--env-file", type=Path, default=ROOT / ".env")
    return parser


def audio_duration(path: Path) -> float | None:
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        return None
    completed = subprocess.run(
        [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode:
        return None
    try:
        return float(completed.stdout.strip())
    except ValueError:
        return None


def split_audio(path: Path, target_dir: Path) -> list[Path]:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg is required to split this long or large audio file")
    pattern = target_dir / "chunk-%03d.mp3"
    completed = subprocess.run(
        [
            ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(path),
            "-f",
            "segment",
            "-segment_time",
            str(CHUNK_SECONDS),
            "-c:a",
            "libmp3lame",
            "-b:a",
            "64k",
            str(pattern),
        ],
        check=False,
    )
    if completed.returncode:
        raise RuntimeError("ffmpeg could not split the audio")
    chunks = sorted(target_dir.glob("chunk-*.mp3"))
    if not chunks:
        raise RuntimeError("ffmpeg produced no chunks")
    return chunks


def transcribe_one(client, path: Path, *, model: str, language: str | None) -> str:
    request: dict[str, object] = {"model": model, "response_format": "text"}
    if language:
        request["language"] = language
    with path.open("rb") as audio_file:
        response = client.audio.transcriptions.create(file=audio_file, **request)
    if isinstance(response, str):
        return response.strip()
    return str(getattr(response, "text", response)).strip()


def main() -> int:
    args = build_parser().parse_args()
    if not args.audio.is_file():
        print(f"ERROR: audio file not found: {args.audio}", file=sys.stderr)
        return 2

    try:
        from dotenv import load_dotenv

        load_dotenv(args.env_file, override=False)
        api_key = (os.getenv("OPENAI_API_KEY") or "").strip()
        if not api_key:
            raise RuntimeError(
                f"OPENAI_API_KEY is not configured locally in {args.env_file}; "
                "do not paste it into chat"
            )
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        duration = audio_duration(args.audio)
        requires_split = args.audio.stat().st_size > MAX_DIRECT_BYTES or (
            duration is not None and duration > CHUNK_SECONDS
        )
        if requires_split:
            with tempfile.TemporaryDirectory(
                prefix="telegram-rich-transcribe-"
            ) as temp:
                chunks = split_audio(args.audio, Path(temp))
                texts = []
                for index, chunk in enumerate(chunks, start=1):
                    print(f"Transcribing chunk {index}/{len(chunks)}")
                    texts.append(
                        transcribe_one(
                            client,
                            chunk,
                            model=args.model,
                            language=args.language,
                        )
                    )
                transcript = "\n\n".join(texts)
        else:
            transcript = transcribe_one(
                client,
                args.audio,
                model=args.model,
                language=args.language,
            )
    except Exception as exc:  # noqa: BLE001 - API/ffmpeg errors become CLI errors.
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(transcript.rstrip() + "\n", encoding="utf-8")
    print(f"Transcript saved: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
