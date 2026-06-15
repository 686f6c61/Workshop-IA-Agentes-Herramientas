import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TrainInferBudgetKitTests(unittest.TestCase):
    def test_run_separates_training_inference_and_serving_constraints(self):
        result = subprocess.run(
            [sys.executable, "ops/plan_train_infer.py", "--write"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        report = json.loads((ROOT / "output/train_infer_report.json").read_text(encoding="utf-8"))
        decision = (ROOT / "output/train_infer_decision.md").read_text(encoding="utf-8")
        rows = report["results"]

        self.assertGreaterEqual(len(rows), 3)
        self.assertTrue(all("recommendation" in row for row in rows))
        self.assertTrue(any("kv_cache_gb" in row for row in rows))
        self.assertIn("inferencia", decision.lower())


if __name__ == "__main__":
    unittest.main()
