import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class VLMRequestContractTest(unittest.TestCase):
    def test_required_files_exist(self):
        required = [
            "Makefile",
            "README.md",
            "requirements.txt",
            "contracts/vlm_request_policy.json",
            "data/vlm_cases.json",
            "data/images/grant_form_blocked.svg",
            "data/docs/grant_policy_excerpt.md",
            "schemas/vlm_output_schema.json",
            "ops/audit_vlm_requests.py",
            "templates/entrega.md",
        ]
        for relative in required:
            self.assertTrue((ROOT / relative).exists(), relative)
        self.assertTrue((ROOT / "data/images/visual_prompt_injection.svg").exists())
        self.assertTrue((ROOT / "data/images/low_quality_capture.svg").exists())

    def test_script_generates_contracts(self):
        subprocess.run(
            ["python3", "ops/audit_vlm_requests.py", "--write", "--fail-on-invalid"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        report = json.loads((ROOT / "output" / "vlm_request_report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["gate"], "pass")
        self.assertGreaterEqual(report["case_count"], 5)
        self.assertGreaterEqual(report["block_count"], 1)
        self.assertGreaterEqual(report["review_count"], 1)
        self.assertTrue((ROOT / "output" / "request_contracts" / "grant_workflow_005.json").exists())
        self.assertTrue((ROOT / "output" / "request_contracts" / "visual_injection_004.json").exists())
        grant = json.loads(
            (ROOT / "output" / "request_contracts" / "grant_workflow_005.json").read_text(encoding="utf-8")
        )
        self.assertIn("visual_evidence", grant["output_fields"])
        self.assertGreater(grant["budget"]["visual_tokens"], 0)
        injection = json.loads(
            (ROOT / "output" / "request_contracts" / "visual_injection_004.json").read_text(encoding="utf-8")
        )
        self.assertIn("prompt_injection_visual", injection["human_review_triggers"])
        self.assertIn("task_metric", injection)

    def test_svg_and_markdown_are_teachable(self):
        svg = (ROOT / "output" / "vlm_architecture_contract.svg").read_text(encoding="utf-8")
        md = (ROOT / "output" / "vlm_request_report.md").read_text(encoding="utf-8")
        self.assertIn("IA para gente curiosa / Facsímil 12 / Capítulo 04 / 686f6c61", svg)
        self.assertIn("Contrato antes de llamar a un VLM", svg)
        self.assertIn("grant_workflow_005", md)
        self.assertIn("visual_injection_004", md)
        self.assertIn("Casos bloqueados correctamente", md)
        self.assertIn("Qué debe comprobar una revisión humana", md)


if __name__ == "__main__":
    unittest.main()
