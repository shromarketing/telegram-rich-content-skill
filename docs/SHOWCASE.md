# Showcase: one source, three deliverables

The synthetic example in [`examples/source-to-post`](../examples/source-to-post) starts
with a rough voice-note transcript about choosing the lightest useful Telegram format.
It produces:

1. an evidence map that prevents invented claims;
2. a broadly compatible plain post;
3. a Rich Message with a heading, decision table, expandable implementation detail,
   action checklist, and source footer.

Validate it locally:

```bash
python scripts/validate_rich.py examples/source-to-post/post-rich.html
python scripts/preview_rich.py examples/source-to-post/post-rich.html \
  --out output/showcase-preview.html
python scripts/check_voice.py examples/source-to-post/post-plain.md \
  --profile examples/source-to-post/style-check.json
```

Nothing is sent. The example deliberately uses no secrets, external media, copyrighted
source text, or live Telegram target.
