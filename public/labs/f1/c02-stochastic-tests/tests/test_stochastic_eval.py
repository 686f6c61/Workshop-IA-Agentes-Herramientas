import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "ops"))

from run_stochastic_eval import evaluate_case, render_decision, softmax  # noqa: E402


class StochasticEvalTests(unittest.TestCase):
    def setUp(self):
        self.policy = json.loads((ROOT / "contracts" / "eval_policy.json").read_text())
        self.cases = json.loads((ROOT / "data" / "sampling_cases.json").read_text())

    def test_softmax_is_distribution(self):
        probabilities = softmax([4.0, 2.0, 1.0], temperature=1.0)
        self.assertAlmostEqual(sum(probabilities), 1.0, places=7)
        self.assertGreater(probabilities[0], probabilities[1])
        self.assertGreater(probabilities[1], probabilities[2])

    def test_temperature_zero_is_deterministic_argmax(self):
        probabilities = softmax([4.0, 2.0, 1.0], temperature=0)
        self.assertEqual(probabilities, [1.0, 0.0, 0.0])

    def test_property_eval_survives_variants_better_than_exact_match(self):
        case = next(case for case in self.cases if case["id"] == "rust_definition")
        row = evaluate_case(case, self.policy, temperature=0.9)
        self.assertGreater(row["property_pass_rate"], row["exact_pass_rate"])
        self.assertTrue(row["gate_pass"])

    def test_high_temperature_can_block_structured_output(self):
        case = next(case for case in self.cases if case["id"] == "json_priority")
        row = evaluate_case(case, self.policy, temperature=1.4)
        self.assertFalse(row["gate_pass"])
        self.assertLess(row["property_pass_rate"], self.policy["property_pass_min"])

    def test_decision_markdown_names_the_contract(self):
        rows = [evaluate_case(self.cases[0], self.policy, temperature=0.9)]
        markdown = render_decision(rows, self.policy)
        self.assertIn("assert exacto", markdown)
        self.assertIn("evaluación de propiedades", markdown)


if __name__ == "__main__":
    unittest.main()
