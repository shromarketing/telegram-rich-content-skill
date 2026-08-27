from __future__ import annotations

import argparse
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from prepare_youtube import build_command


class PrepareYouTubeTests(unittest.TestCase):
    def args(self, **overrides) -> argparse.Namespace:
        values = {
            "url": "https://youtu.be/example",
            "output_dir": Path("output/video"),
            "thumbnail": False,
            "captions": False,
            "audio": False,
            "language": "ru.*,en.*",
        }
        values.update(overrides)
        return argparse.Namespace(**values)

    def test_thumbnail_does_not_download_video(self) -> None:
        command = build_command(self.args(thumbnail=True))
        self.assertIn("--skip-download", command)
        self.assertIn("--write-thumbnail", command)
        self.assertIn("--write-info-json", command)
        self.assertIn("--no-playlist", command)

    def test_captions_include_manual_and_auto(self) -> None:
        command = build_command(self.args(captions=True))
        self.assertIn("--write-subs", command)
        self.assertIn("--write-auto-subs", command)
        self.assertIn("ru.*,en.*", command)

    def test_audio_extracts_without_video_playlist(self) -> None:
        command = build_command(self.args(audio=True))
        self.assertIn("--extract-audio", command)
        self.assertIn("mp3", command)
        self.assertNotIn("--skip-download", command)
        self.assertIn("--no-playlist", command)

    def test_cookies_are_never_added(self) -> None:
        command = build_command(self.args(thumbnail=True, captions=True, audio=True))
        joined = " ".join(command)
        self.assertNotIn("cookie", joined.lower())


if __name__ == "__main__":
    unittest.main()
