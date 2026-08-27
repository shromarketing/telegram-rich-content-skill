from __future__ import annotations

import sys
import unittest
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from transcribe_audio import build_parser, format_timestamp, render_transcript


@dataclass
class Segment:
    start: float
    end: float
    text: str


class TranscribeAudioTests(unittest.TestCase):
    def test_defaults_are_local_and_api_free(self) -> None:
        args = build_parser().parse_args(["audio.mp3", "--out", "transcript.txt"])
        self.assertEqual(args.model, "small")
        self.assertEqual(args.device, "auto")
        self.assertFalse(hasattr(args, "api_key"))
        self.assertFalse(hasattr(args, "env_file"))

    def test_timestamp_format(self) -> None:
        self.assertEqual(format_timestamp(3723.456), "01:02:03.456")

    def test_plain_transcript_keeps_segments_readable(self) -> None:
        result = render_transcript(
            [Segment(0, 1.2, " Первая мысль. "), Segment(1.2, 2, "Вторая.")]
        )
        self.assertEqual(result, "Первая мысль.\n\nВторая.\n")

    def test_timestamped_transcript(self) -> None:
        result = render_transcript([Segment(0, 2.5, "Фрагмент")], timestamps=True)
        self.assertEqual(result, "[00:00:00.000 --> 00:00:02.500] Фрагмент\n")


if __name__ == "__main__":
    unittest.main()
