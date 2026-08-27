#!/usr/bin/env python3
"""Transcribe local audio with free, on-device Whisper runtimes."""

from __future__ import annotations

import argparse
import importlib
import importlib.util
import json
import platform
import sys
from collections.abc import Iterable
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Protocol

FORMATS = {"txt", "md", "srt", "vtt", "json"}


class SegmentLike(Protocol):
    start: float
    end: float
    text: str


@dataclass
class Word:
    start: float | None
    end: float | None
    word: str
    probability: float | None = None


@dataclass
class Segment:
    start: float
    end: float
    text: str
    words: list[Word] = field(default_factory=list)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Transcribe locally. No API key or paid transcription service is used."
    )
    parser.add_argument("audio", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument(
        "--format",
        choices=sorted(FORMATS),
        help="default: infer from --out, otherwise txt",
    )
    parser.add_argument(
        "--backend", choices=("auto", "faster-whisper", "mlx-whisper"), default="auto"
    )
    parser.add_argument("--language", help="ISO-639-1 hint, for example ru or en")
    parser.add_argument(
        "--model",
        default="small",
        help="model name or local model path (default: small)",
    )
    parser.add_argument("--device", default="auto", choices=("auto", "cpu", "cuda"))
    parser.add_argument(
        "--compute-type",
        default="default",
        help="for example int8, float16, or default",
    )
    parser.add_argument("--beam-size", type=int, default=5)
    parser.add_argument("--timestamps", action="store_true", help="include timestamps in txt/md")
    parser.add_argument(
        "--word-timestamps",
        action="store_true",
        help="include words in JSON/checkpoint",
    )
    parser.add_argument(
        "--semantic-block-seconds",
        type=float,
        default=45.0,
        help="target block duration for Markdown; 0 disables",
    )
    parser.add_argument("--no-vad", action="store_true")
    parser.add_argument("--initial-prompt", help="names and domain vocabulary")
    parser.add_argument("--model-dir", type=Path)
    parser.add_argument("--local-model-only", action="store_true")
    parser.add_argument("--checkpoint", type=Path, help="JSONL progress file")
    parser.add_argument("--resume", action="store_true", help="resume from --checkpoint")
    return parser


def format_timestamp(seconds: float, *, srt: bool = False) -> str:
    milliseconds = max(0, round(seconds * 1000))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    whole_seconds, millis = divmod(remainder, 1000)
    separator = "," if srt else "."
    return f"{hours:02d}:{minutes:02d}:{whole_seconds:02d}{separator}{millis:03d}"


def normalize_segments(segments: Iterable[SegmentLike]) -> list[Segment]:
    normalized: list[Segment] = []
    for item in segments:
        text = item.text.strip()
        if not text:
            continue
        words = [
            Word(
                getattr(word, "start", None),
                getattr(word, "end", None),
                getattr(word, "word", "").strip(),
                getattr(word, "probability", None),
            )
            for word in (getattr(item, "words", None) or [])
        ]
        normalized.append(Segment(float(item.start), float(item.end), text, words))
    return normalized


def semantic_blocks(segments: list[Segment], target_seconds: float) -> list[list[Segment]]:
    if target_seconds <= 0:
        return [[item] for item in segments]
    blocks: list[list[Segment]] = []
    current: list[Segment] = []
    start = 0.0
    for item in segments:
        if not current:
            start = item.start
        current.append(item)
        if item.end - start >= target_seconds and item.text.rstrip().endswith((".", "!", "?", "…")):
            blocks.append(current)
            current = []
    if current:
        blocks.append(current)
    return blocks


def render_transcript(segments: Iterable[SegmentLike], *, timestamps: bool = False) -> str:
    normalized = normalize_segments(segments)
    lines = []
    for item in normalized:
        prefix = (
            f"[{format_timestamp(item.start)} --> {format_timestamp(item.end)}] "
            if timestamps
            else ""
        )
        lines.append(prefix + item.text)
    return "\n\n".join(lines).rstrip() + ("\n" if lines else "")


def render(
    segments: list[Segment],
    output_format: str,
    *,
    timestamps: bool,
    block_seconds: float,
) -> str:
    if output_format == "json":
        return json.dumps([asdict(item) for item in segments], ensure_ascii=False, indent=2) + "\n"
    if output_format in {"srt", "vtt"}:
        lines = ["WEBVTT", ""] if output_format == "vtt" else []
        for index, item in enumerate(segments, start=1):
            if output_format == "srt":
                lines.append(str(index))
            stamp = f"{format_timestamp(item.start, srt=output_format == 'srt')} --> {format_timestamp(item.end, srt=output_format == 'srt')}"
            lines.extend([stamp, item.text, ""])
        return "\n".join(lines).rstrip() + "\n"
    if output_format == "md":
        blocks = []
        for block in semantic_blocks(segments, block_seconds):
            body = " ".join(item.text for item in block)
            prefix = f"**[{format_timestamp(block[0].start)}]** " if timestamps else ""
            blocks.append(prefix + body)
        return "\n\n".join(blocks).rstrip() + ("\n" if blocks else "")
    return render_transcript(segments, timestamps=timestamps)


def load_checkpoint(path: Path) -> list[Segment]:
    if not path.is_file():
        return []
    items: list[Segment] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        raw = json.loads(line)
        raw["words"] = [Word(**word) for word in raw.get("words", [])]
        items.append(Segment(**raw))
    return items


def collect_with_checkpoint(
    raw_segments: Iterable[SegmentLike] | Iterable[Segment],
    *,
    existing: list[Segment],
    checkpoint: Path | None,
    append: bool,
) -> list[Segment]:
    """Normalize and persist each completed segment so interruptions are resumable."""
    output = list(existing)
    handle = None
    if checkpoint:
        checkpoint.parent.mkdir(parents=True, exist_ok=True)
        handle = checkpoint.open("a" if append else "w", encoding="utf-8")
    try:
        for raw in raw_segments:
            items = [raw] if isinstance(raw, Segment) else normalize_segments([raw])
            for item in items:
                if output and item.end <= output[-1].end + 0.01:
                    continue
                output.append(item)
                if handle:
                    handle.write(json.dumps(asdict(item), ensure_ascii=False) + "\n")
                    handle.flush()
    finally:
        if handle:
            handle.close()
    return output


def choose_backend(requested: str) -> str:
    if requested != "auto":
        return requested
    apple = platform.system() == "Darwin" and platform.machine() == "arm64"
    if apple and importlib.util.find_spec("mlx_whisper") is not None:
        try:
            importlib.import_module("mlx_whisper")
        except Exception:  # noqa: BLE001 - optional backend may lack a Metal device.
            return "faster-whisper"
        return "mlx-whisper"
    return "faster-whisper"


def transcribe_faster(
    args: argparse.Namespace, start_at: float
) -> tuple[Iterable[SegmentLike], object]:
    from faster_whisper import WhisperModel

    model = WhisperModel(
        args.model,
        device=args.device,
        compute_type=args.compute_type,
        download_root=str(args.model_dir) if args.model_dir else None,
        local_files_only=args.local_model_only,
    )
    kwargs = {
        "language": args.language,
        "beam_size": args.beam_size,
        "vad_filter": not args.no_vad,
        "initial_prompt": args.initial_prompt,
        "word_timestamps": args.word_timestamps,
        "log_progress": True,
    }
    if start_at:
        kwargs["clip_timestamps"] = str(start_at)
    return model.transcribe(str(args.audio), **kwargs)


def transcribe_mlx(args: argparse.Namespace, start_at: float) -> tuple[list[Segment], object]:
    import mlx_whisper

    model = args.model if "/" in args.model else f"mlx-community/whisper-{args.model}"
    options = {
        "path_or_hf_repo": model,
        "language": args.language,
        "initial_prompt": args.initial_prompt,
        "word_timestamps": args.word_timestamps,
    }
    if start_at:
        options["clip_timestamps"] = str(start_at)
    result = mlx_whisper.transcribe(str(args.audio), **options)
    segments = []
    for item in result.get("segments", []):
        words = [
            Word(
                word.get("start"),
                word.get("end"),
                str(word.get("word", "")).strip(),
                word.get("probability"),
            )
            for word in item.get("words", [])
        ]
        segments.append(
            Segment(float(item["start"]), float(item["end"]), item["text"].strip(), words)
        )
    return segments, result


def main() -> int:
    args = build_parser().parse_args()
    if not args.audio.is_file():
        print(f"ERROR: audio file not found: {args.audio}", file=sys.stderr)
        return 2
    if args.beam_size < 1 or args.semantic_block_seconds < 0:
        print("ERROR: invalid numeric option", file=sys.stderr)
        return 2
    if args.resume and not args.checkpoint:
        print("ERROR: --resume requires --checkpoint", file=sys.stderr)
        return 2
    output_format = args.format or args.out.suffix.lower().lstrip(".") or "txt"
    if output_format not in FORMATS:
        print(
            f"ERROR: cannot infer output format from {args.out}; use --format",
            file=sys.stderr,
        )
        return 2

    existing: list[Segment] = []
    try:
        if args.resume and args.checkpoint:
            existing = load_checkpoint(args.checkpoint)
        start_at = existing[-1].end if existing else 0.0
        backend = choose_backend(args.backend)
        raw_segments, info = (
            transcribe_mlx(args, start_at)
            if backend == "mlx-whisper"
            else transcribe_faster(args, start_at)
        )
        segments = collect_with_checkpoint(
            raw_segments,
            existing=existing,
            checkpoint=args.checkpoint,
            append=args.resume,
        )
        transcript = render(
            segments,
            output_format,
            timestamps=args.timestamps,
            block_seconds=args.semantic_block_seconds,
        )
    except ImportError:
        requirement = (
            "requirements-apple-silicon.txt"
            if choose_backend(args.backend) == "mlx-whisper"
            else "requirements-transcription.txt"
        )
        print(
            f"ERROR: backend is not installed. Run: python -m pip install -r {requirement}",
            file=sys.stderr,
        )
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(transcript, encoding="utf-8")
    detected = info.get("language") if isinstance(info, dict) else getattr(info, "language", None)
    probability = None if isinstance(info, dict) else getattr(info, "language_probability", None)
    if detected and isinstance(probability, (int, float)):
        print(f"Detected language: {detected} ({probability:.3f})")
    elif detected:
        print(f"Detected language: {detected}")
    print(f"Backend: {backend}")
    print(f"Transcript saved: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
