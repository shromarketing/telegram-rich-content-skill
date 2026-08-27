from __future__ import annotations

import sys
import tempfile
import unittest
from argparse import Namespace
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from transcribe_audio import (
    Segment as OutputSegment,
)
from transcribe_audio import (
    build_parser,
    collect_with_checkpoint,
    format_timestamp,
    render,
    render_transcript,
    semantic_blocks,
    transcribe_mlx,
)


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
        self.assertEqual(format_timestamp(3.456, srt=True), "00:00:03,456")

    def test_plain_transcript_keeps_segments_readable(self) -> None:
        result = render_transcript([Segment(0, 1.2, " Первая мысль. "), Segment(1.2, 2, "Вторая.")])
        self.assertEqual(result, "Первая мысль.\n\nВторая.\n")

    def test_timestamped_transcript(self) -> None:
        result = render_transcript([Segment(0, 2.5, "Фрагмент")], timestamps=True)
        self.assertEqual(result, "[00:00:00.000 --> 00:00:02.500] Фрагмент\n")

    def test_srt_and_vtt_rendering(self) -> None:
        segments = [OutputSegment(0, 2.5, "Фрагмент")]
        self.assertIn(
            "00:00:00,000 --> 00:00:02,500",
            render(segments, "srt", timestamps=False, block_seconds=45),
        )
        self.assertTrue(
            render(segments, "vtt", timestamps=False, block_seconds=45).startswith("WEBVTT")
        )

    def test_markdown_groups_at_sentence_boundary(self) -> None:
        segments = [
            OutputSegment(0, 30, "Первая мысль"),
            OutputSegment(30, 50, "закончена."),
            OutputSegment(50, 70, "Вторая."),
        ]
        blocks = semantic_blocks(segments, 45)
        self.assertEqual(len(blocks), 2)
        markdown = render(segments, "md", timestamps=True, block_seconds=45)
        self.assertIn("**[00:00:00.000]**", markdown)

    def test_json_keeps_word_level_structure(self) -> None:
        result = render([OutputSegment(0, 1, "Text")], "json", timestamps=False, block_seconds=45)
        self.assertIn('"words": []', result)

    def test_checkpoint_is_written_segment_by_segment(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            checkpoint = Path(directory) / "progress.jsonl"
            result = collect_with_checkpoint(
                [Segment(0, 1, "One"), Segment(1, 2, "Two")],
                existing=[],
                checkpoint=checkpoint,
                append=False,
            )
            self.assertEqual(len(result), 2)
            self.assertEqual(len(checkpoint.read_text(encoding="utf-8").splitlines()), 2)

    def test_mlx_adapter_maps_model_resume_and_words(self) -> None:
        captured: dict[str, object] = {}

        def fake_transcribe(audio: str, **options: object) -> dict[str, object]:
            captured.update({"audio": audio, **options})
            return {
                "language": "en",
                "segments": [
                    {
                        "start": 12.5,
                        "end": 13.0,
                        "text": " Hello",
                        "words": [
                            {
                                "start": 12.5,
                                "end": 13.0,
                                "word": " Hello",
                                "probability": 0.9,
                            }
                        ],
                    }
                ],
            }

        args = Namespace(
            audio=Path("audio.wav"),
            model="small",
            language="en",
            initial_prompt="Names",
            word_timestamps=True,
        )
        fake_module = SimpleNamespace(transcribe=fake_transcribe)
        with patch.dict(sys.modules, {"mlx_whisper": fake_module}):
            segments, _ = transcribe_mlx(args, 12.5)
        self.assertEqual(captured["path_or_hf_repo"], "mlx-community/whisper-small")
        self.assertEqual(captured["clip_timestamps"], "12.5")
        self.assertEqual(segments[0].words[0].word, "Hello")


if __name__ == "__main__":
    unittest.main()
