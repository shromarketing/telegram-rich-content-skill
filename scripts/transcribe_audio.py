#!/usr/bin/env python3
"""Transcribe a local audio file with the open-source faster-whisper runtime."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Protocol


class SegmentLike(Protocol):
    start: float
    end: float
    text: str


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Transcribe local audio with faster-whisper. No API key or paid "
            "transcription service is used."
        )
    )
    parser.add_argument("audio", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--language", help="ISO-639-1 hint, for example ru or en")
    parser.add_argument(
        "--model",
        default="small",
        help="Whisper model name or local model path (default: small)",
    )
    parser.add_argument(
        "--device",
        default="auto",
        choices=("auto", "cpu", "cuda"),
        help="inference device (default: auto)",
    )
    parser.add_argument(
        "--compute-type",
        default="default",
        help="CTranslate2 compute type, for example int8, float16, or default",
    )
    parser.add_argument("--beam-size", type=int, default=5)
    parser.add_argument(
        "--timestamps",
        action="store_true",
        help="prefix every segment with start and end timestamps",
    )
    parser.add_argument(
        "--no-vad",
        action="store_true",
        help="disable the built-in Silero voice activity filter",
    )
    parser.add_argument(
        "--initial-prompt",
        help="optional vocabulary/context hint with names and domain terms",
    )
    parser.add_argument(
        "--model-dir",
        type=Path,
        help="directory for downloaded model files",
    )
    parser.add_argument(
        "--local-model-only",
        action="store_true",
        help="fail instead of downloading missing model files",
    )
    return parser


def format_timestamp(seconds: float) -> str:
    milliseconds = max(0, round(seconds * 1000))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    whole_seconds, millis = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{whole_seconds:02d}.{millis:03d}"


def render_transcript(
    segments: Iterable[SegmentLike], *, timestamps: bool = False
) -> str:
    lines: list[str] = []
    for segment in segments:
        text = segment.text.strip()
        if not text:
            continue
        if timestamps:
            start = format_timestamp(segment.start)
            end = format_timestamp(segment.end)
            lines.append(f"[{start} --> {end}] {text}")
        else:
            lines.append(text)
    return "\n\n".join(lines).rstrip() + ("\n" if lines else "")


def main() -> int:
    args = build_parser().parse_args()
    if not args.audio.is_file():
        print(f"ERROR: audio file not found: {args.audio}", file=sys.stderr)
        return 2
    if args.beam_size < 1:
        print("ERROR: --beam-size must be at least 1", file=sys.stderr)
        return 2

    try:
        from faster_whisper import WhisperModel

        model = WhisperModel(
            args.model,
            device=args.device,
            compute_type=args.compute_type,
            download_root=str(args.model_dir) if args.model_dir else None,
            local_files_only=args.local_model_only,
        )
        segments, info = model.transcribe(
            str(args.audio),
            language=args.language,
            beam_size=args.beam_size,
            vad_filter=not args.no_vad,
            initial_prompt=args.initial_prompt,
            log_progress=True,
        )
        transcript = render_transcript(segments, timestamps=args.timestamps)
    except ImportError:
        print(
            "ERROR: faster-whisper is not installed. Run: "
            "python -m pip install -r requirements-youtube.txt",
            file=sys.stderr,
        )
        return 1
    except Exception as exc:  # noqa: BLE001 - runtime/model errors become CLI errors.
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(transcript, encoding="utf-8")
    detected = getattr(info, "language", None)
    probability = getattr(info, "language_probability", None)
    if detected and isinstance(probability, (int, float)):
        print(f"Detected language: {detected} ({probability:.3f})")
    elif detected:
        print(f"Detected language: {detected}")
    print(f"Transcript saved: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
