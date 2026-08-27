#!/usr/bin/env python3
"""Read recent bot updates and display chat IDs without printing the token."""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


async def run() -> int:
    from aiogram import Bot
    from dotenv import load_dotenv

    env_file = ROOT / ".env"
    load_dotenv(env_file, override=False)
    token = (os.getenv("TELEGRAM_BOT_TOKEN") or "").strip()
    if not token:
        print(
            f"ERROR: TELEGRAM_BOT_TOKEN is not configured in {env_file}",
            file=sys.stderr,
        )
        return 1

    bot = Bot(token)
    try:
        updates = await bot.get_updates(timeout=5, limit=100)
    finally:
        await bot.session.close()

    chats: dict[int, tuple[str, str]] = {}
    for update in updates:
        candidates = [
            update.message,
            update.edited_message,
            update.channel_post,
            update.edited_channel_post,
        ]
        for message in candidates:
            if message is None:
                continue
            title = (
                message.chat.title or message.chat.username or message.chat.full_name
            )
            chats[message.chat.id] = (message.chat.type, title or "untitled")

    if not chats:
        print(
            "No recent chats found. Add the bot to the test channel, publish a harmless "
            "message there, and run this command again."
        )
        return 0
    for chat_id, (chat_type, title) in sorted(chats.items()):
        print(f"{chat_id}\t{chat_type}\t{title}")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run()))
