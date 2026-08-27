---
name: telegram-rich-content
description: "Create, validate, and safely publish structured Telegram Rich Messages from text, articles, interviews, podcasts, or YouTube videos. Use for Telegram longreads, headings, tables, details, footnotes, slideshows, collages, BotFather setup, aiogram sendRichMessage publishing, YouTube thumbnails, captions, or transcription."
---

# Telegram Rich Content

Turn source material into a structured Telegram post and deliver it through the safest suitable path:

1. manual Telegram **Article** editor when a human with Premium publishes occasional posts;
2. classic `sendMediaGroup` album when compatibility matters most;
3. Bot API `sendRichMessage` when headings, tables, collapsible blocks, footnotes, or a true slideshow materially improve the post.

Do not assume that a bot is required. Read [references/workflow.md](references/workflow.md) and choose the lightest mode that satisfies the request.

## Safety boundary

- Treat bot tokens, chat IDs for private channels, API keys, cookies, and unpublished source material as secrets.
- Keep secrets only in a local `.env` excluded from Git. Never paste tokens into prompts, code, screenshots, commits, or logs.
- Default to validation and a private test channel. A successful test is not permission to publish to production.
- Before creating a bot, adding it as an administrator, changing channel rights, sending a post, downloading protected media, or using paid transcription, obtain the user's explicit authorization for that action.
- Grant the bot only the **Post Messages** channel permission unless the user has a separate need.
- Do not bypass DRM, paywalls, private access, age gates, or platform safety controls. Download only material the user may lawfully access and process.

## Route by task

- For BotFather, channel permissions, environment variables, and first test: read [references/botfather-setup.md](references/botfather-setup.md).
- For installation in Codex or Claude Code: read [references/installation.md](references/installation.md).
- For supported Rich HTML/Markdown and media IDs: read [references/formatting.md](references/formatting.md).
- For YouTube thumbnails, captions, audio, and transcription: read [references/youtube-workflow.md](references/youtube-workflow.md).
- For end-to-end production and acceptance: read [references/workflow.md](references/workflow.md).
- When Telegram returns an error or an old client cannot render the message: read [references/troubleshooting.md](references/troubleshooting.md).

## Required working pattern

1. Confirm the source, audience, destination, and whether publication is requested or only a draft is needed.
2. Extract facts and structure before writing. Keep claims tied to the supplied source; do not invent quotations or timestamps.
3. Select manual Article, album, or Rich Message based on complexity and audience compatibility.
4. Create the post from `assets/rich-post.example.html` or a fresh structure using the formatting reference.
5. Run `scripts/validate_rich.py` locally. Resolve every error before any network call.
6. For bot delivery, use `scripts/publish_rich.py`. It validates by default and sends only with `--send` plus an exact `--confirm-target` value.
7. Send to a private test channel first. Review on current Telegram Desktop and mobile; also decide what readers on older clients should receive.
8. Publish to production only after the user approves the exact text, media, bot, and target channel immediately before sending.

## Media invariant

A reference such as `tg://photo?id=cover` in the markup must have exactly one matching media item with ID `cover`. Every declared media ID must be used. IDs contain 1–64 characters from `A-Z`, `a-z`, `0-9`, `_`, and `-`.

Prefer local files for stable publishing. Public HTTP(S) media URLs are acceptable when the source is durable and verified. Never pass a local path as a plain URL string; upload it as a file.

## Acceptance

- validation passes without a network call;
- secrets are absent from tracked files and command output;
- the target shown to the user matches the target configured for the send;
- a private test message renders correctly on mobile and desktop;
- links, tables, details, slideshow order, captions, and notification preview are checked;
- a fallback is chosen for clients that do not support Rich Messages;
- production publication has separate, current approval.
