#!/usr/bin/env python3
"""Safely validate or publish classic Telegram plain/album fallbacks."""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

from publish_rich import ENV_TARGETS, ROOT, file_or_url, typed_media

MAX_MESSAGE = 4096
MAX_CAPTION = 1024


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate or explicitly send a plain post or album"
    )
    parser.add_argument("text", type=Path, help="UTF-8 text/caption file")
    parser.add_argument("--mode", choices=("plain", "album"), default="plain")
    parser.add_argument("--photo", action="append", default=[], type=typed_media("photo"))
    parser.add_argument("--video", action="append", default=[], type=typed_media("video"))
    parser.add_argument("--parse-mode", choices=("HTML", "MarkdownV2", "none"), default="none")
    parser.add_argument("--environment", choices=("test", "production"), default="test")
    parser.add_argument("--env-file", type=Path, default=ROOT / ".env")
    parser.add_argument("--send", action="store_true")
    parser.add_argument("--confirm-target")
    return parser


def validate(args: argparse.Namespace, text: str) -> list[str]:
    errors: list[str] = []
    media = [*args.photo, *args.video]
    if args.mode == "plain":
        if media:
            errors.append("plain mode does not accept media; use album")
        if len(text) > MAX_MESSAGE:
            errors.append(f"message has {len(text)} characters; limit is {MAX_MESSAGE}")
    else:
        if not 2 <= len(media) <= 10:
            errors.append("album mode requires 2–10 photos/videos")
        if len(text) > MAX_CAPTION:
            errors.append(f"caption has {len(text)} characters; limit is {MAX_CAPTION}")
    return errors


async def send(args: argparse.Namespace, text: str) -> None:
    from aiogram import Bot
    from aiogram.types import InputMediaPhoto, InputMediaVideo
    from dotenv import load_dotenv

    if not args.env_file.is_file():
        raise ValueError(f"env file not found: {args.env_file}")
    load_dotenv(args.env_file, override=True)
    target_name = ENV_TARGETS[args.environment]
    target = (os.getenv(target_name) or "").strip()
    token = (os.getenv("TELEGRAM_BOT_TOKEN") or "").strip()
    if not target or not token:
        raise ValueError(f"TELEGRAM_BOT_TOKEN and {target_name} must be configured")
    if args.confirm_target != target:
        raise ValueError("target confirmation failed")
    parse_mode = None if args.parse_mode == "none" else args.parse_mode
    bot = Bot(token)
    try:
        if args.mode == "plain":
            message = await bot.send_message(target, text, parse_mode=parse_mode)
        else:
            classes = {"photo": InputMediaPhoto, "video": InputMediaVideo}
            items = []
            for index, item in enumerate([*args.photo, *args.video]):
                items.append(
                    classes[item.kind](
                        media=file_or_url(item.source),
                        caption=text if index == 0 else None,
                        parse_mode=parse_mode if index == 0 else None,
                        show_caption_above_media=True,
                    )
                )
            messages = await bot.send_media_group(target, media=items)
            message = messages[0]
        print(
            f"SENT: environment={args.environment} chat={message.chat.id} message_id={message.message_id}"
        )
    finally:
        await bot.session.close()


def main() -> int:
    args = build_parser().parse_args()
    if not args.text.is_file():
        print(f"ERROR: text file not found: {args.text}", file=sys.stderr)
        return 2
    text = args.text.read_text(encoding="utf-8").strip()
    errors = validate(args, text)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"VALID: {args.mode}, {len(text)} chars, {len(args.photo) + len(args.video)} media")
    if not args.send:
        print("Nothing sent. Add --send and exact --confirm-target only after approval.")
        return 0
    try:
        asyncio.run(send(args, text))
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
