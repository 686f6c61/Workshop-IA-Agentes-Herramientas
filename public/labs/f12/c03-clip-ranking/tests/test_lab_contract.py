import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ClipRankingLabTest(unittest.TestCase):
    def test_required_files_exist(self):
        required = [
            "Makefile",
            "README.md",
            "requirements.txt",
            "contracts/retrieval_policy.json",
            "data/catalog_pairs.json",
            "ops/run_contrastive_ranking.py",
            "templates/entrega.md",
        ]
        for relative in required:
            self.assertTrue((ROOT / relative).exists(), relative)

    def test_script_generates_report(self):
        subprocess.run(
            ["python3", "ops/run_contrastive_ranking.py", "--write", "--fail-on-invalid"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        report = json.loads((ROOT / "output" / "clip_ranking_report.json").read_text(encoding="utf-8"))
        self.assertTrue(report["gate_ok"])
        self.assertGreaterEqual(report["metrics"]["image_to_text_recall_at_1"], 0.6)
        self.assertGreaterEqual(report["metrics"]["text_to_image_recall_at_1"], 0.6)
        self.assertIn("symmetric_loss", report["loss"])
        self.assertGreaterEqual(len(report["hard_negatives"]), 1)

    def test_outputs_are_teachable(self):
        svg = (ROOT / "output" / "contrastive_matrix.svg").read_text(encoding="utf-8")
        md = (ROOT / "output" / "clip_ranking_report.md").read_text(encoding="utf-8")
        self.assertIn("IA para gente curiosa / Facsímil 12 / Capítulo 03 / 686f6c61", svg)
        self.assertIn("Negativos duros", md)
        self.assertIn("Consultas externas", md)


if __name__ == "__main__":
    unittest.main()
