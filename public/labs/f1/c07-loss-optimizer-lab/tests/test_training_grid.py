import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TrainingGridKitTests(unittest.TestCase):
    def test_run_compares_losses_optimizers_and_validation(self):
        result = subprocess.run(
            [sys.executable, "ops/run_training_grid.py", "--write"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        report = json.loads((ROOT / "output/training_report.json").read_text(encoding="utf-8"))
        decision = (ROOT / "output/training_decision.md").read_text(encoding="utf-8")

        self.assertGreaterEqual(len(report), 3)
        self.assertTrue(all("valid" in row and "f1" in row["valid"] for row in report))
        self.assertTrue(any(row.get("optimizer") == "adamw" for row in report))
        self.assertIn("validación", decision.lower())


if __name__ == "__main__":
    unittest.main()
