import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "ops"))

from triage_ai_fit import build_report, render_markdown  # noqa: E402


class TriageAiFitTests(unittest.TestCase):
    def setUp(self):
        self.cases = json.loads((ROOT / "data" / "use_cases.json").read_text(encoding="utf-8"))
        self.policy = json.loads(
            (ROOT / "contracts" / "decision_policy.json").read_text(encoding="utf-8")
        )
        self.rows = build_report(self.cases, self.policy)

    def test_every_case_gets_allowed_recommendation(self):
        allowed = set(self.policy["allowed_recommendations"])
        for row in self.rows:
            self.assertIn(row["recommendation"], allowed, row["id"])

    def test_high_impact_or_external_action_requires_review(self):
        by_id = {case["id"]: case for case in self.cases}
        for row in self.rows:
            case = by_id[row["id"]]
            if case["impact"] >= self.policy["impact_review_threshold"] or case["external_action"]:
                self.assertTrue(row["needs_review"], row["id"])
                self.assertIn("human_review", row["components"], row["id"])

    def test_exact_numbers_do_not_become_llm_only(self):
        for row in self.rows:
            case = next(case for case in self.cases if case["id"] == row["id"])
            if case["needs_exact_number"]:
                self.assertIn("sql_or_deterministic_code", row["components"], row["id"])
                self.assertNotEqual(row["recommendation"], "llm_generation", row["id"])

    def test_controls_are_known_and_markdown_is_explainable(self):
        known_controls = {
            control
            for controls in self.policy["controls"].values()
            for control in controls
        }
        for row in self.rows:
            self.assertTrue(row["reasons"], row["id"])
            self.assertTrue(set(row["controls"]).issubset(known_controls), row["id"])

        markdown = render_markdown(self.rows)
        self.assertIn("LLM genera lenguaje", markdown)
        self.assertIn("revisión humana trazable", markdown)


if __name__ == "__main__":
    unittest.main()
