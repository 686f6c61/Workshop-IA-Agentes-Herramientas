import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ModalityContractKitTest(unittest.TestCase):
    def test_required_files_exist(self):
        for relative in [
            "README.md",
            "Makefile",
            "requirements.txt",
            "data/modality_manifest.json",
            "contracts/modality_policy.json",
            "ops/evaluate_modality_manifest.py",
            "templates/entrega.md",
        ]:
            self.assertTrue((ROOT / relative).exists(), relative)

    def test_runner_generates_valid_report(self):
        subprocess.run(
            [sys.executable, "ops/evaluate_modality_manifest.py", "--write", "--fail-on-invalid"],
            cwd=ROOT,
            check=True,
        )
        report = json.loads((ROOT / "output/modality_contract_report.json").read_text(encoding="utf-8"))
        self.assertTrue(report["valid"], report)
        self.assertGreaterEqual(report["case_count"], 3)
        self.assertIn("support-screenshot-001", [case["case_id"] for case in report["cases"]])
        for case in report["cases"]:
            self.assertGreaterEqual(len(case["metrics"]), 2)
            self.assertGreaterEqual(len(case["evidence_required"]), 1)
            self.assertIn("modality_tax", case)

    def test_markdown_contains_decisions(self):
        subprocess.run([sys.executable, "ops/evaluate_modality_manifest.py", "--write"], cwd=ROOT, check=True)
        text = (ROOT / "output/modality_contract_report.md").read_text(encoding="utf-8")
        for expected in [
            "## Decision de ingenieria",
            "## Casos",
            "Impuesto multimodal",
            "Arquitectura recomendada",
        ]:
            self.assertIn(expected, text)


if __name__ == "__main__":
    unittest.main()
