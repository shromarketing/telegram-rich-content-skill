# YouTube to Telegram rich content

Use the smallest acquisition step that supplies the needed evidence.

## Decision order

1. Read the public title, description, chapters, and original URL.
2. Retrieve the original thumbnail and available creator-provided captions.
3. Use automatic captions if creator captions are absent and their quality is sufficient.
4. Download audio only when captions are unavailable or materially incomplete.
5. Transcribe locally with `faster-whisper`; no paid transcription API is required.
6. Download full video only when frame selection or visual analysis truly requires it.

Do not download more data than the task requires.

## Rights and platform boundaries

- Process user-owned videos or public material the user has a lawful reason to access.
- Do not bypass DRM, private access, login barriers, paywalls, age verification, or safety interstitials.
- Do not use browser cookies by default. If authenticated access is genuinely required, stop and explain the exact data and destination before proceeding.
- For another creator's video, produce a transformative summary, credit and link the original, and avoid republishing a full transcript or substantial media segments.

## Original thumbnail, metadata, and captions

```bash
python scripts/prepare_youtube.py 'https://youtu.be/VIDEO_ID' \
  --thumbnail --captions --language 'ru.*,en.*' \
  --output-dir output/video
```

The helper calls `yt-dlp` without browser cookies, disables playlists by default, writes metadata, downloads available manual/automatic captions, and converts the thumbnail to JPEG when possible.

Thumbnail only:

```bash
python scripts/prepare_youtube.py URL \
  --thumbnail --output-dir output/video
```

## Audio only

Audio extraction through `yt-dlp` requires a local FFmpeg executable:

```bash
python scripts/prepare_youtube.py URL \
  --audio --output-dir output/video
```

## Free local transcription

Install the optional dependencies once:

```bash
python -m pip install -r requirements-youtube.txt
```

Balanced default for a typical computer:

```bash
python scripts/transcribe_audio.py output/video/source.mp3 \
  --language ru \
  --timestamps \
  --out output/video/transcript.txt
```

The default `small` model is a practical starting point. For a final transcript with enough RAM and time, try `--model large-v3`. For CPU inference, `--device cpu --compute-type int8` usually reduces memory use. For a supported NVIDIA setup, `--device cuda --compute-type float16` is the common fast path.

`faster-whisper` processes long recordings as local segments and can filter silence with Silero VAD. There is no upload-size split and no per-minute API bill. The selected model is downloaded on first use; later runs can be forced offline with `--local-model-only`. Its PyAV decoder bundles the required FFmpeg libraries, so the transcription script itself does not require a system FFmpeg installation.

Names and domain vocabulary can be supplied without sending them to an API:

```bash
python scripts/transcribe_audio.py interview.mp3 \
  --model large-v3 --language ru \
  --initial-prompt 'Роман Тарасенко, Telegram, Rich Messages' \
  --out transcript.txt
```

### Optional Apple Silicon path

On Apple Silicon, `mlx-whisper` is an optional alternative optimized for the MLX ecosystem. It is not required by this repository and its CLI differs from `scripts/transcribe_audio.py`. Install it in a separate virtual environment and follow the official MLX Whisper instructions. Keep `faster-whisper` as the portable default for Codex and Claude Code installations across operating systems.

## Selecting a frame

Only after lawful video acquisition, use FFmpeg for a frame:

```bash
ffmpeg -ss 00:12:34 -i video.mp4 -frames:v 1 -q:v 2 frame.jpg
```

Check the frame visually. Prefer a clear speaker expression and readable composition. Do not fabricate an AI image and present it as a frame from the video.

## From transcript to post

Create an evidence map before writing:

- key claim;
- supporting excerpt or timestamp;
- whether it is a direct quote or paraphrase;
- visual candidate;
- uncertainty or missing context.

Do not invent quotes, chapter names, credentials, or timestamps. If automatic recognition is uncertain, paraphrase cautiously or verify against the audio.
