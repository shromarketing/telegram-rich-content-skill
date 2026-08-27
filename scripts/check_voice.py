#!/usr/bin/env python3
"""Deterministic editorial checks; never pretends to measure a person's voice."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

EMOJI_RE = re.compile("[\U0001f1e6-\U0001f1ff\U0001f300-\U0001faff\u2600-\u27bf]")
SENTENCE_RE = re.compile(r"[^.!?…]+[.!?…]?")


@dataclass
class Finding:
    level: str
    rule: str
    detail: str


def check_text(text: str, config: dict[str, object]) -> list[Finding]:
    findings: list[Finding] = []
    lowered = text.casefold()
    for phrase in config.get("banned_phrases", []):
        if str(phrase).casefold() in lowered:
            findings.append(Finding("FAIL", "banned_phrase", repr(str(phrase))))
    for phrase in config.get("required_phrases", []):
        if str(phrase).casefold() not in lowered:
            findings.append(Finding("FAIL", "required_phrase", f"missing {phrase!r}"))

    max_paragraph = int(config.get("max_paragraph_chars", 0) or 0)
    if max_paragraph:
        for index, paragraph in enumerate(re.split(r"\n\s*\n", text), start=1):
            if len(paragraph.strip()) > max_paragraph:
                findings.append(
                    Finding(
                        "WARN",
                        "paragraph_length",
                        f"paragraph {index}: {len(paragraph.strip())} chars > {max_paragraph}",
                    )
                )

    max_sentence_words = int(config.get("max_sentence_words", 0) or 0)
    if max_sentence_words:
        for index, sentence in enumerate(SENTENCE_RE.findall(text), start=1):
            words = re.findall(r"\b[\w'-]+\b", sentence, flags=re.UNICODE)
            if len(words) > max_sentence_words:
                findings.append(
                    Finding(
                        "WARN",
                        "sentence_length",
                        f"sentence {index}: {len(words)} words > {max_sentence_words}",
                    )
                )

    emoji_count = len(EMOJI_RE.findall(text))
    max_emoji = int(config.get("max_emoji", 0) or 0)
    if max_emoji and emoji_count > max_emoji:
        findings.append(Finding("WARN", "emoji_count", f"{emoji_count} > {max_emoji}"))

    if config.get("require_call_to_action"):
        markers = [str(item).casefold() for item in config.get("call_to_action_markers", [])]
        if not any(marker in lowered for marker in markers):
            findings.append(Finding("WARN", "call_to_action", "no configured CTA marker found"))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Run explainable tone-of-voice guardrails")
    parser.add_argument("text", type=Path)
    parser.add_argument("--profile", type=Path, required=True, help="JSON editorial rules")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.text.is_file() or not args.profile.is_file():
        print("ERROR: text and profile files must exist", file=sys.stderr)
        return 2
    try:
        config = json.loads(args.profile.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: invalid profile: {exc}", file=sys.stderr)
        return 2
    findings = check_text(args.text.read_text(encoding="utf-8"), config)
    if args.json:
        print(json.dumps([finding.__dict__ for finding in findings], ensure_ascii=False, indent=2))
    elif findings:
        for finding in findings:
            print(f"{finding.level}: {finding.rule}: {finding.detail}")
    else:
        print("PASS: no configured voice guardrails were triggered")
    print("Note: this is an explainable rule check, not a subjective 'voice score'.")
    return 1 if any(item.level == "FAIL" for item in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
