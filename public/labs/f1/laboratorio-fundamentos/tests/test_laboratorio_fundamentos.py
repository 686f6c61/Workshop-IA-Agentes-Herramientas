import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(name, relative_path):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


classifier = load_module("evaluate_classifier", "ops/evaluate_classifier.py")
semantic = load_module("run_semantic_search", "ops/run_semantic_search.py")
checker = load_module("check_student_submission", "ops/check_student_submission.py")


class LaboratorioFundamentosTest(unittest.TestCase):
    def test_classifier_gate_selects_capacity_aware_model(self):
        cases = classifier.read_json(ROOT / "data" / "classifier_cases.json")
        contract = classifier.read_json(ROOT / "contracts" / "fundamentos_lab_contract.json")
        rows = [classifier.metrics_for(model) for model in cases["models"]]
        decision = classifier.decide(rows, contract)

        self.assertEqual(decision["status"], "publicar_piloto")
        self.assertEqual(decision["selected_model"], "modelo_b")
        selected = {row["model_id"]: row for row in rows}["modelo_b"]
        self.assertLessEqual(selected["priority_queue"], contract["priority_review_capacity"])

    def test_semantic_search_traces_every_query(self):
        data = semantic.read_json(ROOT / "data" / "semantic_documents.json")
        results = [semantic.run_case(case, data["documents"], data) for case in data["queries"]]
        metrics = semantic.evaluate(results)

        self.assertEqual(metrics["hit_at_1"], 1.0)
        self.assertEqual(metrics["mrr"], 1.0)
        for result in results:
            span_names = [span["name"] for span in result["trace"]["spans"]]
            self.assertEqual(span_names, ["tokenize_query", "embed_query", "score_documents", "rank"])
            self.assertEqual(result["ranked_docs"][0]["doc_id"], result["expected_doc"])

    def test_reference_submission_passes_checker(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            subprocess.run(
                [sys.executable, "ops/evaluate_classifier.py", "--output-dir", str(tmp_path), "--write"],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                [sys.executable, "ops/run_semantic_search.py", "--output-dir", str(tmp_path), "--write"],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            report = checker.build_report(tmp_path)

        self.assertTrue(report["gate_ok"], json.dumps(report, ensure_ascii=False))
        self.assertEqual(report["score"], report["max_score"])


if __name__ == "__main__":
    unittest.main()
