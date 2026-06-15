import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PrincipleRouterKitTests(unittest.TestCase):
    def test_run_generates_defensible_decision(self):
        result = subprocess.run(
            [sys.executable, "ops/route_ai_principles.py", "--write"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        report = json.loads((ROOT / "output/principle_report.json").read_text(encoding="utf-8"))
        decision = (ROOT / "output/principle_decision.md").read_text(encoding="utf-8")

        self.assertGreaterEqual(len(report), 3)
        self.assertTrue(all("primary_principle" in row for row in report))
        self.assertIn("Decisión", decision)
        self.assertIn("principio", decision.lower())


if __name__ == "__main__":
    unittest.main()
