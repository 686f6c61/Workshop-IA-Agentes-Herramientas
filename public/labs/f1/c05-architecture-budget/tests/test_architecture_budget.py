import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ArchitectureBudgetKitTests(unittest.TestCase):
    def test_run_computes_parameters_and_review_decisions(self):
        result = subprocess.run(
            [sys.executable, "ops/audit_architectures.py", "--write"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        report = json.loads((ROOT / "output/architecture_report.json").read_text(encoding="utf-8"))
        decision = (ROOT / "output/architecture_decision.md").read_text(encoding="utf-8")

        self.assertGreaterEqual(len(report), 3)
        self.assertTrue(all("total_parameters" in row for row in report if row.get("valid")))
        self.assertTrue(any(row.get("warnings") for row in report if row.get("valid")))
        self.assertIn("parámetros", decision.lower())


if __name__ == "__main__":
    unittest.main()
