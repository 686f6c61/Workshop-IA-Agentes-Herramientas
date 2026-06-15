#!/usr/bin/env python3
import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "data" / "final_project_events.csv"
DEFAULT_CONTRACT = ROOT / "contracts" / "final_review_contract.json"
DEFAULT_OUTPUT = ROOT / "output"


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_json(path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def as_float(row, field):
    return float(str(row[field]).replace(",", "."))


def mean(values):
    values = list(values)
    return sum(values) / len(values) if values else 0.0


def pct(value):
    return round(value, 6)


def percentile(values, p):
    values = sorted(values)
    if not values:
        return 0.0
    index = min(len(values) - 1, int(round((len(values) - 1) * p)))
    return values[index]


def group_by(rows, field):
    grouped = defaultdict(list)
    for row in rows:
        grouped[row[field]].append(row)
    return dict(grouped)


def accuracy(rows):
    if not rows:
        return 0.0
    return mean(1 if row["label"] == row["prediction"] else 0 for row in rows)


def miss_rate(rows):
    positives = [row for row in rows if row["label"] == "1"]
    if not positives:
        return 0.0
    return mean(1 if row["prediction"] == "0" else 0 for row in positives)


def validate_schema(rows, contract):
    if not rows:
        return ["dataset vacio"]
    missing = sorted(set(contract["required_columns"]) - set(rows[0]))
    errors = [f"falta columna {field}" for field in missing]
    allowed_splits = set(contract["allowed_splits"])
    for row in rows:
        if row.get("split") not in allowed_splits:
            errors.append(f"split fuera de catalogo: {row.get('case_id')}")
    return errors


def build_report(rows, contract):
    schema_errors = validate_schema(rows, contract)
    test_rows = [row for row in rows if row["split"] == "test"]
    missing_trace_rate = mean(1 if not row["trace_id"] else 0 for row in rows)
    missing_required_fields_rate = mean(1 if row["has_required_fields"] != "1" else 0 for row in rows)
    latency_p95 = percentile([as_float(row, "latency_ms") for row in rows], 0.95)
    citation_valid_rate = mean(as_float(row, "citation_valid") for row in rows)
    split_summary = []
    for split, subset in sorted(group_by(rows, "split").items()):
        split_summary.append({
            "split": split,
            "n": len(subset),
            "accuracy": pct(accuracy(subset)),
            "miss_rate": pct(miss_rate(subset)),
            "accepted_rate": pct(mean(as_float(row, "accepted") for row in subset)),
        })
    slice_summary = []
    for item in contract["critical_slices"]:
        subset = [row for row in rows if row[item["field"]] == item["value"]]
        slice_summary.append({
            "slice": f"{item['field']}={item['value']}",
            "n": len(subset),
            "accuracy": pct(accuracy(subset)),
            "miss_rate": pct(miss_rate(subset)),
            "accepted_rate": pct(mean(as_float(row, "accepted") for row in subset)) if subset else 0,
        })

    slos = contract["slos"]
    checks = [
        {"check": "schema", "status": "block" if schema_errors else "pass", "value": schema_errors},
        {"check": "missing_trace_rate", "status": "block" if missing_trace_rate > slos["max_missing_trace_rate"] else "pass", "value": pct(missing_trace_rate), "threshold": slos["max_missing_trace_rate"]},
        {"check": "missing_required_fields_rate", "status": "block" if missing_required_fields_rate > slos["max_missing_required_fields_rate"] else "pass", "value": pct(missing_required_fields_rate), "threshold": slos["max_missing_required_fields_rate"]},
        {"check": "latency_p95_ms", "status": "review" if latency_p95 > slos["max_latency_p95_ms"] else "pass", "value": pct(latency_p95), "threshold": slos["max_latency_p95_ms"]},
        {"check": "test_accuracy", "status": "review" if accuracy(test_rows) < slos["min_test_accuracy"] else "pass", "value": pct(accuracy(test_rows)), "threshold": slos["min_test_accuracy"]},
        {"check": "citation_valid_rate", "status": "review" if citation_valid_rate < slos["min_citation_valid_rate"] else "pass", "value": pct(citation_valid_rate), "threshold": slos["min_citation_valid_rate"]},
    ]
    for row in slice_summary:
        checks.append({
            "check": f"critical_slice_miss_rate:{row['slice']}",
            "status": "review" if row["miss_rate"] > slos["max_critical_slice_miss_rate"] else "pass",
            "value": row["miss_rate"],
            "threshold": slos["max_critical_slice_miss_rate"],
        })
    statuses = {item["status"] for item in checks}
    status = "block" if "block" in statuses else "review" if "review" in statuses else "pass"
    return {
        "status": status,
        "contract_id": contract.get("contract_id", ""),
        "contract_version": contract.get("versión", ""),
        "checks": checks,
        "split_summary": split_summary,
        "slice_summary": slice_summary,
    }


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def render(report):
    block_checks = [item for item in report["checks"] if item["status"] == "block"]
    review_checks = [item for item in report["checks"] if item["status"] == "review"]
    pass_checks = [item for item in report["checks"] if item["status"] == "pass"]
    lines = [
        "# Decisión final del facsímil 8",
        "",
        f"Estado: **{report['status']}**.",
        "",
        "## Lectura ejecutiva",
        "",
        "Este resultado no dice que el sistema sea inútil. Dice algo más concreto: todavia no hay evidencia operativa suficiente para publicarlo como automatización.",
        "El bloqueo viene de dos condiciones que no se negocian en un sistema de IA aplicado: trazabilidad completa y campos obligatorios completos. Sin esas dos piezas, no se puede reconstruir una decisión ni defender una medición.",
        "",
        "## Resumen técnico",
        "",
        f"- Checks en `pass`: {len(pass_checks)}.",
        f"- Checks en `review`: {len(review_checks)}.",
        f"- Checks en `block`: {len(block_checks)}.",
        "",
        "Interpretacion:",
        "",
        "- `block` impide publicar.",
        "- `review` no impide por sí solo, pero exige plan de corrección y nueva medición.",
        "- `pass` solo significa que ese control concreto no encontro problema con este dataset.",
        "",
        "## Checks",
        "",
        "| Check | Estado | Valor | Umbral |",
        "|---|---|---:|---:|",
    ]
    for item in report["checks"]:
        lines.append(f"| `{item['check']}` | `{item['status']}` | `{item.get('value', '')}` | `{item.get('threshold', '')}` |")
    lines.extend([
        "",
        "## Lectura de los fallos",
        "",
        "| Zona | Lectura | Accion esperada |",
        "|---|---|---|",
        "| Trazabilidad | Hay al menos una fila sin `trace_id`. | No publicar hasta poder reconstruir cada decision. |",
        "| Campos obligatorios | Hay al menos una fila incompleta. | Corregir ingesta, validación y contrato de datos. |",
        "| Latencia | `p95` queda por encima del SLO. | Revisar ruta lenta, proveedor, RAG o fallback. |",
        "| Test | La accuracy de test queda por debajo del mínimo. | Revisar split, datos, umbral y tipos de error. |",
        "| Slices críticos | `language=en`, `segment=practicas` y `source=form` concentran misses. | No fiarse de la media global; corregir esos segmentos antes de automatizar. |",
        "",
        "## Decisión profesional",
        "",
        "No se publica. El proyecto debe corregir trazabilidad, campos obligatorios y slices críticos antes de usar este dataset para automatizar decisiones.",
        "",
        "## Siguiente iteracion",
        "",
        "1. Reparar `trace_id` y validar que todo evento de decision tiene traza.",
        "2. Bloquear en ingesta cualquier fila sin campos obligatorios.",
        "3. Analizar los casos `language=en`, `segment=practicas` y `source=form` como slices de primer nivel.",
        "4. Repetir evaluación con el mismo contrato, no con una metrica elegida después.",
        "5. Si se propone una intervencion, medirla con el kit de experimentos del capítulo 07.",
    ])
    return "\n".join(lines) + "\n"


def source_evidence_rows(contract):
    rows = []
    for item in contract.get("evidence_files", []):
        path = ROOT / item["path"]
        exists = path.exists()
        rows.append({
            "evidence_id": item["id"],
            "chapter": item["chapter"],
            "path": item["path"],
            "exists": str(exists).lower(),
            "purpose": item["purpose"],
        })
    return rows


def render_source_evidence_review(contract):
    rows = source_evidence_rows(contract)
    missing = [row for row in rows if row["exists"] == "false"]
    lines = [
        "# Revision de evidencias fuente",
        "",
        "Este informe comprueba que el laboratorio no se apoya solo en salidas generadas. Cada decision debe conectarse con una evidencia fuente del temario: contrato, trazabilidad, slices, experimento o alcance.",
        "",
        f"- Evidencias declaradas: {len(rows)}.",
        f"- Evidencias ausentes: {len(missing)}.",
        "",
        "| Evidencia | Capitulo | Ruta | Existe | Para que sirve |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| `{row['evidence_id']}` | `{row['chapter']}` | `{row['path']}` | `{row['exists']}` | {row['purpose']} |"
        )
    lines.extend([
        "",
        "## Cómo usarlo",
        "",
        "Primero se mira el estado final. Despues se abre la evidencia fuente que sostiene cada decision. Si un control está en `pass`, el archivo debe existir y debe poder defenderse sin cambiar umbrales después de ver el resultado.",
        "",
    ])
    return "\n".join(lines)


def render_technical_memo(report):
    block_checks = [item for item in report["checks"] if item["status"] == "block"]
    review_checks = [item for item in report["checks"] if item["status"] == "review"]
    lines = [
        "# Memo técnico de decision de datos",
        "",
        f"Decisión recomendada: `{report['status']}`.",
        "",
        "## Motivo",
        "",
    ]
    if block_checks:
        names = ", ".join(f"`{item['check']}`" for item in block_checks)
        lines.append(f"No se publica porque hay controles bloqueantes: {names}.")
    elif review_checks:
        lines.append("No hay controles bloqueantes, pero quedan revisiones abiertas. El sistema solo podría avanzar con alcance limitado y nuevo gate.")
    else:
        lines.append("No hay controles bloqueantes ni revisiones abiertas. Se puede avanzar con seguimiento.")
    lines.extend([
        "",
        "## Checks abiertos",
        "",
        "| Check | Estado | Valor | Umbral |",
        "|---|---|---:|---:|",
    ])
    for item in block_checks + review_checks:
        lines.append(
            f"| `{item['check']}` | `{item['status']}` | `{item.get('value', '')}` | `{item.get('threshold', '')}` |"
        )
    if not block_checks and not review_checks:
        lines.append("| - | - | - | - |")
    lines.extend([
        "",
        "## Recomendación operativa",
        "",
        "No se cambian umbrales después de mirar el resultado. Se corrige trazabilidad, ingesta, slices o experimento, y después se repite el gate con el mismo contrato.",
        "",
    ])
    return "\n".join(lines)


def render_correction_plan(report):
    lines = [
        "# Plan de corrección de datos",
        "",
        "| Prioridad | Problema | Estado | Acción | Capítulo |",
        "|---:|---|---|---|---|",
    ]
    priority = 1
    for item in report["checks"]:
        if item["status"] not in {"block", "review"}:
            continue
        if item["check"] == "missing_trace_rate":
            action = "Completar `trace_id` y comprobar que toda decision se puede reconstruir."
            chapter = "08.06"
        elif item["check"] == "missing_required_fields_rate":
            action = "Bloquear ingesta incompleta antes de crear el dataset de evaluación."
            chapter = "08.02"
        elif item["check"] == "latency_p95_ms":
            action = "Revisar ruta lenta, RAG, proveedor o fallback antes de ampliar alcance."
            chapter = "08.06"
        elif item["check"] == "test_accuracy":
            action = "Revisar split, umbral, errores y representatividad del test."
            chapter = "08.03"
        elif item["check"].startswith("critical_slice_miss_rate"):
            action = "Analizar el slice como unidad de decisión, no esconderlo en la media global."
            chapter = "08.05"
        elif item["check"] == "citation_valid_rate":
            action = "Revisar calidad documental y evidencias de cita."
            chapter = "08.01"
        else:
            action = "Revisar evidencia y repetir gate."
            chapter = "08"
        lines.append(
            f"| {priority} | `{item['check']}` | `{item['status']}` | {action} | `{chapter}` |"
        )
        priority += 1
    if priority == 1:
        lines.append("| - | Sin correcciones abiertas | `pass` | Mantener monitorización. | `08.06` |")
    lines.extend([
        "",
        "## Criterio de cierre",
        "",
        "Una corrección se cierra cuando se regenera el reporte con el mismo contrato y el check deja de bloquear o queda justificado como alcance limitado.",
        "",
        "La entrega no puede cambiar `final_review_contract.json` para parecer mejor. Debe demostrar que `trace_id` permite reconstruir cada decisión y que `has_required_fields` bloquea filas incompletas antes de crear el dataset de evaluación.",
        "",
    ])
    return "\n".join(lines)


def weakest_slice(report):
    if not report["slice_summary"]:
        return None
    return max(report["slice_summary"], key=lambda row: row["miss_rate"])


def render_next_experiment_plan(report):
    slice_row = weakest_slice(report)
    target = slice_row["slice"] if slice_row else "slice_no_definido"
    lines = [
        "# Plan de siguiente experimento",
        "",
        f"Slice prioritario: `{target}`.",
        "",
        "## Hipótesis",
        "",
        "Una plantilla guiada y una recuperación documental revisada para el slice prioritario reducirán fallos sin romper citas, latencia ni feedback.",
        "",
        "## Diseño",
        "",
        "| Pieza | Decisión |",
        "|---|---|",
        "| Unidad | `case_id`. |",
        "| Tratamiento | Plantilla guiada + recuperación documental revisada. |",
        "| Control | Flujo actual. |",
        "| Métrica primaria | `resolved_day_7`. |",
        "| Guardrails | `citation_valid`, `latency_ms`, `negative_feedback`, `cost_eur`. |",
        "| Exposure event | `case_id`, variante, versión de prompt, versión de retriever y `trace_id`. |",
        "| Decisión si queda en review | No rollout general; ampliar muestra, corregir instrumentación o limitar alcance. |",
        "",
        "## Conexión con el capítulo 07",
        "",
        "Este plan no demuestra causalidad por estar escrito. Debe ejecutarse con asignación, exposición real, ventana de maduración y regla de analisis definida antes de mirar resultados.",
        "",
    ]
    return "\n".join(lines)


def ci_gate(report, contract, data_path):
    try:
        dataset = str(data_path.resolve().relative_to(ROOT))
    except ValueError:
        dataset = str(data_path)
    return {
        "status": report["status"],
        "block_count": sum(1 for item in report["checks"] if item["status"] == "block"),
        "review_count": sum(1 for item in report["checks"] if item["status"] == "review"),
        "contract_id": contract.get("contract_id", ""),
        "contract_version": contract.get("versión", ""),
        "dataset": dataset,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-blocker", action="store_true")
    args = parser.parse_args()
    rows = read_csv(args.data)
    contract = read_json(args.contract)
    report = build_report(rows, contract)
    if args.write:
        write_json(args.output_dir / "final_review_report.json", report)
        write_csv(args.output_dir / "final_split_summary.csv", report["split_summary"])
        write_csv(args.output_dir / "final_slice_summary.csv", report["slice_summary"])
        write_csv(args.output_dir / "source_evidence_matrix.csv", source_evidence_rows(contract))
        (args.output_dir / "final_decision.md").write_text(render(report), encoding="utf-8")
        (args.output_dir / "technical_decision_memo.md").write_text(render_technical_memo(report), encoding="utf-8")
        (args.output_dir / "source_evidence_review.md").write_text(render_source_evidence_review(contract), encoding="utf-8")
        (args.output_dir / "correction_plan.md").write_text(render_correction_plan(report), encoding="utf-8")
        (args.output_dir / "next_experiment_plan.md").write_text(render_next_experiment_plan(report), encoding="utf-8")
        write_json(args.output_dir / "data_release_ci_gate.json", ci_gate(report, contract, args.data))
    else:
        print(json.dumps(report, indent=2, ensure_ascii=False))

    if args.fail_on_blocker and report["status"] == "block":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
