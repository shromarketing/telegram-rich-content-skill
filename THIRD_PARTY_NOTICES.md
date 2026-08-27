# Third-party notices

## tg-rich-post

Parts of the Telegram Rich Message grammar, troubleshooting knowledge, and the original minimal `aiogram` example were adapted from:

- Project: `tg-rich-post`
- Author: `seozavr`
- Source: https://github.com/seozavr/tg-rich-post
- License: MIT
- Source revision reviewed: `0015d78c54ca80f8d5cecbddf0c92ce8b3b7c145`

Original notice:

```text
MIT License

Copyright (c) 2026 seozavr
```

The full MIT permission and warranty disclaimer is preserved in this repository's [LICENSE](LICENSE).

## yt-dlp

The optional YouTube workflow invokes `yt-dlp` as an external dependency. It is not vendored into this repository.

- Source: https://github.com/yt-dlp/yt-dlp
- License: The Unlicense; third-party components have their own licenses.

## faster-whisper

The optional local transcription helper uses the separately installed `faster-whisper` package. It is not vendored into this repository.

- Source: https://github.com/SYSTRAN/faster-whisper
- License: MIT

`faster-whisper` installs CTranslate2, PyAV, and other dependencies with their own
licenses. Whisper model weights are downloaded separately on first use and remain
subject to their respective model licenses.

## mlx-whisper

The optional Apple Silicon backend can use the separately installed `mlx-whisper`
package. It is not vendored into this repository.

- Source: https://github.com/ml-explore/mlx-examples/tree/main/whisper
- License: MIT

MLX-converted model weights are downloaded separately and remain subject to their model
licenses.
