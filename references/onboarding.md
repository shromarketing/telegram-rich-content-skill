# First-use onboarding and tone of voice

The onboarding turns the skill from a formatter into a reusable Telegram editor. Keep it short, optional, and evidence-based.

## Fast start

If the user needs a post now, ask only for the missing facts that materially change it, draft with stated assumptions, and offer profile setup after the draft.

If the user wants ongoing copywriting support, ask for:

1. the channel and the people it serves;
2. the main editorial or business goal;
3. 3–5 approved examples written in the desired voice;
4. three desired qualities and three unwanted qualities;
5. preferred depth, formatting, directness, and call to action;
6. words, clichés, claims, or topics to avoid;
7. the local path where the approved profile may be saved.

Do not ask all seven questions again when the answer already exists in project context.

## Build the voice profile

Copy `assets/voice-profile.template.md` into the user's project only after they approve creating it. Extract observable writing decisions from approved examples:

- common openings and headline patterns;
- sentence length, rhythm, paragraphs, and transitions;
- vocabulary, professional terms, and acceptable slang;
- first-person position and degree of certainty;
- humor, emotion, disagreement, and sales pressure;
- use of emoji, lists, headings, tables, and rich blocks;
- typical CTA and source/credit habits;
- explicit anti-patterns.

Label weak inferences as hypotheses and ask the user to correct them. A voice profile is not a psychological assessment and must not contain diagnoses, manipulation triggers, private vulnerabilities, or secrets.

## Use it on every draft

1. Read the current approved profile and 2–3 relevant examples.
2. Preserve source facts and the user's intended position.
3. Apply the profile to editorial choices, not as a word-substitution filter.
4. Run a natural-language pass: remove generic AI openings, repetitive conclusions, unsupported certainty, and decorative formatting.
5. Explain any intentional deviation when clarity, accuracy, platform limits, or legal risk requires it.

Do not imitate a third party in a deceptive way. For a brand or team voice, define shared observable characteristics instead of pretending to be a named person.

## Recommended optional connections

Offer only what matches the user's workflow:

- a project-local `voice-profile.md` and approved example folder;
- a source-of-truth document with current products, links, bios, and claims;
- a content brief template for repeated channels;
- a fact-check or web-research capability for changing claims;
- local `faster-whisper` for voice notes, podcasts, and video audio;
- `yt-dlp` for lawful public YouTube metadata, thumbnails, captions, and audio;
- a separate Telegram bot and private test channel for repeatable rich publishing;
- an editorial calendar or content backlog, if the user already has one.

These are recommendations, not permission to install software, create bots, modify channels, browse private sources, or publish.

## Useful first prompts

```text
Проведи короткий онбординг и создай черновик моего voice profile по этим пяти постам.
Ничего не публикуй.
```

```text
Вот голосовая с мыслью. Расшифруй локально без платного API, задай только
существенные вопросы и сделай подробный пост в моём tone of voice.
```

```text
Преврати эту статью в самостоятельный Telegram-пост: отдели факты автора от моего
комментария, сохрани ссылки, не копируй исходник и подготовь rich-версию для теста.
```
