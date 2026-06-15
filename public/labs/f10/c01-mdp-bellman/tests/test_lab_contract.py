import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH_RE = re.compile(r"`((?:data|contracts|configs|templates|evals|sql|ops|output|output_bad|output_risky|solutions/reference|evidence|policies|runbooks|guides|tests|\.github)/[^`]+|Makefile|requirements\.txt)`")


def collect_referenced_paths():
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8") if readme.exists() else ""
    paths = []
    for raw in PATH_RE.findall(text):
        item = raw.strip().rstrip(".,;:")
        if item.endswith("/"):
            continue
        if "*" in item or "XX" in item or "xx" in item or "tu-entrega" in item or "mi-equipo" in item:
            continue
        paths.append(item)
    return sorted(set(paths))


class LabContractTest(unittest.TestCase):
    def test_referenced_source_files_exist(self):
        missing = []
        for item in collect_referenced_paths():
            if item.startswith(("output/", "output_bad/", "output_risky/", "solutions/reference/")):
                continue
            if not (ROOT / item).exists():
                missing.append(item)
        self.assertEqual(missing, [])

    def test_promised_outputs_exist_after_run(self):
        missing = []
        for item in collect_referenced_paths():
            if item.startswith(("output/", "output_bad/", "output_risky/", "solutions/reference/")) and not (ROOT / item).exists():
                missing.append(item)
        self.assertEqual(missing, [])

    def test_json_outputs_are_valid_json(self):
        invalid = []
        for item in collect_referenced_paths():
            if item.endswith(".json") and item.startswith(("output/", "output_bad/", "output_risky/", "solutions/reference/")):
                path = ROOT / item
                if not path.exists():
                    continue
                try:
                    json.loads(path.read_text(encoding="utf-8"))
                except json.JSONDecodeError as exc:
                    invalid.append(f"{item}: {exc}")
        self.assertEqual(invalid, [])


if __name__ == "__main__":
    unittest.main()
