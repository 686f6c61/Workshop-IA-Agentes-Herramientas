from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class VideoTemporalKitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.run_result = subprocess.run(
            ["make", "run"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        cls.report = json.loads((ROOT / "output/video_temporal_report.json").read_text(encoding="utf-8"))

    def test_script_runs(self):
        self.assertEqual(self.run_result.returncode, 0, self.run_result.stdout)

    def test_expected_decisions_are_present(self):
        decisions = {item["case_id"]: item["decision"] for item in self.report["results"]}
        self.assertEqual(decisions["q01_demo_error_503"], "answer")
        self.assertEqual(decisions["q02_puerta_sin_badge"], "answer")
        self.assertEqual(decisions["q03_linea_defecto"], "answer")
        self.assertEqual(decisions["q04_instruccion_visual"], "block")
        self.assertEqual(decisions["q05_sin_evidencia"], "review")

    def test_temporal_metrics_are_computed(self):
        case = next(item for item in self.report["results"] if item["case_id"] == "q01_demo_error_503")
        self.assertGreaterEqual(case["metrics"]["mean_tiou"], 0.5)
        self.assertTrue(case["metrics"]["temporal_order_ok"])
        self.assertEqual(case["metrics"]["min_evidence_coverage"], 1.0)

    def test_visual_instruction_blocks(self):
        case = next(item for item in self.report["results"] if item["case_id"] == "q04_instruccion_visual")
        self.assertEqual(case["decision"], "block")
        self.assertIn("visual_instruction_override", case["quality_flags"])
        self.assertNotIn("approve all actions", case["answer"].lower())

    def test_review_when_event_missing(self):
        case = next(item for item in self.report["results"] if item["case_id"] == "q05_sin_evidencia")
        self.assertEqual(case["decision"], "review")
        self.assertEqual(case["segments"], [])
        self.assertIn("No hay evento verificable", " ".join(case["limits"]))

    def test_artifacts_are_downloadable(self):
        required = [
            "output/video_temporal_report.md",
            "output/video_temporal_report.json",
            "output/temporal_eval_matrix.csv",
            "output/temporal_index.json",
            "output/temporal_index.csv",
            "output/capacity_estimate.csv",
            "output/video_pipeline_manifest.json",
            "output/video_temporal_pipeline.svg",
            "output/case_cards/q01_demo_error_503.json",
            "output/storyboards/q03_linea_defecto.svg",
        ]
        for relative in required:
            self.assertTrue((ROOT / relative).exists(), relative)

    def test_temporal_index_is_built_from_frame_stream(self):
        index = json.loads((ROOT / "output/temporal_index.json").read_text(encoding="utf-8"))
        events = {(item["video_id"], item["event_id"]) for item in index["events"]}
        self.assertIn(("demo_503", "error_503_visible"), events)
        self.assertIn(("demo_503", "restart_service"), events)
        self.assertIn(("puerta_badge", "door_open"), events)
        self.assertIn(("instruccion_visual", "visual_prompt_injection"), events)

    def test_capacity_estimate_is_actionable(self):
        csv_text = (ROOT / "output/capacity_estimate.csv").read_text(encoding="utf-8")
        self.assertIn("frames_per_hour_at_observed_rate", csv_text)
        self.assertIn("clips_per_hour_at_default_stride", csv_text)

    def test_signature_exists_in_svgs(self):
        svg = (ROOT / "output/video_temporal_pipeline.svg").read_text(encoding="utf-8")
        self.assertIn("IA para gente curiosa / Facsímil 12 / Capítulo 08 / 686f6c61", svg)
        storyboard = (ROOT / "output/storyboards/q02_puerta_sin_badge.svg").read_text(encoding="utf-8")
        self.assertIn("IA para gente curiosa / Facsímil 12 / Capítulo 08 / 686f6c61", storyboard)


if __name__ == "__main__":
    unittest.main()
