#!/usr/bin/env python3
import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIELDS = [
    "state_visible",
    "evidence_visible",
    "limits_copy",
    "action_separated",
    "recovery_path",
    "accessibility_copy",
    "trace_available",
    "manual_fallback",
]


def yes(value):
    return str(value).strip().lower() in {"yes", "true", "1", "si", "sí"}


def load_sessions(path):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def score_session(row):
    passed = [field for field in FIELDS if yes(row[field])]
    missing = [field for field in FIELDS if not yes(row[field])]
    score = round(len(passed) / len(FIELDS), 3)
    return {
        "session_id": row["session_id"],
        "scenario": row["scenario"],
        "score": score,
        "success": yes(row["success"]),
        "missing": missing,
    }


def write_outputs(report, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "ux_review_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    gate = {
        "gate": "ux_release_gate",
        "status": "pass" if report["gate_ok"] else "review",
        "overall_score": report["overall_score"],
        "required_fixes": report["required_fixes"],
    }
    (output_dir / "ux_release_gate.json").write_text(json.dumps(gate, indent=2, ensure_ascii=False), encoding="utf-8")
    (output_dir / "ux_decision.md").write_text(ux_decision(report), encoding="utf-8")
    append_final_packet(output_dir, report)


def ux_decision(report):
    fixes = "\n".join(f"- {fix}" for fix in report["required_fixes"]) if report["required_fixes"] else "- Ninguno."
    return f"""# Decisión UX

Score UX global: {report['overall_score']}.

Gate: {"pass" if report['gate_ok'] else "review"}.

## Cambios obligatorios

{fixes}

## Lectura

La experiencia no se considera lista porque una respuesta sea correcta en promedio. Debe mostrar estados, evidencia, límites, separación entre sugerencia y acción, recuperación, accesibilidad, trazas y fallback manual.
"""


def append_final_packet(output_dir, report):
    path = output_dir / "final_product_packet.md"
    existing = path.read_text(encoding="utf-8") if path.exists() else "# Paquete final de producto\n"
    addition = f"""

## Revisión UX

Score UX global: {report['overall_score']}.

Gate UX: {"pass" if report['gate_ok'] else "review"}.

Cambios obligatorios:

{chr(10).join(f"- {fix}" for fix in report["required_fixes"]) if report["required_fixes"] else "- Ninguno."}
"""
    path.write_text(existing.rstrip() + addition, encoding="utf-8")


def build_report(sessions):
    scored = [score_session(row) for row in sessions]
    overall = round(sum(item["score"] for item in scored) / len(scored), 3)
    required_fixes = []
    for item in scored:
        for missing in item["missing"]:
            required_fixes.append(f"{item['scenario']}: falta `{missing}`.")
        if not item["success"]:
            required_fixes.append(f"{item['scenario']}: la sesión no termina en éxito de tarea.")
    gate_ok = overall >= 0.95 and not required_fixes
    return {
        "sessions": scored,
        "overall_score": overall,
        "gate_ok": gate_ok,
        "required_fixes": required_fixes,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sessions", default=ROOT / "data/ux_review_sessions.csv")
    parser.add_argument("--output-dir", default=ROOT / "output")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-review", action="store_true")
    args = parser.parse_args()

    report = build_report(load_sessions(args.sessions))
    if args.write:
        write_outputs(report, Path(args.output_dir))
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if args.fail_on_review and not report["gate_ok"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
