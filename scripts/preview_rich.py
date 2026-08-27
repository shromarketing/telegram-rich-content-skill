#!/usr/bin/env python3
"""Build an approximate, offline browser preview of Telegram Rich HTML."""

from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

MEDIA_RE = re.compile(
    r'<(?:img|video|audio|tg-document)\b[^>]*src=["\']tg://[^"\']+["\'][^>]*?(?:/>|>.*?</(?:video|audio|tg-document)>)',
    re.IGNORECASE | re.DOTALL,
)
SHELL = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Telegram Rich Content — approximate preview</title>
<style>
:root{color-scheme:dark;--bg:#0b1020;--card:#17212b;--text:#f5f7fb;--muted:#9fb0c2;--accent:#2aabee}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at 20% 0,#17365b 0,transparent 42%),var(--bg);font:16px/1.55 Inter,system-ui,sans-serif;color:var(--text)}
main{width:min(760px,calc(100% - 32px));margin:48px auto}.notice{color:var(--muted);font-size:13px;margin:0 0 12px}.card{background:var(--card);border:1px solid #294056;border-radius:22px;padding:28px;box-shadow:0 24px 80px #0008}
h1,h2,h3{line-height:1.12;margin:1.3em 0 .45em}h1:first-child{margin-top:0}a{color:#63c4f5}blockquote{border-left:4px solid var(--accent);margin:20px 0;padding:10px 16px;background:#0f1a25;border-radius:0 12px 12px 0}
table{width:100%;border-collapse:collapse;margin:20px 0}th,td{border:1px solid #3a5064;padding:10px;text-align:left}details,aside{display:block;background:#101b26;padding:14px;border-radius:12px;margin:16px 0}.media{display:grid;place-items:center;min-height:180px;border:1px dashed #557087;border-radius:16px;color:var(--muted);background:#0e1822;margin:18px 0}footer{color:var(--muted);border-top:1px solid #33495c;margin-top:24px;padding-top:16px}tg-button-row{display:flex;gap:8px;margin-top:16px}tg-button{background:var(--accent);padding:10px 16px;border-radius:10px;font-weight:700}
</style></head><body><main><p class="notice">Approximate local preview — verify the final result in Telegram Desktop and mobile.</p><article class="card">{{CONTENT}}</article></main></body></html>
"""


def render(markup: str) -> str:
    safe = re.sub(
        r"<(script|style)\b.*?</\1>",
        lambda match: html.escape(match.group(0)),
        markup,
        flags=re.IGNORECASE | re.DOTALL,
    )
    safe = MEDIA_RE.sub('<div class="media">Telegram media placeholder</div>', safe)
    return SHELL.replace("{{CONTENT}}", safe)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create an approximate offline Rich HTML preview")
    parser.add_argument("markup", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if not args.markup.is_file():
        print(f"ERROR: markup file not found: {args.markup}", file=sys.stderr)
        return 2
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(render(args.markup.read_text(encoding="utf-8")), encoding="utf-8")
    print(f"Approximate preview saved: {args.out.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
