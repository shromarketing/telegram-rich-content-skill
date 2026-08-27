# Contributing

Issues and pull requests are welcome. Keep contributions small, auditable, and safe by
default.

## Development setup

```bash
python3 -m venv .venv
.venv/bin/python -m pip install ruff
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/ruff check .
.venv/bin/ruff format --check scripts tests
python scripts/validate_rich.py assets/rich-post.example.html \
  --media cover=https://example.com/cover.jpg
```

Core tests must stay offline. Do not add active bot tokens, private chat IDs, cookies,
customer materials, model caches, or copied third-party transcripts as fixtures. Use
synthetic examples.

When Telegram changes Rich HTML, update the allowlist, formatting reference, tests, and
version note in the same pull request. New publishing paths must remain dry-run-first and
must preserve the explicit target confirmation gate.

By contributing, you agree that your work is licensed under this repository's MIT
license.
