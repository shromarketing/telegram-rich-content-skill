# End-to-end workflow

## 1. Establish the publishing brief

Capture:

- source material and permission to use it;
- author, channel, audience, and desired action;
- whether the user wants a draft, a test, or an actual production publication;
- target length and whether the source may be condensed;
- required links, quotes, timestamps, credits, and media;
- availability of Telegram Premium and target-client compatibility.

Do not infer publication permission from a request to draft or preview a post.

## 2. Choose the delivery mode

| Mode | Best for | Main limitation |
|---|---|---|
| Manual Article | occasional human-reviewed posts with Premium | manual action; Premium required |
| Classic album | broad compatibility and 2–10 media items | 1024-character caption; no structured longread |
| Rich Message | longreads, tables, details, footnotes, slideshows | older clients may show unsupported content |

If audience compatibility is unknown, prepare a small rich test and a classic fallback.

## 3. Build an evidence map

Before prose, list:

- verified facts;
- direct quotes with exact source positions;
- claims requiring cautious wording;
- useful timestamps;
- media rights and credits;
- links to the original material;
- unresolved gaps.

For third-party videos, write a transformative summary. Do not reproduce a full copyrighted transcript or imply that the speaker endorsed the new post.

## 4. Design the post

A strong long-form structure is usually:

1. outcome-oriented headline;
2. short lead explaining why the material matters;
3. source image or credited original thumbnail;
4. core ideas grouped into sections;
5. a table, checklist, aside, or `details` block only when it improves comprehension;
6. timestamps or source links;
7. one clear next action;
8. footer with source and credits.

Use rich elements as information architecture, not decoration. Avoid empty headings, decorative tables, and collapsible blocks that hide the central point.

## 5. Create media

- Prefer user-owned source media.
- For YouTube, read `youtube-workflow.md`.
- Use the platform's original thumbnail only when its use is appropriate and the post links back to the source.
- For a frame capture, choose a readable, representative frame without subtitles cut off or faces distorted.
- Keep aspect ratios suitable for Telegram previews.

## 6. Write and validate

Start from `assets/rich-post.example.html` or create fresh Rich HTML.

```bash
python scripts/validate_rich.py draft.html \
  --media cover=cover.jpg
```

Then run the publisher without `--send`:

```bash
python scripts/publish_rich.py draft.html \
  --photo cover=cover.jpg
```

Resolve every error before a network action.

## 7. Test in isolation

After explicit approval to send a test:

```bash
python scripts/publish_rich.py draft.html \
  --photo cover=cover.jpg \
  --send \
  --confirm-target=-1001234567890
```

Check:

- current Telegram Desktop;
- current mobile Telegram;
- an older client or a planned fallback;
- notification and chat-list preview;
- forwarding behavior;
- all links and anchors;
- media order and captions;
- tables at narrow width;
- collapsed and expanded `details` blocks.

## 8. Production gate

Immediately before production, show the user:

- final text or rendered test message;
- exact media files or URLs;
- bot identity;
- exact destination;
- whether notifications are enabled;
- known compatibility limitations.

Only then use `--environment production --send --confirm-target=...`.

## 9. Record the outcome

Keep only durable operational information:

- source and verification date;
- template/version used;
- test result and client versions;
- production message link or ID when publication was authorized;
- known limitations.

Never record tokens, API keys, cookies, or private source material in a decision log.
