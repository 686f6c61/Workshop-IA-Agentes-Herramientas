import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class MlClassicBaselineKitTests(unittest.TestCase):
    def test_run_compares_model_against_majority_baseline(self):
        result = subprocess.run(
            [sys.executable, "ops/run_ml_classic_baseline.py", "--write"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        report = json.loads((ROOT / "output/ml_classic_report.json").read_text(encoding="utf-8"))
        decision = (ROOT / "output/ml_classic_decision.md").read_text(encoding="utf-8")

        self.assertIn("model_metrics", report)
        self.assertIn("majority_metrics", report)
        self.assertGreaterEqual(report["model_metrics"]["f1"], report["majority_metrics"]["f1"])
        self.assertTrue({"tp", "tn", "fp", "fn"}.issubset(report["model_metrics"]))
        self.assertIn("baseline", decision.lower())


if __name__ == "__main__":
    unittest.main()
