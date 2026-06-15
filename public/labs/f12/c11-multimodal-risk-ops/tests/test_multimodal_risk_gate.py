from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class MultimodalRiskGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.run_result = subprocess.run(
            ["python3", "ops/run_multimodal_risk_gate.py"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        cls.report = json.loads((ROOT / "output/risk_report.json").read_text(encoding="utf-8"))

    def test_script_runs(self):
        self.assertEqual(self.run_result.returncode, 0, self.run_result.stdout)

    def test_expected_decisions_match(self):
        cases = self.report["cases"]
        self.assertEqual(len(cases), 14)
        mismatches = [item["case_id"] for item in cases if not item["decision_matches_expected"]]
        self.assertEqual(mismatches, [])

    def test_secret_and_prompt_injection_block(self):
        cases = {item["case_id"]: item for item in self.report["cases"]}
        self.assertEqual(cases["ui_api_key_prompt_injection"]["decision"], "block")
        self.assertIn("secreto_sin_redactar", cases["ui_api_key_prompt_injection"]["failures"])
        self.assertIn("prompt_injection_visual_actionable", cases["ui_api_key_prompt_injection"]["failures"])

    def test_public_case_passes(self):
        cases = {item["case_id"]: item for item in self.report["cases"]}
        self.assertEqual(cases["public_product_photo"]["decision"], "pass")

    def test_artifacts_exist(self):
        required = [
            "output/risk_report.md",
            "output/risk_report.json",
            "output/risk_matrix.csv",
            "output/redaction_plan.csv",
            "output/retention_matrix.csv",
            "output/incident_runbook.md",
            "output/threat_model.csv",
            "output/artifact_lineage.csv",
            "output/artifact_lineage.jsonl",
            "output/policy_decisions.csv",
            "output/policy_decisions.md",
            "output/detector_metrics.csv",
            "output/detector_samples.csv",
            "output/detector_eval_report.md",
            "output/multimodal_risk_gate.svg",
            "contracts/multimodal_risk_policy.json",
            "data/multimodal_risk_cases.json",
            "data/detector_eval_cases.json",
            "data/policy_decision_examples.json",
            "policies/egress_policy.rego",
            "policies/egress_policy.cedar",
            "schemas/risk_case_schema.json",
            "templates/entrega.md",
        ]
        for relative in required:
            self.assertTrue((ROOT / relative).exists(), relative)

    def test_policy_decisions_match(self):
        decisions = self.report["policy_decisions"]
        self.assertEqual(len(decisions), 4)
        mismatches = [item["decision_id"] for item in decisions if not item["matches_expected"]]
        self.assertEqual(mismatches, [])
        deny = {item["decision_id"]: item for item in decisions}
        self.assertEqual(deny["deny_public_webhook"]["decision"], "deny")

    def test_detector_metrics_expose_false_negatives(self):
        metrics = {item["entity_type"]: item for item in self.report["detector_metrics"]}
        self.assertIn("DNI_NIE", metrics)
        self.assertGreaterEqual(metrics["DNI_NIE"]["fn"], 1)
        self.assertFalse(metrics["DNI_NIE"]["passes_recall_target"])

    def test_lineage_exists_for_each_case(self):
        self.assertEqual(len(self.report["lineage"]), len(self.report["cases"]))
        first = self.report["lineage"][0]
        self.assertIn("artifact_hash", first)
        self.assertIn("policy_hash", first)

    def test_signature_exists(self):
        svg = (ROOT / "output/multimodal_risk_gate.svg").read_text(encoding="utf-8")
        self.assertIn("IA para gente curiosa / Facsímil 12 / Capítulo 11 / 686f6c61", svg)


if __name__ == "__main__":
    unittest.main()
