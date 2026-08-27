#!/usr/bin/env python3
"""Validate by default; publish a Telegram Rich Message only with explicit gates."""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

from validate_rich import MediaSpec, is_http_url, parse_media_spec, validate_rich

ROOT = Path(__file__).resolve().parent.parent
ENV_TARGETS = {
    "test": "TELEGRAM_TEST_CHAT_ID",
    "production": "TELEGRAM_PRODUCTION_CHAT_ID",
}


def typed_media(kind: str):
    return lambda value: parse_media_spec(value, kind=kind)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate or explicitly publish Telegram Rich HTML"
    )
    parser.add_argument("markup", type=Path, help="UTF-8 Rich HTML file")
    parser.add_argument("--photo", action="append", default=[], type=typed_media("photo"))
    parser.add_argument("--video", action="append", default=[], type=typed_media("video"))
    parser.add_argument("--audio", action="append", default=[], type=typed_media("audio"))
    parser.add_argument("--document", action="append", default=[], type=typed_media("document"))
    parser.add_argument(
        "--environment",
        choices=("test", "production"),
        default="test",
        help="select the target variable; default: test",
    )
    parser.add_argument("--env-file", type=Path, default=ROOT / ".env")
    parser.add_argument("--send", action="store_true", help="perform the network send")
    parser.add_argument(
        "--confirm-target",
        help="must exactly match the configured target when --send is used",
    )
    return parser


def all_media(args: argparse.Namespace) -> list[MediaSpec]:
    return [*args.photo, *args.video, *args.audio, *args.document]


def file_or_url(source: str):
    from aiogram.types import FSInputFile

    return source if is_http_url(source) else FSInputFile(Path(source).expanduser())


def input_media(item: MediaSpec):
    from aiogram.types import (
        InputMediaAudio,
        InputMediaDocument,
        InputMediaPhoto,
        InputMediaVideo,
    )

    classes = {
        "photo": InputMediaPhoto,
        "video": InputMediaVideo,
        "audio": InputMediaAudio,
        "document": InputMediaDocument,
    }
    assert item.kind is not None
    return classes[item.kind](media=file_or_url(item.source))


async def send(args: argparse.Namespace, markup: str, media: list[MediaSpec]) -> None:
    from aiogram import Bot
    from aiogram.types import InputRichMessage, InputRichMessageMedia
    from dotenv import load_dotenv

    if not args.env_file.is_file():
        raise ValueError(f"env file not found: {args.env_file}")
    load_dotenv(args.env_file, override=True)

    target_name = ENV_TARGETS[args.environment]
    target = (os.getenv(target_name) or "").strip()
    token = (os.getenv("TELEGRAM_BOT_TOKEN") or "").strip()
    if not target:
        raise ValueError(f"{target_name} is not set in {args.env_file}")
    if not token:
        raise ValueError(f"TELEGRAM_BOT_TOKEN is not set in {args.env_file}")
    if args.confirm_target != target:
        raise ValueError(
            "target confirmation failed: --confirm-target must exactly match "
            f"the configured {args.environment} target"
        )

    rich = InputRichMessage(
        html=markup,
        media=[InputRichMessageMedia(id=item.media_id, media=input_media(item)) for item in media],
    )
    bot = Bot(token)
    try:
        message = await bot.send_rich_message(target, rich)
        print(
            f"SENT: environment={args.environment} "
            f"chat={message.chat.id} message_id={message.message_id}"
        )
    finally:
        await bot.session.close()


def main() -> int:
    args = build_parser().parse_args()
    if not args.markup.is_file():
        print(f"ERROR: markup file not found: {args.markup}", file=sys.stderr)
        return 2
    markup = args.markup.read_text(encoding="utf-8").strip()
    media = all_media(args)
    result = validate_rich(markup, media)
    for warning in result.warnings:
        print(f"WARNING: {warning}")
    if not result.ok:
        for error in result.errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"VALID: {result.text_chars} chars, {result.blocks} blocks, {result.media_count} media.")
    if not args.send:
        print("Nothing sent. Add --send and exact --confirm-target only after approval.")
        return 0
    try:
        asyncio.run(send(args, markup, media))
    except Exception as exc:  # noqa: BLE001 - CLI boundary must return a clean error.
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
