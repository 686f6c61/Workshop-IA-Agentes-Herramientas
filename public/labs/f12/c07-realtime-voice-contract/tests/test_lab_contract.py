from __future__ import annotations

import json
import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RealtimeVoiceKitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.run_result = subprocess.run(
            ["python3", "ops/run_realtime_voice_audit.py"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        cls.report = json.loads((ROOT / "output/realtime_voice_report.json").read_text(encoding="utf-8"))

    def test_script_runs(self):
        self.assertEqual(self.run_result.returncode, 0, self.run_result.stdout)

    def test_expected_decisions_are_present(self):
        decisions = {item["case_id"]: item["decision"] for item in self.report["results"]}
        self.assertEqual(decisions["q01_estado_beca"], "answer")
        self.assertEqual(decisions["q02_ruido_pasillo"], "ask_repeat")
        self.assertEqual(decisions["q03_interrupcion_usuario"], "stop_and_answer")
        self.assertEqual(decisions["q04_datos_sensibles"], "answer")
        self.assertEqual(decisions["q05_accion_con_confirmacion"], "confirm_before_tool")

    def test_turn_cards_are_downloadable_artifacts(self):
        for case_id in ["q01_estado_beca", "q03_interrupcion_usuario", "q04_datos_sensibles"]:
            path = ROOT / "output/turn_cards" / f"{case_id}.json"
            self.assertTrue(path.exists(), path)
            card = json.loads(path.read_text(encoding="utf-8"))
            self.assertIn("metrics", card)
            self.assertIn("evidence", card)
            self.assertIn("limits", card)
            self.assertIn("next_action", card)

    def test_pii_is_redacted_in_turn_card(self):
        path = ROOT / "output/turn_cards/q04_datos_sensibles.json"
        card = json.loads(path.read_text(encoding="utf-8"))
        transcript = card["redacted_transcript"]
        self.assertNotRegex(transcript, re.compile(r"\b12345678Z\b"))
        self.assertNotRegex(transcript, re.compile(r"\b612 345 678\b"))
        self.assertIn("[DNI]", transcript)
        self.assertIn("[PHONE_ES]", transcript)

    def test_barge_in_latency_is_measured(self):
        case = next(item for item in self.report["results"] if item["case_id"] == "q03_interrupcion_usuario")
        self.assertEqual(case["decision"], "stop_and_answer")
        self.assertLessEqual(case["metrics"]["barge_in_stop_latency_ms"], 250)

    def test_critical_slots_are_part_of_the_gate(self):
        noisy = next(item for item in self.report["results"] if item["case_id"] == "q02_ruido_pasillo")
        self.assertGreater(noisy["metrics"]["critical_slot_error_rate"], 0)
        self.assertIn("critical_slot_error", noisy["quality_flags"])
        self.assertTrue((ROOT / "output/voice_eval_matrix.csv").exists())

    def test_audio_and_svg_outputs_exist(self):
        for case_id in ["q01_estado_beca", "q02_ruido_pasillo", "q05_accion_con_confirmacion"]:
            self.assertTrue((ROOT / "output/audio" / f"{case_id}.wav").exists(), case_id)
        svg = (ROOT / "output/realtime_voice_pipeline.svg").read_text(encoding="utf-8")
        self.assertIn("IA para gente curiosa / Facsímil 12 / Capítulo 07 / 686f6c61", svg)

    def test_zip_contains_operational_entries(self):
        required = [
            "README.md",
            "Makefile",
            "contracts/realtime_voice_policy.json",
            "schemas/voice_turn_schema.json",
            "data/voice_cases.json",
            "ops/run_realtime_voice_audit.py",
            "templates/entrega.md",
        ]
        for relative in required:
            self.assertTrue((ROOT / relative).exists(), relative)


if __name__ == "__main__":
    unittest.main()
