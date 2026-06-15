import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DissectionKitTest(unittest.TestCase):
    def test_required_files_exist(self):
        for relative in [
            "README.md",
            "Makefile",
            "requirements.txt",
            "data/request_case.json",
            "data/toy_vocab.json",
            "contracts/dissection_policy.json",
            "ops/dissect_llm_request.py",
            "templates/entrega.md",
        ]:
            self.assertTrue((ROOT / relative).exists(), relative)

    def test_runner_generates_valid_report(self):
        subprocess.run(
            [sys.executable, "ops/dissect_llm_request.py", "--write", "--fail-on-invalid"],
            cwd=ROOT,
            check=True,
        )
        report = json.loads((ROOT / "output/dissection_report.json").read_text(encoding="utf-8"))
        self.assertTrue(report["gate_valid"], report.get("issues"))
        self.assertEqual(report["sampling"]["selected_first_token"], "{\"categoria\"")
        self.assertGreater(report["prompt_token_count"], 55)
        self.assertIn("kv_cache_gb", report["runtime"])
        self.assertIn("architecture_signals", report)
        self.assertEqual(report["architecture_signals"]["position_encoding"], "RoPE")
        self.assertGreater(report["runtime"]["gqa_kv_cache_saving_percent"], 0)
        self.assertGreater(report["runtime"]["speculative_speedup_toy"], 1)

    def test_markdown_contains_engineering_sections(self):
        subprocess.run([sys.executable, "ops/dissect_llm_request.py", "--write"], cwd=ROOT, check=True)
        text = (ROOT / "output/dissection_report.md").read_text(encoding="utf-8")
        for heading in [
            "## Tokenizacion",
            "## Formas de tensores",
            "## Arquitectura y runtime moderno",
            "## Logits y sampling",
            "## KV cache y runtime",
            "## Decision de ingenieria",
        ]:
            self.assertIn(heading, text)


if __name__ == "__main__":
    unittest.main()
