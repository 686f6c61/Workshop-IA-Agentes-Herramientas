from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class MultimodalRagKitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.run_result = subprocess.run(
            ["python3", "ops/run_multimodal_rag_audit.py"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        cls.report = json.loads((ROOT / "output/multimodal_rag_report.json").read_text(encoding="utf-8"))

    def test_script_runs(self):
        self.assertEqual(self.run_result.returncode, 0, self.run_result.stdout)

    def test_expected_decisions_are_present(self):
        decisions = {item["query_id"]: item["decision"] for item in self.report["results"]}
        self.assertEqual(decisions["q01_beca_envio"], "answer")
        self.assertEqual(decisions["q02_factura_total"], "answer")
        self.assertEqual(decisions["q03_piloto_metricas"], "answer")
        self.assertEqual(decisions["q04_instruccion_visual"], "block")
        self.assertEqual(decisions["q05_pregunta_sin_evidencia"], "review")

    def test_answer_cards_are_downloadable_artifacts(self):
        for query_id in ["q01_beca_envio", "q02_factura_total", "q04_instruccion_visual"]:
            path = ROOT / "output/answer_cards" / f"{query_id}.json"
            self.assertTrue(path.exists(), path)
            card = json.loads(path.read_text(encoding="utf-8"))
            self.assertIn("evidence", card)
            self.assertIn("limits", card)
            self.assertIn("next_action", card)

    def test_visual_instruction_blocks(self):
        unsafe = next(item for item in self.report["results"] if item["query_id"] == "q04_instruccion_visual")
        self.assertIn("visual_instruction_override", unsafe["security_flags"])
        self.assertEqual(unsafe["decision"], "block")
        self.assertNotIn("aprobada", unsafe["answer"].lower())

    def test_zip_contains_operational_entries(self):
        required = [
            "README.md",
            "Makefile",
            "contracts/multimodal_rag_policy.json",
            "data/multimodal_corpus.json",
            "data/rag_queries.json",
            "data/qrels.json",
            "ops/run_multimodal_rag_audit.py",
            "templates/entrega.md",
        ]
        for relative in required:
            self.assertTrue((ROOT / relative).exists(), relative)

    def test_retrieval_metrics_include_qrels_based_scores(self):
        first = self.report["results"][0]["metrics"]
        self.assertIn("ndcg_at_k", first)
        self.assertIn("mrr", first)
        self.assertGreater(first["ndcg_at_k"], 0)


if __name__ == "__main__":
    unittest.main()
