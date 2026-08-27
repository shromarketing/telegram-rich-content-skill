# Security

## Never commit secrets

Keep these values only in a local `.env`:

- Telegram bot token;
- private channel IDs when their disclosure matters;
- cookies or authenticated browser exports.

The bundled transcription path is local and does not require an OpenAI or other paid
speech-to-text API key. Downloaded model files remain on the machine unless the user
chooses a different model cache location.

`scripts/doctor.py` does not print environment variable values. Its default run is
offline; `--telegram` performs only explicit read-only `getMe`/`getChat` checks.

The repository ignores `.env`, cookies, local output, and virtual environments. Before every public push, inspect the staged diff and run a secret scan.

## If a Telegram token leaked

1. Open `@BotFather`.
2. Revoke the exposed token.
3. Generate a replacement.
4. Update only the local `.env`.
5. Remove the secret from Git history if it was committed; rotating the token is still mandatory.

## Minimal Telegram rights

For channel publishing, grant the bot only **Post Messages**. Do not grant rights to manage administrators, members, stories, live streams, or other messages unless the use case explicitly requires them.

Both publishers are dry-run-first. A network send requires `--send` and an exact
`--confirm-target`; production uses a separate environment variable and does not bypass
either gate.

## Reporting a vulnerability

Open a GitHub security advisory for the repository. Do not include active tokens, API keys, cookies, private channel IDs, or unpublished customer data in a public issue.
