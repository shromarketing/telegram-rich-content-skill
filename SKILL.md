---
name: telegram-rich-content
description: "Turn a raw thought, voice note, article, document, interview, podcast, or video into a structured Telegram post in the user's tone of voice; validate and safely publish Telegram Rich Messages when requested. Use for Telegram copywriting, content repurposing, onboarding a channel voice, BotFather setup, YouTube assets, or local transcription."
---

# Telegram Rich Content

Act as a Telegram editor and copywriter: preserve the source meaning, shape it for a defined audience, apply the user's approved voice, and use rich formatting only when it improves comprehension.

Choose the lightest delivery path that satisfies the request:

1. a normal Telegram post or manual **Article** when a human publishes occasionally;
2. a classic album when compatibility matters most;
3. Bot API `sendRichMessage` when headings, tables, collapsible blocks, footnotes, or a true slideshow materially improve the post.

Do not assume that rich formatting or a bot is required. Read [references/workflow.md](references/workflow.md) before producing a full post.

## Start from any useful source

- raw typed notes or an unstructured idea;
- a voice note, podcast, meeting recording, or local audio file;
- an article URL, document, or pasted text;
- the user's own video or a lawful third-party video;
- several sources that must be reconciled.

For mode-specific extraction rules, read [references/source-modes.md](references/source-modes.md). For YouTube assets and local transcription, read [references/youtube-workflow.md](references/youtube-workflow.md).

## First-use onboarding and voice

When no editorial profile exists, read [references/onboarding.md](references/onboarding.md). Offer a short setup and create a project-local voice profile from [assets/voice-profile.template.md](assets/voice-profile.template.md) only with the user's approval.

Do not block an urgent draft on optional onboarding. State reasonable assumptions and continue. Ask a question only when the answer can materially change factual meaning, audience, format, call to action, legal risk, or publication target.

Treat the voice profile as editable evidence, not a personality diagnosis. Learn from 3–5 user-approved examples when available. Do not reveal private profiles in the post or impersonate a third party.

## Safety boundary

- Treat bot tokens, private chat IDs, cookies, voice profiles, and unpublished source material as sensitive.
- Keep Telegram secrets only in a local `.env` excluded from Git. Never paste them into prompts, screenshots, commits, or logs.
- Local transcription uses `faster-whisper`; it requires no paid API key. Model files download on first use unless a local model path is supplied.
- Default to validation and a private test channel. A successful test is not permission to publish to production.
- Before creating a bot, adding it as an administrator, changing channel rights, sending a post, or downloading protected media, obtain explicit authorization for that action.
- Grant the bot only **Post Messages** unless the user has a separate need.
- Do not bypass DRM, paywalls, private access, age gates, or platform safety controls.

## Route by task

- First setup, voice profile, and recommended extensions: [references/onboarding.md](references/onboarding.md).
- Input-specific extraction and editorial decisions: [references/source-modes.md](references/source-modes.md).
- Installation in Codex or Claude Code: [references/installation.md](references/installation.md).
- BotFather, channel permissions, environment variables, and first test: [references/botfather-setup.md](references/botfather-setup.md).
- Supported Rich HTML/Markdown and media IDs: [references/formatting.md](references/formatting.md).
- YouTube thumbnails, captions, audio, and free local transcription: [references/youtube-workflow.md](references/youtube-workflow.md).
- End-to-end production and acceptance: [references/workflow.md](references/workflow.md).
- Telegram, YouTube, or transcription errors: [references/troubleshooting.md](references/troubleshooting.md).

## Required working pattern

1. Identify the source, intended audience, goal, and requested deliverable: draft, private test, or production publication.
2. If essential information is missing, ask only the smallest set of consequential questions. Otherwise state assumptions and continue.
3. Extract an evidence map before writing. Keep claims tied to supplied sources; do not invent facts, quotations, or timestamps.
4. Load the approved voice profile and examples when provided. Preserve meaning over stylistic imitation.
5. Propose or create the post with a strong hook, readable structure, appropriate depth, one clear action, and a source/credit footer when needed.
6. Select normal post, manual Article, album, or Rich Message based on content and audience compatibility.
7. For Rich HTML, run `scripts/validate_rich.py`. For bot delivery, `scripts/publish_rich.py` validates by default and sends only with `--send` plus an exact `--confirm-target`.
8. Send to a private test channel only after approval. Review on current Telegram Desktop and mobile and choose an older-client fallback.
9. Publish to production only after approval of the exact text, media, bot, and target immediately before sending.

## Media invariant

A reference such as `tg://photo?id=cover` must have exactly one matching media item with ID `cover`. Every declared media ID must be used. IDs contain 1–64 characters from `A-Z`, `a-z`, `0-9`, `_`, and `-`.

Prefer local files for stable publishing. Public HTTP(S) media URLs are acceptable when durable and verified. Never pass a local path as a plain URL string; upload it as a file.

## Acceptance

- source meaning, facts, quotations, links, and credits are checked;
- the result follows the approved voice without exposing private profile content;
- Rich markup validates without a network call;
- secrets are absent from tracked files and command output;
- the target shown to the user matches the configured target;
- a private test renders correctly on mobile and desktop;
- a fallback is chosen for clients that do not support Rich Messages;
- production publication has separate, current approval.
