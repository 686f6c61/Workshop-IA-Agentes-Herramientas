import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DocumentAIPipelineTest(unittest.TestCase):
    def test_required_files_exist(self):
        required = [
            "Makefile",
            "README.md",
            "requirements.txt",
            "contracts/document_ai_policy.json",
            "schemas/document_extraction_schema.json",
            "data/document_cases.json",
            "data/docs/grant_policy_excerpt.md",
            "data/docs/status_history.csv",
            "data/pages/grant_policy_page.svg",
            "data/pages/invoice_page.svg",
            "data/pages/low_quality_scan.svg",
            "data/pages/merged_table_page.svg",
            "data/pages/visual_instruction_doc.svg",
            "ops/run_document_ai_pipeline.py",
            "templates/entrega.md",
        ]
        for relative in required:
            self.assertTrue((ROOT / relative).exists(), relative)

    def test_script_generates_teachable_outputs(self):
        subprocess.run(
            ["python3", "ops/run_document_ai_pipeline.py", "--write", "--fail-on-invalid"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        report = json.loads((ROOT / "output" / "document_ai_report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["gate"], "pass")
        self.assertGreaterEqual(report["case_count"], 5)
        self.assertGreaterEqual(report["review_count"], 3)
        self.assertGreaterEqual(report["block_count"], 1)
        self.assertTrue((ROOT / "output" / "document_ai_report.md").exists())
        self.assertTrue((ROOT / "output" / "document_pipeline.svg").exists())
        self.assertTrue((ROOT / "output" / "table_cells.csv").exists())
        self.assertTrue((ROOT / "output" / "extractions" / "invoice_line_items_002.json").exists())
        self.assertTrue((ROOT / "output" / "extractions" / "visual_instruction_doc_006.json").exists())

    def test_extractions_keep_evidence_and_security(self):
        invoice = json.loads(
            (ROOT / "output" / "extractions" / "invoice_line_items_002.json").read_text(encoding="utf-8")
        )
        self.assertEqual(invoice["decision"], "pass")
        self.assertTrue(invoice["fields"])
        self.assertTrue(invoice["tables"])
        self.assertIn("amount_delta", invoice["tables"][0])
        for field in invoice["fields"]:
            self.assertIn("page", field)
            self.assertIn("bbox", field)
            self.assertIn("region_id", field)

        blocked = json.loads(
            (ROOT / "output" / "extractions" / "visual_instruction_doc_006.json").read_text(encoding="utf-8")
        )
        self.assertEqual(blocked["decision"], "block")
        self.assertIn("untrusted_document_instruction", blocked["block_hits"])
        self.assertIn("dato no confiable", blocked["trusted_instruction_rule"])

    def test_svg_has_project_signature(self):
        svg = (ROOT / "output" / "document_pipeline.svg").read_text(encoding="utf-8")
        self.assertIn("IA para gente curiosa / Facsímil 12 / Capítulo 05 / 686f6c61", svg)
        self.assertIn("Document AI", svg)


if __name__ == "__main__":
    unittest.main()
