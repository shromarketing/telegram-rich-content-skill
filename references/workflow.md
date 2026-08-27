# End-to-end workflow

For a reusable or high-stakes material, begin with:

```bash
python scripts/init_material.py "descriptive material name"
```

This creates one auditable folder for the source, transcript, evidence map, brief,
voice-profile reference, plain fallback, Rich HTML, media, and validation report.

## 1. Establish the editorial brief

Capture what is known:

- source material and permission to use it;
- author, channel, audience, and desired action;
- draft, private test, or production publication;
- target depth and whether the source may be condensed;
- required links, quotes, timestamps, credits, and media;
- approved voice profile or examples;
- availability of Telegram Premium and target-client compatibility.

Use `assets/content-brief.template.md` when a reusable record helps. Do not infer publication permission from a request to draft or preview a post.

## 2. Clarify only consequential gaps

Ask the minimum needed when missing information could change facts, audience, first-person position, call to action, legal risk, or destination. Otherwise make a reasonable assumption, state it briefly, and produce a useful first version.

If no tone of voice is configured, offer the onboarding in `onboarding.md`; do not block urgent work on it.

## 3. Build an evidence map

Before prose, list verified facts, exact quotes and positions, uncertain claims, timestamps, media rights, source links, and unresolved conflicts. For third-party material, write a transformative post and clearly separate the source author's ideas from the user's commentary.

## 4. Shape the copy

A strong long-form structure is usually:

1. a specific, outcome-oriented hook;
2. a short lead explaining why the material matters;
3. source media or a credited original thumbnail when appropriate;
4. core ideas grouped into readable sections;
5. a table, checklist, aside, or `details` block only when it improves comprehension;
6. examples, timestamps, or source links;
7. one clear next action;
8. a source and credit footer when needed.

Apply the approved voice profile to rhythm, vocabulary, degree of directness, formatting, humor, and CTA. Preserve factual meaning over stylistic consistency. Produce variants only when they support a real choice, such as different hooks or lengths.

## 5. Choose delivery mode

| Mode | Best for | Main limitation |
|---|---|---|
| Normal post | short, broadly compatible copy | limited structure |
| Manual Article | occasional human-reviewed longreads with Premium | manual action; Premium required |
| Classic album | broad compatibility and 2–10 media items | short caption; no structured longread |
| Rich Message | longreads, tables, details, footnotes, slideshows | older clients may show unsupported content |

If compatibility is unknown, prepare a small rich test and a normal or album fallback.

## 6. Create media, write, and validate

Prefer user-owned source media. For YouTube, read `youtube-workflow.md`.

```bash
python scripts/validate_rich.py draft.html --media cover=cover.jpg
python scripts/preview_rich.py draft.html --out preview.html
python scripts/publish_rich.py draft.html --photo cover=cover.jpg
```

The browser preview is deliberately approximate. Resolve every validation error before
a network action and treat Telegram Desktop/mobile as the rendering authority. For a
plain or album fallback:

```bash
python scripts/publish_fallback.py post-plain.md --mode plain
python scripts/publish_fallback.py album-caption.txt --mode album \
  --photo p1=first.jpg --photo p2=second.jpg
```

## 7. Test in isolation

After explicit approval to send a test:

```bash
python scripts/publish_rich.py draft.html \
  --photo cover=cover.jpg \
  --send \
  --confirm-target=-1001234567890
```

Check current desktop and mobile Telegram, notification preview, forwarding, links, media order, narrow tables, expanded details, and the planned fallback.

## 8. Production gate

Immediately before production, show the final text or test message, exact media, bot identity, exact destination, notification choice, and known compatibility limitations. Only then use `--environment production --send --confirm-target=...`.

## 9. Improve the editorial system

After the user approves a material, offer—not automatically perform—the following durable updates:

- add the post as an approved voice example;
- record a stable preferred phrase or banned cliché;
- save a reusable structure for that channel;
- note a verified source or recurring CTA.

Never store tokens, cookies, unpublished source content, sensitive personal inferences, or a hidden psychological profile in the editorial profile.
