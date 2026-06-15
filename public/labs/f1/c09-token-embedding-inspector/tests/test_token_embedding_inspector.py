import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TokenEmbeddingInspectorKitTests(unittest.TestCase):
    def test_run_exposes_tokens_vectors_and_similarity(self):
        result = subprocess.run(
            [sys.executable, "ops/inspect_tokens_embeddings.py", "--write"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        report = json.loads((ROOT / "output/token_embedding_report.json").read_text(encoding="utf-8"))
        decision = (ROOT / "output/token_embedding_decision.md").read_text(encoding="utf-8")
        rows = report["results"]

        self.assertTrue(rows)
        self.assertTrue(
            all(
                all("tokens" in text and "embedding_preview" in text for text in row["texts"])
                for row in rows
            )
        )
        self.assertTrue(all("cosine_similarity" in row for row in rows))
        self.assertIn("embedding", decision.lower())


if __name__ == "__main__":
    unittest.main()
