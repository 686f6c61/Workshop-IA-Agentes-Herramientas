import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class NeuronContractKitTests(unittest.TestCase):
    def test_run_validates_dimensions_and_outputs(self):
        result = subprocess.run(
            [sys.executable, "ops/run_neuron_contract.py", "--write"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        report = json.loads((ROOT / "output/neuron_report.json").read_text(encoding="utf-8"))
        decision = (ROOT / "output/neuron_decision.md").read_text(encoding="utf-8")
        valid_rows = [row for row in report if row.get("valid")]
        invalid_rows = [row for row in report if not row.get("valid")]

        self.assertTrue(valid_rows)
        self.assertTrue(invalid_rows)
        self.assertTrue(all("z" in row and "output" in row for row in valid_rows))
        self.assertIn("dimensión", decision.lower())


if __name__ == "__main__":
    unittest.main()
