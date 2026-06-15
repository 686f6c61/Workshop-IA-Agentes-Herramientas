import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class BackpropCheckKitTests(unittest.TestCase):
    def test_run_compares_analytic_and_numeric_gradients(self):
        result = subprocess.run(
            [sys.executable, "ops/check_backprop.py", "--write"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        report = json.loads((ROOT / "output/backprop_report.json").read_text(encoding="utf-8"))
        decision = (ROOT / "output/backprop_decision.md").read_text(encoding="utf-8")

        self.assertTrue(report)
        self.assertTrue(all("gradient_check" in row for row in report))
        self.assertTrue(all(row["gradient_check"] for row in report))
        self.assertIn("learning rate", decision.lower())


if __name__ == "__main__":
    unittest.main()
