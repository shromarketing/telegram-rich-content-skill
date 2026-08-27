# Troubleshooting

## `chat not found`

Check in order:

1. The bot is an administrator of the target channel.
2. It has **Post Messages** permission.
3. A private channel ID includes the Bot API `-100...` prefix.
4. A public channel uses the exact `@username`.
5. The `.env` selected by the command is the intended one.

## `Unauthorized`

The token is invalid, revoked, copied with whitespace, or loaded from the wrong `.env`. Verify it locally with `getMe`. Never print the full token.

## Validation reports missing or unused media IDs

Every markup reference such as `tg://photo?id=cover` requires one declared `cover` media item. Remove unused declarations and provide every referenced item.

## Telegram returns a vague `BAD_REQUEST`

Common causes:

- media embedded inside a paragraph instead of a separate block;
- unsupported HTML tag or named entity;
- a local path passed as a URL instead of uploaded as a file;
- more than 32768 text characters, 500 blocks, 16 nesting levels, 50 media files, or 20 table columns;
- media type does not match the `tg://photo`, `tg://video`, `tg://audio`, or `tg://document` reference;
- malformed HTML.

Run `scripts/validate_rich.py` before retrying the network call.

## `message is not supported`

The reader's Telegram client is too old for Rich Messages. Choose one of:

- a classic album for maximum compatibility;
- a normal summary message linking to the rich version;
- an accepted audience limitation after testing.

## Album caption is truncated

Classic album captions are much shorter than Rich Messages. Move the long text into a separate message or use a Rich Message.

## `show_caption_above_media must be the same for all messages`

For `sendMediaGroup`, set `show_caption_above_media` to the same value on every album item even when only the first item carries the caption.

## Post is going to the wrong place

Stop before retrying. Inspect:

- `--environment`;
- `TELEGRAM_TEST_CHAT_ID` and `TELEGRAM_PRODUCTION_CHAT_ID` without exposing tokens;
- the exact value supplied to `--confirm-target`.

The publisher refuses to send unless confirmation and configured target match exactly.

## YouTube thumbnail or captions time out

Do not loop indefinitely. Confirm the public page works, update `yt-dlp`, and try one focused retry. If access is restricted, report the limitation rather than adding cookies or changing network identity without authorization.

## Audio extraction fails

Install `ffmpeg` and verify `ffmpeg -version`. The YouTube helper can retrieve thumbnails and metadata without it, but audio conversion and subtitle conversion may require it.

## First transcription downloads a model

This is expected. `faster-whisper` downloads the selected model once and reuses its
local cache. Use `--model-dir` to choose the cache or `--local-model-only` to prohibit
downloads. The local workflow does not upload audio to a paid transcription API.

## Transcription is too slow or runs out of memory

Start with the `small` model. On CPU, try:

```bash
python scripts/transcribe_audio.py audio.mp3 --out transcript.txt \
  --device cpu --compute-type int8
```

Use `large-v3` only when the machine has enough time and memory. On a supported NVIDIA
setup, use `--device cuda --compute-type float16`. Apple Silicon users may choose the
optional MLX path documented in `youtube-workflow.md`.

## Transcription omits speech or mishandles names

The built-in VAD removes silence and can occasionally be too aggressive. Retry a known
problem file with `--no-vad`. Supply names and specialist vocabulary through
`--initial-prompt`; verify uncertain names against the audio before quoting them.

## Flood control

Respect Telegram retry information. Do not rapidly repeat sends. For bulk work, use a queue and rate limiting; keep production publishing outside a blind retry loop.
