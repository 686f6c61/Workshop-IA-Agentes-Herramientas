from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class MultimodalReleaseLabTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.run_result = subprocess.run(
            ["python3", "ops/run_multimodal_release_lab.py"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        cls.report = json.loads((ROOT / "output/release_report.json").read_text(encoding="utf-8"))

    def test_runner_executes(self):
        self.assertEqual(self.run_result.returncode, 0, self.run_result.stdout)

    def test_expected_decisions_match(self):
        for section in ("baseline", "remediated", "candidate"):
            mismatches = [item["case_id"] for item in self.report[section] if not item["decision_matches_expected"]]
            self.assertEqual(mismatches, [], section)

    def test_baseline_blocks_and_remediation_improves(self):
        baseline = self.report["summaries"]["baseline"]
        remediated = self.report["summaries"]["remediated"]
        self.assertEqual(baseline["global_decision"], "block_release")
        self.assertEqual(remediated["global_decision"], "review_release")
        self.assertGreater(baseline["block_count"], remediated["block_count"])
        self.assertGreater(remediated["pass_count"], baseline["pass_count"])

    def test_candidate_is_ship_ready(self):
        candidate = self.report["summaries"]["candidate"]
        self.assertEqual(candidate["global_decision"], "ship")
        self.assertEqual(candidate["review_count"], 0)
        self.assertEqual(candidate["block_count"], 0)
        self.assertEqual(candidate["pass_count"], candidate["case_count"])

    def test_all_chapters_are_traced(self):
        rows = self.report["chapter_traceability"]
        chapters = {int(row["chapter"]) for row in rows if row["case_count"] > 0}
        self.assertEqual(chapters, set(range(1, 12)))

    def test_artifacts_exist(self):
        required = [
            "output/release_report.json",
            "output/baseline_release_report.md",
            "output/remediated_release_report.md",
            "output/candidate_release_report.md",
            "output/release_matrix.csv",
            "output/remediation_diff.csv",
            "output/release_candidate_diff.csv",
            "output/chapter_traceability.csv",
            "output/modality_coverage.csv",
            "output/sli_slo_matrix.csv",
            "output/contract_validation_report.md",
            "output/contract_validation_report.json",
            "output/contract_validation_matrix.csv",
            "output/evidence_pack.md",
            "output/decision_card.md",
            "output/release_change_request.md",
            "output/release_pr_checklist.md",
            "output/version_manifest.json",
            "output/multimodal_lab_architecture.svg",
            "contracts/release_policy.json",
            "contracts/release_gate_policy.rego",
            "data/baseline_cases.json",
            "data/remediated_cases.json",
            "data/candidate_patch.json",
            "data/invalid_case_examples.json",
            "schemas/case_schema.json",
            "schemas/candidate_patch_schema.json",
            "templates/entrega.md",
            "solutions/reference/expected_decision.md",
        ]
        for relative in required:
            self.assertTrue((ROOT / relative).exists(), relative)

    def test_candidate_sli_slo_passes(self):
        rows = self.report["sli_slo_matrix"]
        candidate_rows = [row for row in rows if row["scenario"] == "candidate"]
        self.assertTrue(candidate_rows)
        self.assertEqual([row for row in candidate_rows if row["status"] != "pass"], [])

    def test_contract_validation_catches_bad_examples(self):
        rows = self.report["contract_validation"]
        invalid = [row for row in rows if row["source"] == "invalid_examples"]
        self.assertEqual(len(invalid), 3)
        self.assertTrue(all(row["status"] == "fail" for row in invalid))

    def test_signature_exists(self):
        svg = (ROOT / "output/multimodal_lab_architecture.svg").read_text(encoding="utf-8")
        self.assertIn("IA para gente curiosa / Facsímil 12 / Capítulo 12 / 686f6c61", svg)


if __name__ == "__main__":
    unittest.main()
