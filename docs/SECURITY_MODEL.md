# Security model

The skill assumes an AI agent can read project files and run local commands, but should
not receive or disclose secrets in conversational context.

| Asset | Location | Main control |
|---|---|---|
| Bot token | local `.env` | ignored by Git; never printed |
| Test/production target | local `.env` | separate variables and exact confirmation |
| Voice profile | user project | explicit creation and editable evidence |
| Unpublished source | material folder | user-controlled local storage |
| Model files | local cache | optional offline-only mode |

Publishing has two independent gates: `--send` enables a network mutation, and
`--confirm-target` must exactly match the selected environment. The default environment
is test. Selecting production does not bypass either gate.

The Rich validator rejects unsupported tags/attributes, event handlers, inline style,
unsafe URL schemes, malformed nesting, unsupported named entities, limit overflows, and
media-ID mismatches. This reduces accidental rejection and injection risk, but Telegram's
server validation remains authoritative.

See [SECURITY.md](../SECURITY.md) for reporting and token-rotation instructions.
