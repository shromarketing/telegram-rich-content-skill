#!/usr/bin/env python3
"""Offline validation for Telegram Rich HTML and declared media."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

MAX_TEXT_CHARS = 32_768
MAX_BLOCKS = 500
MAX_NESTING = 16
MAX_MEDIA = 50
MAX_TABLE_COLUMNS = 20

MEDIA_REF_RE = re.compile(
    r"tg://(?P<kind>photo|video|audio|document)\?id=(?P<id>[A-Za-z0-9_-]{1,64})"
)
MEDIA_ID_RE = re.compile(r"[A-Za-z0-9_-]{1,64}")
NAMED_ENTITY_RE = re.compile(r"&([A-Za-z][A-Za-z0-9]+);")
ALLOWED_NAMED_ENTITIES = {
    "lt",
    "gt",
    "amp",
    "quot",
    "apos",
    "nbsp",
    "hellip",
    "mdash",
    "ndash",
    "lsquo",
    "rsquo",
    "ldquo",
    "rdquo",
}

BLOCK_TAGS = {
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "p",
    "pre",
    "footer",
    "hr",
    "ul",
    "ol",
    "li",
    "blockquote",
    "aside",
    "table",
    "caption",
    "tr",
    "details",
    "tg-math-block",
    "tg-map",
    "tg-collage",
    "tg-slideshow",
    "tg-document",
    "img",
    "video",
    "audio",
}
VOID_TAGS = {"hr", "img", "input", "tg-map"}


@dataclass(frozen=True)
class MediaSpec:
    media_id: str
    source: str
    kind: str | None = None


@dataclass
class ValidationResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    text_chars: int = 0
    blocks: int = 0
    max_nesting: int = 0
    media_count: int = 0

    @property
    def ok(self) -> bool:
        return not self.errors


class RichHTMLMetrics(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.stack: list[str] = []
        self.errors: list[str] = []
        self.blocks = 0
        self.max_nesting = 0
        self.current_row_columns: int | None = None
        self.max_table_columns = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in BLOCK_TAGS:
            self.blocks += 1
        if tag == "tr":
            self.current_row_columns = 0
        elif tag in {"th", "td"} and self.current_row_columns is not None:
            raw = dict(attrs).get("colspan") or "1"
            try:
                colspan = max(1, int(raw))
            except ValueError:
                self.errors.append(f"invalid colspan={raw!r}")
                colspan = 1
            self.current_row_columns += colspan
            self.max_table_columns = max(
                self.max_table_columns, self.current_row_columns
            )

        if tag not in VOID_TAGS:
            self.stack.append(tag)
            self.max_nesting = max(self.max_nesting, len(self.stack))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        lowered = tag.lower()
        if lowered not in VOID_TAGS and self.stack and self.stack[-1] == lowered:
            self.stack.pop()

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "tr":
            self.current_row_columns = None
        if not self.stack:
            self.errors.append(f"closing tag </{tag}> has no opener")
            return
        if self.stack[-1] != tag:
            self.errors.append(
                f"closing tag </{tag}> does not match <{self.stack[-1]}>"
            )
            if tag in self.stack:
                while self.stack and self.stack[-1] != tag:
                    self.stack.pop()
                if self.stack:
                    self.stack.pop()
            return
        self.stack.pop()

    def close(self) -> None:
        super().close()
        if self.stack:
            self.errors.append(f"unclosed tags: {', '.join(self.stack)}")


def is_http_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def parse_media_spec(value: str, *, kind: str | None = None) -> MediaSpec:
    try:
        media_id, source = value.split("=", 1)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("media must use ID=PATH_OR_URL") from exc
    if not MEDIA_ID_RE.fullmatch(media_id):
        raise argparse.ArgumentTypeError("media ID must match [A-Za-z0-9_-]{1,64}")
    if not source:
        raise argparse.ArgumentTypeError("media source is empty")
    if not is_http_url(source) and not Path(source).expanduser().is_file():
        raise argparse.ArgumentTypeError(f"media file not found: {source}")
    return MediaSpec(media_id=media_id, source=source, kind=kind)


def validate_rich(
    markup: str, media: list[MediaSpec] | None = None
) -> ValidationResult:
    media = media or []
    result = ValidationResult(text_chars=len(markup), media_count=len(media))

    if len(markup) > MAX_TEXT_CHARS:
        result.errors.append(
            f"text has {len(markup)} characters; limit is {MAX_TEXT_CHARS}"
        )
    if len(media) > MAX_MEDIA:
        result.errors.append(
            f"declared media count is {len(media)}; limit is {MAX_MEDIA}"
        )

    parser = RichHTMLMetrics()
    try:
        parser.feed(markup)
        parser.close()
    except (AssertionError, ValueError) as exc:
        result.errors.append(f"HTML parser error: {exc}")
    result.blocks = parser.blocks
    result.max_nesting = parser.max_nesting
    result.errors.extend(parser.errors)

    if parser.blocks > MAX_BLOCKS:
        result.errors.append(
            f"estimated block count is {parser.blocks}; limit is {MAX_BLOCKS}"
        )
    if parser.max_nesting > MAX_NESTING:
        result.errors.append(f"nesting is {parser.max_nesting}; limit is {MAX_NESTING}")
    if parser.max_table_columns > MAX_TABLE_COLUMNS:
        result.errors.append(
            f"table row has {parser.max_table_columns} columns; limit is {MAX_TABLE_COLUMNS}"
        )

    invalid_entities = sorted(
        set(NAMED_ENTITY_RE.findall(markup)) - ALLOWED_NAMED_ENTITIES
    )
    if invalid_entities:
        result.errors.append(
            f"unsupported named HTML entities: {', '.join(invalid_entities)}"
        )

    references = [
        (match.group("kind"), match.group("id"))
        for match in MEDIA_REF_RE.finditer(markup)
    ]
    referenced_ids = {media_id for _, media_id in references}
    declared_ids = [item.media_id for item in media]
    declared_set = set(declared_ids)

    duplicates = sorted({item for item in declared_ids if declared_ids.count(item) > 1})
    if duplicates:
        result.errors.append(f"duplicate declared media IDs: {', '.join(duplicates)}")

    missing = sorted(referenced_ids - declared_set)
    unused = sorted(declared_set - referenced_ids)
    if missing:
        result.errors.append(
            f"markup references undeclared media IDs: {', '.join(missing)}"
        )
    if unused:
        result.errors.append(f"declared media IDs are unused: {', '.join(unused)}")

    expected_kind = {media_id: kind for kind, media_id in references}
    for item in media:
        if (
            item.kind
            and item.media_id in expected_kind
            and item.kind != expected_kind[item.media_id]
        ):
            result.errors.append(
                f"media {item.media_id!r} declared as {item.kind}, "
                f"but markup references {expected_kind[item.media_id]}"
            )

    if not references and media:
        result.warnings.append(
            "media was declared but no tg:// media references were found"
        )
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate Telegram Rich HTML without sending"
    )
    parser.add_argument("markup", type=Path, help="UTF-8 Rich HTML file")
    parser.add_argument(
        "--media",
        action="append",
        default=[],
        metavar="ID=PATH_OR_URL",
        help="declare media referenced by tg://...; repeat as needed",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not args.markup.is_file():
        print(f"ERROR: markup file not found: {args.markup}", file=sys.stderr)
        return 2
    try:
        media = [parse_media_spec(value) for value in args.media]
    except argparse.ArgumentTypeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    markup = args.markup.read_text(encoding="utf-8").strip()
    result = validate_rich(markup, media)
    for warning in result.warnings:
        print(f"WARNING: {warning}")
    if not result.ok:
        for error in result.errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(
        "VALID: "
        f"{result.text_chars} chars, {result.blocks} blocks, "
        f"nesting {result.max_nesting}, {result.media_count} media. Nothing sent."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
