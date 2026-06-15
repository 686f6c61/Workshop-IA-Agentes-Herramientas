#!/usr/bin/env python3
"""Compatibilidad para el ejemplo largo del capítulo 10.

Ejecuta la práctica C10 y escribe `report.json` en la raíz del kit para que
una CI sencilla pueda consumirlo sin conocer la estructura interna.
"""

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def main():
    subprocess.run(
        [
            sys.executable,
            "ops/run_f5_practices.py",
            "--chapter",
            "c10",
            "--write",
            "--fail-on-invalid",
        ],
        cwd=ROOT,
        check=True,
    )
    source = ROOT / "output" / "c10_report.json"
    report = json.loads(source.read_text(encoding="utf-8"))
    (ROOT / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "report": "report.json"}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

