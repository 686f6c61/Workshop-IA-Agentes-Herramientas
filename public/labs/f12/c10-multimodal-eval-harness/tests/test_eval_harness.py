from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class MultimodalEvalHarnessTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.run_result = subprocess.run(
            ["python3", "ops/run_multimodal_eval.py"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        cls.report = json.loads((ROOT / "output/eval_report.json").read_text(encoding="utf-8"))

    def test_script_runs(self):
        self.assertEqual(self.run_result.returncode, 0, self.run_result.stdout)

    def test_cases_are_scored(self):
        cases = {item["case_id"]: item for item in self.report["cases"]}
        self.assertEqual(len(cases), 8)
        self.assertEqual(cases["doc_invoice_total"]["decision"], "pass")
        self.assertEqual(cases["chart_becas_growth"]["decision"], "review")
        self.assertEqual(cases["video_alarm_timestamp"]["decision"], "review")
        self.assertEqual(cases["document_pii_refusal"]["decision"], "pass")

    def test_evidence_failures_are_visible(self):
        cases = {item["case_id"]: item for item in self.report["cases"]}
        self.assertIn("evidencia_insuficiente", cases["chart_becas_growth"]["failures"])
        self.assertIn("claims_no_soportados", cases["rag_pdf_slide_policy"]["failures"])

    def test_required_slices_exist(self):
        policy = self.report["policy"]
        slices = {item["slice"] for item in self.report["slices"]}
        self.assertTrue(set(policy["required_slices"]).issubset(slices))

    def test_gate_requires_review(self):
        gate = self.report["gate"]
        self.assertEqual(gate["decision"], "review_before_release")
        self.assertGreaterEqual(len(gate["review_cases"]), 1)

    def test_artifacts_exist(self):
        required = [
            "output/eval_report.md",
            "output/eval_report.json",
            "output/case_scores.csv",
            "output/slice_scores.csv",
            "output/annotation_queue.csv",
            "output/regression_gate.md",
            "output/regression_gate.json",
            "output/multimodal_eval_dashboard.svg",
            "contracts/eval_policy.json",
            "data/eval_cases.json",
            "schemas/eval_case_schema.json",
            "templates/eval_brief.md",
            "templates/entrega.md",
        ]
        for relative in required:
            self.assertTrue((ROOT / relative).exists(), relative)

    def test_signature_exists(self):
        svg = (ROOT / "output/multimodal_eval_dashboard.svg").read_text(encoding="utf-8")
        self.assertIn("IA para gente curiosa / Facsímil 12 / Capítulo 10 / 686f6c61", svg)


if __name__ == "__main__":
    unittest.main()
