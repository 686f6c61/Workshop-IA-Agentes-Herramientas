import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ArchitectureTriageKitTests(unittest.TestCase):
    def test_run_selects_architecture_with_cost_signals(self):
        result = subprocess.run(
            [sys.executable, "ops/audit_architecture_triage.py", "--write"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        report = json.loads((ROOT / "output/architecture_triage_report.json").read_text(encoding="utf-8"))
        decision = (ROOT / "output/architecture_triage_decision.md").read_text(encoding="utf-8")
        rows = report["results"]

        self.assertGreaterEqual(len(rows), 3)
        self.assertTrue(all("recommendation" in row for row in rows))
        self.assertTrue(
            any(
                any(any("attention" in key for key in candidate) for candidate in row["candidates"])
                for row in rows
            )
        )
        self.assertIn("arquitectura", decision.lower())


if __name__ == "__main__":
    unittest.main()
