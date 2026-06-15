import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PatchTokenizerKitTest(unittest.TestCase):
    def test_required_files_exist(self):
        for relative in [
            "README.md",
            "Makefile",
            "requirements.txt",
            "data/synthetic_ticket.ppm",
            "data/resolution_cases.json",
            "contracts/patch_policy.json",
            "ops/inspect_patches.py",
            "templates/entrega.md",
        ]:
            self.assertTrue((ROOT / relative).exists(), relative)

    def test_runner_generates_report_and_svg(self):
        subprocess.run(
            [sys.executable, "ops/inspect_patches.py", "--write", "--fail-on-invalid"],
            cwd=ROOT,
            check=True,
        )
        report = json.loads((ROOT / "output/patch_report.json").read_text(encoding="utf-8"))
        self.assertTrue(report["valid"], report.get("issues"))
        self.assertEqual(report["visual_token_count"], 16)
        self.assertEqual(report["patch_rows"], 4)
        self.assertEqual(report["patch_cols"], 4)
        self.assertGreater(report["attention_pairs"], report["visual_token_count"])
        self.assertTrue((ROOT / "output/patch_grid.svg").exists())
        self.assertIn(
            "IA para gente curiosa / Facsímil 12 / Capítulo 02 / 686f6c61",
            (ROOT / "output/patch_grid.svg").read_text(encoding="utf-8"),
        )

    def test_resolution_budget_contains_attention_growth(self):
        subprocess.run([sys.executable, "ops/inspect_patches.py", "--write"], cwd=ROOT, check=True)
        report = json.loads((ROOT / "output/patch_report.json").read_text(encoding="utf-8"))
        cases = {item["name"]: item for item in report["resolution_budgets"]}
        self.assertGreater(cases["captura_hd_p16"]["visual_tokens"], cases["vit_base_224_p16"]["visual_tokens"])
        self.assertGreater(
            cases["captura_hd_p16"]["attention_pair_ratio_vs_vit_224_p16"],
            cases["captura_hd_p16"]["token_ratio_vs_vit_224_p16"],
        )


if __name__ == "__main__":
    unittest.main()
