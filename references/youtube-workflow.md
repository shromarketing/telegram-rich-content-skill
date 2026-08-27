# YouTube to Telegram rich content

Use the smallest acquisition step that supplies the needed evidence.

## Decision order

1. Read the public title, description, chapters, and original URL.
2. Retrieve the original thumbnail and available creator-provided captions.
3. Use automatic captions if creator captions are absent and their quality is sufficient.
4. Download audio only when captions are unavailable or materially incomplete.
5. Transcribe only after the user approves the API/cost path and a local API key is configured.
6. Download full video only when representative frame selection or visual analysis truly requires it.

Do not download more data than the task requires.

## Rights and platform boundaries

- Process user-owned videos or public material the user has a lawful reason to access.
- Do not bypass DRM, private access, login barriers, paywalls, age verification, or safety interstitials.
- Do not use browser cookies by default. If authenticated access is genuinely required, stop and explain the exact data and destination before proceeding.
- For another creator's video, produce a transformative summary, credit the source, link the original, and avoid republishing a full transcript or substantial media segments.

## Original thumbnail, metadata, and captions

Install dependencies from `requirements.txt`, then run:

```bash
python scripts/prepare_youtube.py 'https://youtu.be/VIDEO_ID' \
  --thumbnail --captions --language 'ru.*,en.*' \
  --output-dir output/video
```

The helper calls `yt-dlp` without browser cookies, disables playlists by default, writes metadata, downloads available manual/automatic captions, and converts the thumbnail to JPEG when possible.

Thumbnail-only:

```bash
python scripts/prepare_youtube.py URL \
  --thumbnail --output-dir output/video
```

## Audio only

Audio extraction requires `ffmpeg`:

```bash
python scripts/prepare_youtube.py URL \
  --audio --output-dir output/video
```

The helper requests compressed MP3 suitable for transcription rather than the largest video stream.

## Transcription

Set `OPENAI_API_KEY` locally in `.env`; never paste it into a prompt.

```bash
python scripts/transcribe_audio.py output/video/source.mp3 \
  --language ru \
  --out output/video/transcript.txt
```

Default model: `gpt-4o-mini-transcribe`. Large files are split locally with `ffmpeg` before upload. Transcription uses the user's OpenAI API account and may incur cost.

If an agent environment already provides a trusted transcription skill, it may use that instead, preserving the same secret and approval boundaries.

## Selecting a frame

Only after lawful video acquisition, use `ffmpeg` for a frame:

```bash
ffmpeg -ss 00:12:34 -i video.mp4 -frames:v 1 -q:v 2 frame.jpg
```

Check the frame visually. Prefer a clear speaker expression, readable composition, and no transient overlays. Do not fabricate a screenshot with image generation and present it as a frame from the video.

## From transcript to post

Create an evidence map before writing:

- key claim;
- supporting excerpt or timestamp;
- whether it is a direct quote or paraphrase;
- visual candidate;
- uncertainty or missing context.

Do not invent quotes, chapter names, credentials, or timestamps. If automatic captions are uncertain, paraphrase cautiously or verify against audio.
