from __future__ import annotations

import csv
import json
import math
import re
from collections import defaultdict
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "contracts/eval_policy.json"
CASES_PATH = ROOT / "data/eval_cases.json"
OUTPUT = ROOT / "output"
SIGNATURE = "IA para gente curiosa / Facsímil 12 / Capítulo 10 / 686f6c61"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def normalize(text: str) -> str:
    text = text.lower()
    text = text.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
    text = re.sub(r"[^a-z0-9%]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def temporal_iou(expected: list[float], predicted: list[float] | None) -> float:
    if not predicted:
        return 0.0
    start = max(float(expected[0]), float(predicted[0]))
    end = min(float(expected[1]), float(predicted[1]))
    intersection = max(0.0, end - start)
    union = max(float(expected[1]), float(predicted[1])) - min(float(expected[0]), float(predicted[0]))
    return 0.0 if union <= 0 else intersection / union


def answer_score(case: dict) -> tuple[float, str]:
    expected = case["expected"]
    output = case["model_output"]
    kind = expected["answer_kind"]
    answer = normalize(output.get("answer", ""))
    accepted = [normalize(item) for item in expected.get("accepted_answers", [])]

    if kind == "numeric":
        expected_value = float(expected["numeric_value"])
        predicted = output.get("numeric_value")
        if predicted is None:
            return 0.0, "sin_numero_predicho"
        tolerance = abs(expected_value) * (float(expected.get("numeric_tolerance_pct", 0.0)) / 100.0)
        ok = abs(float(predicted) - expected_value) <= tolerance
        return (1.0 if ok else 0.0), "numeric_ok" if ok else "numeric_mismatch"

    if kind == "temporal":
        iou = temporal_iou(expected["temporal_span_seconds"], output.get("temporal_span_seconds"))
        if iou >= 0.5:
            return 1.0, "temporal_iou_ok"
        if iou > 0:
            return round(iou, 4), "temporal_overlap_partial"
        return 0.0, "temporal_mismatch"

    if kind == "decision":
        if output.get("decision") == expected.get("decision"):
            return 1.0, "decision_ok"
        if any(item in answer for item in accepted):
            return 0.8, "decision_text_partial"
        return 0.0, "decision_mismatch"

    if any(item and item in answer for item in accepted):
        return 1.0, "exact_or_alias_ok"
    return 0.0, "answer_mismatch"


def evidence_score(case: dict) -> tuple[float, str]:
    expected = set(case["expected"].get("evidence_ids", []))
    cited = set(case["model_output"].get("cited_evidence_ids", []))
    if not expected:
        return 1.0, "no_evidence_required"
    coverage = len(expected & cited) / len(expected)
    if coverage >= 1.0:
        return 1.0, "evidence_complete"
    if coverage > 0:
        return round(coverage, 4), "evidence_partial"
    return 0.0, "evidence_missing"


def unsupported_claim_rate(case: dict) -> float:
    claims = case["model_output"].get("claims", [])
    if not claims:
        return 0.0
    unsupported = sum(1 for claim in claims if not claim.get("supported_by_evidence", False))
    return unsupported / len(claims)


def score_case(case: dict, policy: dict) -> dict:
    answer, answer_reason = answer_score(case)
    evidence, evidence_reason = evidence_score(case)
    unsupported_rate = unsupported_claim_rate(case)
    claim_support = 1.0 - unsupported_rate
    safety = 0.0 if case["model_output"].get("pii_leak", False) else 1.0
    weights = policy["weights"]
    case_score = (
        weights["answer"] * answer
        + weights["evidence"] * evidence
        + weights["claim_support"] * claim_support
        + weights["safety"] * safety
    )

    failures = []
    gates = policy["quality_gates"]
    if case_score < gates["min_case_score"]:
        failures.append("case_score_bajo")
    if evidence < gates["min_evidence_score"] and not case["model_output"].get("model_refused", False):
        failures.append("evidencia_insuficiente")
    if unsupported_rate > gates["max_unsupported_claim_rate"]:
        failures.append("claims_no_soportados")
    if case["model_output"].get("latency_ms", 0) > gates["max_latency_ms"]:
        failures.append("latencia_alta")
    if case["model_output"].get("cost_usd", 0) > gates["max_cost_usd"]:
        failures.append("coste_alto")
    if gates["block_on_pii_leak"] and case["model_output"].get("pii_leak", False):
        failures.append("pii_leak")

    if "pii_leak" in failures:
        decision = "block"
    elif failures:
        decision = "review"
    else:
        decision = "pass"

    return {
        "case_id": case["case_id"],
        "title": case["title"],
        "modality": case["modality"],
        "task_type": case["task_type"],
        "slice_tags": case["slice_tags"],
        "answer_score": round(answer, 4),
        "answer_reason": answer_reason,
        "evidence_score": round(evidence, 4),
        "evidence_reason": evidence_reason,
        "unsupported_claim_rate": round(unsupported_rate, 4),
        "safety_score": safety,
        "case_score": round(case_score, 4),
        "latency_ms": case["model_output"].get("latency_ms", 0),
        "cost_usd": case["model_output"].get("cost_usd", 0),
        "decision": decision,
        "failures": failures,
        "next_action": next_action(failures, case),
    }


def next_action(failures: list[str], case: dict) -> str:
    if not failures:
        return "Mantener en baseline y vigilar regresiones."
    if "evidencia_insuficiente" in failures:
        return "Revisar recuperación/citas: la respuesta no se puede defender con evidencias."
    if "claims_no_soportados" in failures:
        return "Reducir afirmaciones libres o exigir extracción de evidencias antes de responder."
    if "latencia_alta" in failures:
        return "Reducir frames, páginas, audio o llamadas; medir p95 por paso."
    if "pii_leak" in failures:
        return "Bloquear publicación y revisar política de privacidad."
    if case["task_type"] == "temporal_localization":
        return "Añadir evaluación de timestamps e IoU temporal."
    return "Enviar a anotación humana y convertir en test de regresión."


def aggregate_slices(scored_cases: list[dict]) -> list[dict]:
    buckets = defaultdict(list)
    for item in scored_cases:
        for tag in item["slice_tags"]:
            buckets[tag].append(item)
    rows = []
    for tag, items in sorted(buckets.items()):
        rows.append(
            {
                "slice": tag,
                "case_count": len(items),
                "avg_case_score": round(sum(item["case_score"] for item in items) / len(items), 4),
                "avg_evidence_score": round(sum(item["evidence_score"] for item in items) / len(items), 4),
                "review_count": sum(item["decision"] == "review" for item in items),
                "block_count": sum(item["decision"] == "block" for item in items),
                "p95_latency_ms": percentile([item["latency_ms"] for item in items], 0.95),
                "total_cost_usd": round(sum(item["cost_usd"] for item in items), 4),
            }
        )
    return rows


def percentile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    values = sorted(values)
    index = (len(values) - 1) * q
    lower = math.floor(index)
    upper = math.ceil(index)
    if lower == upper:
        return float(values[int(index)])
    weight = index - lower
    return round(values[lower] * (1 - weight) + values[upper] * weight, 2)


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    normalized_rows = []
    for row in rows:
        clean_row = dict(row)
        if isinstance(clean_row.get("failures"), list):
            clean_row["failures"] = "|".join(clean_row["failures"])
        normalized_rows.append(clean_row)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(normalized_rows)


def gate_summary(scored_cases: list[dict], slice_rows: list[dict], policy: dict) -> dict:
    overall = sum(item["case_score"] for item in scored_cases) / len(scored_cases)
    failing_slices = [
        row["slice"]
        for row in slice_rows
        if row["avg_case_score"] < policy["quality_gates"]["min_slice_score"]
    ]
    required_missing = sorted(set(policy["required_slices"]) - {row["slice"] for row in slice_rows})
    blockers = [item["case_id"] for item in scored_cases if item["decision"] == "block"]
    reviews = [item["case_id"] for item in scored_cases if item["decision"] == "review"]
    decision = "pass"
    if blockers or required_missing:
        decision = "block_release"
    elif overall < policy["quality_gates"]["min_overall_score"] or failing_slices or reviews:
        decision = "review_before_release"
    return {
        "overall_score": round(overall, 4),
        "decision": decision,
        "review_cases": reviews,
        "block_cases": blockers,
        "failing_slices": failing_slices,
        "missing_required_slices": required_missing,
        "total_cost_usd": round(sum(item["cost_usd"] for item in scored_cases), 4),
        "p95_latency_ms": percentile([item["latency_ms"] for item in scored_cases], 0.95),
    }


def write_markdown(scored_cases: list[dict], slice_rows: list[dict], gate: dict) -> None:
    lines = [
        "# Informe de evaluación multimodal",
        "",
        f"Decisión: `{gate['decision']}`",
        f"Score global: `{gate['overall_score']}`",
        f"p95 latency: `{gate['p95_latency_ms']} ms`",
        f"Coste total estimado: `${gate['total_cost_usd']}`",
        "",
        "## Casos",
        "",
        "| Caso | Modalidad | Score | Evidencia | Unsupported claims | Decisión | Siguiente acción |",
        "|---|---|---:|---:|---:|---|---|",
    ]
    for item in scored_cases:
        lines.append(
            f"| `{item['case_id']}` | {item['modality']} | {item['case_score']} | {item['evidence_score']} | "
            f"{item['unsupported_claim_rate']} | `{item['decision']}` | {item['next_action']} |"
        )
    lines.extend(["", "## Slices", "", "| Slice | Casos | Score | Evidencia | Revisiones | Bloqueos | p95 latency | Coste |", "|---|---:|---:|---:|---:|---:|---:|---:|"])
    for row in slice_rows:
        lines.append(
            f"| `{row['slice']}` | {row['case_count']} | {row['avg_case_score']} | {row['avg_evidence_score']} | "
            f"{row['review_count']} | {row['block_count']} | {row['p95_latency_ms']} | ${row['total_cost_usd']} |"
        )
    lines.extend(
        [
            "",
            "## Lectura de ingeniería",
            "",
            "- Si el score global parece aceptable pero un slice falla, no publiques sin revisar ese slice.",
            "- Una respuesta numéricamente correcta sin evidencia no es suficientemente defendible.",
            "- En vídeo, evalúa timestamp o IoU temporal; no basta con una respuesta textual.",
            "- En computer use, evalúa trayectoria y permisos, no solo el estado final.",
            "- La cola de anotación convierte fallos reales en nuevos tests de regresión.",
        ]
    )
    (OUTPUT / "eval_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_annotation_queue(scored_cases: list[dict]) -> None:
    rows = [
        {
            "case_id": item["case_id"],
            "title": item["title"],
            "modality": item["modality"],
            "decision": item["decision"],
            "failures": "|".join(item["failures"]),
            "review_instruction": item["next_action"],
        }
        for item in scored_cases
        if item["decision"] != "pass"
    ]
    write_csv(
        OUTPUT / "annotation_queue.csv",
        rows,
        ["case_id", "title", "modality", "decision", "failures", "review_instruction"],
    )


def write_svg(slice_rows: list[dict], gate: dict) -> None:
    width = 1180
    height = 760
    chart_x = 84
    chart_y = 164
    row_h = 44
    max_bar = 460
    rows_svg = []
    for idx, row in enumerate(slice_rows[:10]):
        y = chart_y + idx * row_h
        bar = int(max_bar * row["avg_case_score"])
        rows_svg.append(f'<text x="{chart_x}" y="{y + 18}" font-size="12" fill="#111111">{escape(row["slice"])}</text>')
        rows_svg.append(f'<rect x="{chart_x + 230}" y="{y}" width="{max_bar}" height="24" fill="#F3F3F3" stroke="#111111" stroke-width="0.8"/>')
        rows_svg.append(f'<rect x="{chart_x + 230}" y="{y}" width="{bar}" height="24" fill="#111111"/>')
        rows_svg.append(f'<text x="{chart_x + 710}" y="{y + 18}" font-size="12" fill="#111111">{row["avg_case_score"]:.2f}</text>')
        rows_svg.append(f'<text x="{chart_x + 790}" y="{y + 18}" font-size="12" fill="#555555">rev {row["review_count"]} · p95 {row["p95_latency_ms"]} ms</text>')

    svg = f'''<svg viewBox="0 0 {width} {height}" role="img" aria-labelledby="f12c10-title f12c10-desc" xmlns="http://www.w3.org/2000/svg">
  <title id="f12c10-title">Evaluación multimodal por slices</title>
  <desc id="f12c10-desc">Panel con score por slice, revisiones, latencia y decisión global.</desc>
  <rect width="{width}" height="{height}" fill="#FFFFFF"/>
  <text x="62" y="58" font-size="28" font-weight="700" fill="#111111">Evaluación multimodal: calidad, evidencia y coste</text>
  <text x="62" y="88" font-size="15" fill="#555555">No basta con acertar: hay que acertar con evidencia, por slice, dentro de coste y latencia.</text>
  <rect x="62" y="118" width="1056" height="496" fill="#FFFFFF" stroke="#111111" stroke-width="1.2"/>
  <text x="84" y="142" font-size="13" font-weight="700" fill="#111111">Slice</text>
  <text x="314" y="142" font-size="13" font-weight="700" fill="#111111">Score</text>
  <text x="874" y="142" font-size="13" font-weight="700" fill="#111111">Revisión y latencia</text>
  {''.join(rows_svg)}
  <rect x="62" y="646" width="1056" height="56" fill="#F7F7F7" stroke="#111111" stroke-width="1.2"/>
  <text x="84" y="680" font-size="14" font-weight="700" fill="#111111">Decisión global</text>
  <text x="220" y="680" font-size="14" fill="#111111">{escape(gate["decision"])} · score {gate["overall_score"]} · p95 {gate["p95_latency_ms"]} ms · coste ${gate["total_cost_usd"]}</text>
  <text x="1092" y="724" text-anchor="end" font-size="11" fill="#999999">{SIGNATURE}</text>
</svg>
'''
    (OUTPUT / "multimodal_eval_dashboard.svg").write_text(svg, encoding="utf-8")


def main() -> None:
    policy = load_json(POLICY_PATH)
    cases = load_json(CASES_PATH)
    OUTPUT.mkdir(exist_ok=True)
    scored_cases = [score_case(case, policy) for case in cases]
    slice_rows = aggregate_slices(scored_cases)
    gate = gate_summary(scored_cases, slice_rows, policy)

    report = {
        "schema_version": "1.0",
        "project": "IA para gente curiosa",
        "fasciculo": 12,
        "capitulo": 10,
        "policy": policy,
        "gate": gate,
        "cases": scored_cases,
        "slices": slice_rows,
    }
    (OUTPUT / "eval_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(scored_cases, slice_rows, gate)
    write_csv(
        OUTPUT / "case_scores.csv",
        scored_cases,
        [
            "case_id",
            "title",
            "modality",
            "task_type",
            "answer_score",
            "evidence_score",
            "unsupported_claim_rate",
            "safety_score",
            "case_score",
            "latency_ms",
            "cost_usd",
            "decision",
            "failures",
            "next_action",
        ],
    )
    write_csv(
        OUTPUT / "slice_scores.csv",
        slice_rows,
        ["slice", "case_count", "avg_case_score", "avg_evidence_score", "review_count", "block_count", "p95_latency_ms", "total_cost_usd"],
    )
    write_annotation_queue(scored_cases)
    (OUTPUT / "regression_gate.json").write_text(json.dumps(gate, indent=2, ensure_ascii=False), encoding="utf-8")
    (OUTPUT / "regression_gate.md").write_text(
        f"# Gate de regresión multimodal\n\nDecisión: `{gate['decision']}`\n\nScore global: `{gate['overall_score']}`\n\nCasos a revisar: {', '.join(gate['review_cases']) or 'ninguno'}\n",
        encoding="utf-8",
    )
    write_svg(slice_rows, gate)
    print(f"OK: {len(scored_cases)} casos evaluados; decisión {gate['decision']} en {OUTPUT}")


if __name__ == "__main__":
    main()
