# Telegram Rich Message formatting

Verified against the official [Telegram Bot API](https://core.telegram.org/bots/api#rich-message-formatting-options) and [bot features guide](https://core.telegram.org/bots/features) on 2026-08-27. Re-check the official documentation before production use because the API is evolving.

## Input model

`InputRichMessage` accepts exactly one content field:

- `html` — Rich HTML;
- `markdown` — Rich Markdown;
- `blocks` — explicit input block objects.

It may also contain:

- `media` — files referenced from HTML or Markdown;
- `is_rtl` — right-to-left rendering;
- `skip_entity_detection` — disable automatic URL, mention, hashtag, command, email, and phone detection.

For agent-generated editorial posts, Rich HTML is usually the most predictable choice.

## Limits

- 32768 UTF-8 text characters;
- 500 blocks including nested blocks, list items, rows, quotations, and details;
- 16 nesting levels;
- 50 media attachments;
- 20 table columns.

The local validator catches common structural errors but the official Telegram API remains authoritative.

## Inline HTML

Supported inline forms include:

```html
<b>bold</b>
<i>italic</i>
<u>underline</u>
<s>strikethrough</s>
<code>inline code</code>
<mark>highlight</mark>
<sub>subscript</sub>
<sup>superscript</sup>
<tg-spoiler>hidden text</tg-spoiler>
<tg-math>x^2</tg-math>
<a href="https://example.com">link</a>
```

Use only tags documented by Telegram. Unknown tags may be ignored or rejected.

## Blocks

```html
<h2>Section heading</h2>
<p>Paragraph.</p>
<hr/>

<ul>
  <li>First item</li>
  <li><input type="checkbox" checked/> Completed item</li>
</ul>

<blockquote>Quoted text<cite>Source</cite></blockquote>
<aside>Important takeaway<cite>Editorial note</cite></aside>

<details>
  <summary>Open the details</summary>
  <p>Additional context.</p>
</details>

<table bordered striped>
  <caption>Comparison</caption>
  <tr><th>Option</th><th>Use when</th></tr>
  <tr><td>Album</td><td>Compatibility matters</td></tr>
</table>

<footer>Source and credits</footer>
```

Other documented blocks include code, mathematical expressions, anchors, references, maps, collages, slideshows, and media.

## Media references

Markup:

```html
<img src="tg://photo?id=cover"/>
<video src="tg://video?id=demo"></video>
<audio src="tg://audio?id=episode"></audio>
<tg-document src="tg://document?id=guide"></tg-document>
```

Each ID must be declared in the `media` array. In `aiogram`, local files use `FSInputFile`; a public HTTP(S) URL may be passed as a URL string.

IDs must match `[A-Za-z0-9_-]{1,64}`.

## Slideshow and collage

True swipe slideshow:

```html
<tg-slideshow>
  <img src="tg://photo?id=p1"/>
  <img src="tg://photo?id=p2"/>
  <figcaption>One caption for the slideshow<cite>Photo credit</cite></figcaption>
</tg-slideshow>
```

Grid:

```html
<tg-collage>
  <img src="tg://photo?id=p1"/>
  <img src="tg://photo?id=p2"/>
</tg-collage>
```

Media elements must be separate blocks, not nested inside a paragraph.

## Footnotes and anchors

```html
<p>The claim has a source<a href="#note-1">[1]</a>.</p>
<tg-reference name="note-1">Source description and URL.</tg-reference>
```

An empty `<a name="section"></a>` on its own creates an internal anchor.

## HTML entities

All numeric entities are supported. Telegram documents a limited named set, including:

```text
&lt; &gt; &amp; &quot; &apos; &nbsp; &hellip; &mdash; &ndash;
&lsquo; &rsquo; &ldquo; &rdquo;
```

Prefer literal UTF-8 punctuation when possible.

## Rich Markdown

Rich Markdown follows GitHub Flavored Markdown where possible and supports Telegram-specific extensions:

```markdown
# Heading

**bold** *italic* ~~strike~~ ==highlight== ||spoiler||

- [x] completed
- [ ] pending

| Option | Result |
|---|---|
| Rich | Structured longread |

![](tg://photo?id=cover)

<details>
<summary>More</summary>
Markdown is supported here.
</details>
```

Choose one primary style per project. Rich HTML is more verbose but easier to validate deterministically; Rich Markdown is faster for text-heavy drafts.

## Compatibility fallback

Readers on older Telegram clients may see an unsupported-message placeholder. For broad audiences, pair the rich post with a regular summary or publish a classic album instead.

## Version note

Bot API 10.1 introduced Rich Messages. Bot API 10.2 added explicit media arrays and input blocks. Bot API 10.3 added document media and additional rich controls. This skill's publisher targets `aiogram >= 3.31` and uses HTML plus explicit media.
