# BotFather and channel setup

Use an isolated bot and a private test channel before connecting any production channel.

## 1. Decide whether a bot is needed

A bot is useful when posts are generated from templates, publication is frequent, Telegram Premium is unavailable, or a repeatable agent workflow is required.

For a few manually reviewed posts, a human with Telegram Premium can use the attachment menu → **Article** and may not need a bot. If broad client compatibility is more important than advanced structure, use a classic album.

## 2. Create a separate bot

This step changes an external Telegram account and must be performed by or explicitly authorized by the user.

1. Open the verified `@BotFather` account in Telegram.
2. Send `/newbot`.
3. Choose a human-readable name, for example `Brand Rich Publisher`.
4. Choose a username ending in `bot`.
5. BotFather returns a token. Treat it as a password.

Optional BotFather commands:

- `/setdescription` — public bot description;
- `/setuserpic` — avatar;
- `/setcommands` — command menu for an interactive bot;
- `/revoke` — invalidate a leaked token;
- `/deletebot` — destructive; use only on explicit request.

Do not paste the token into an agent chat. Save it directly into the local `.env`:

```dotenv
TELEGRAM_BOT_TOKEN=replace_locally
TELEGRAM_TEST_CHAT_ID=
TELEGRAM_PRODUCTION_CHAT_ID=
```

## 3. Create a private test channel

1. Create a new private Telegram channel.
2. Open channel management → Administrators → Add administrator.
3. Select the new bot.
4. Enable only **Post Messages**.
5. Leave management of administrators, members, stories, live streams, and other messages disabled.

Use a test channel containing no customer data or private production archive.

## 4. Get the target identifier

For a public channel, `@channel_username` is sufficient.

For a private channel:

1. add the bot as described above;
2. publish a harmless test message in the channel;
3. run `python scripts/show_chat_ids.py`;
4. copy the reported channel ID beginning with `-100` into `TELEGRAM_TEST_CHAT_ID`.

If the bot uses a webhook or another polling process, stop that process before `show_chat_ids.py`; Telegram allows one update consumer at a time.

## 5. Validate before sending

```bash
python scripts/publish_rich.py assets/rich-post.example.html \
  --photo cover=path/to/cover.jpg
```

This must print a validation result and `Nothing sent`.

## 6. Send the first test

Read `TELEGRAM_TEST_CHAT_ID` from the local `.env` and repeat it exactly as the confirmation value:

```bash
python scripts/publish_rich.py assets/rich-post.example.html \
  --photo cover=path/to/cover.jpg \
  --send \
  --confirm-target=-1001234567890
```

The agent must show the user the final text, media list, and target before this network action. A successful test does not authorize production.

## 7. Connect production only after acceptance

After mobile and desktop review, add the same bot or a separate production bot to the production channel with only **Post Messages**. Store its target in `TELEGRAM_PRODUCTION_CHAT_ID`.

Production send requires all three signals:

```bash
python scripts/publish_rich.py final.html \
  --photo cover=cover.jpg \
  --environment production \
  --send \
  --confirm-target=@production_channel
```

Do not put `--send` into an unattended example, alias, default script, or CI job.

## 8. Token incident response

If a token appears in a prompt, screenshot, log, Git commit, or public file:

1. revoke it through BotFather;
2. generate a replacement;
3. update the local `.env`;
4. remove the leaked value from history where applicable;
5. verify the old token no longer works.
