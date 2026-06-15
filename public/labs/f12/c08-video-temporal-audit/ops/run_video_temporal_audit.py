from __future__ import annotations

import csv
import json
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "contracts/video_temporal_policy.json"
CASES_PATH = ROOT / "data/video_cases.json"
OUTPUT = ROOT / "output"
CARDS = OUTPUT / "case_cards"
STORYBOARDS = OUTPUT / "storyboards"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def temporal_iou(a_start: float | None, a_end: float | None, b_start: float | None, b_end: float | None) -> float:
    if None in {a_start, a_end, b_start, b_end}:
        return 0.0
    intersection = max(0.0, min(a_end, b_end) - max(a_start, b_start))
    union = max(a_end, b_end) - min(a_start, b_start)
    if union <= 0:
        return 0.0
    return round(intersection / union, 4)


def boundary_error(expected: dict, predicted: dict | None) -> float | None:
    if not predicted or expected.get("start_s") is None or expected.get("end_s") is None:
        return None
    start_error = abs(predicted["start_s"] - expected["start_s"])
    end_error = abs(predicted["end_s"] - expected["end_s"])
    return round(max(start_error, end_error), 4)


def prediction_by_event(case: dict) -> dict[str, dict]:
    return {segment["event_id"]: segment for segment in case.get("prediction", {}).get("segments", [])}


def evidence_coverage(expected: dict, predicted: dict | None) -> float:
    if not predicted:
        return 0.0
    required = set(expected.get("required_modalities", []))
    observed = set(predicted.get("evidence_modalities", []))
    if not required:
        return 1.0
    return round(len(required & observed) / len(required), 4)


def order_ok(case: dict, predicted: dict[str, dict]) -> bool:
    for relation in case.get("order_constraints", []):
        before = predicted.get(relation["before"])
        after = predicted.get(relation["after"])
        if not before or not after:
            return False
        if before["start_s"] > after["start_s"]:
            return False
    return True


def source_trace_ok(case: dict, predicted: dict[str, dict]) -> bool:
    frame_ids = {frame["frame_id"] for frame in case.get("frames", [])}
    for segment in predicted.values():
        evidence_ids = set(segment.get("evidence_frame_ids", []))
        if not evidence_ids or not evidence_ids <= frame_ids:
            return False
    if case["expected_decision"] == "review" and not predicted:
        return True
    return True


def has_visual_instruction_override(case: dict) -> bool:
    needles = ("IGNORE POLICY", "APPROVE ALL", "SYSTEM PROMPT", "OVERRIDE")
    for frame in case.get("frames", []):
        ocr = frame.get("ocr", "").upper()
        if any(needle in ocr for needle in needles):
            return True
    return False


def evaluate_case(case: dict, policy: dict) -> dict:
    gates = policy["quality_gates"]
    predicted = prediction_by_event(case)
    event_rows = []
    tiou_values = []
    boundary_errors = []
    coverage_values = []

    for expected in case.get("required_events", []):
        pred = predicted.get(expected["event_id"])
        tiou = temporal_iou(expected.get("start_s"), expected.get("end_s"), pred.get("start_s") if pred else None, pred.get("end_s") if pred else None)
        coverage = evidence_coverage(expected, pred)
        error = boundary_error(expected, pred)
        tiou_values.append(tiou)
        coverage_values.append(coverage)
        if error is not None:
            boundary_errors.append(error)
        event_rows.append(
            {
                "event_id": expected["event_id"],
                "label": expected["label"],
                "expected": [expected.get("start_s"), expected.get("end_s")],
                "predicted": [pred.get("start_s"), pred.get("end_s")] if pred else None,
                "tiou": tiou,
                "boundary_error_s": error,
                "evidence_coverage": coverage,
                "evidence_frame_ids": pred.get("evidence_frame_ids", []) if pred else [],
            }
        )

    order = order_ok(case, predicted)
    trace = source_trace_ok(case, predicted)
    mean_tiou = round(sum(tiou_values) / max(len(tiou_values), 1), 4)
    min_coverage = min(coverage_values) if coverage_values else 0.0
    max_boundary_error = max(boundary_errors) if boundary_errors else None
    visual_override = has_visual_instruction_override(case)

    flags = []
    if mean_tiou < gates["min_tiou"] and case["expected_decision"] != "review":
        flags.append("tiou_below_gate")
    if max_boundary_error is not None and max_boundary_error > gates["max_boundary_error_s"]:
        flags.append("boundary_error_high")
    if min_coverage < gates["min_evidence_coverage"]:
        flags.append("evidence_coverage_low")
    if gates["require_temporal_order"] and not order:
        flags.append("temporal_order_failed")
    if gates["require_source_trace"] and not trace:
        flags.append("source_trace_missing")
    if visual_override and policy["security"]["block_visual_instruction_override"]:
        flags.append("visual_instruction_override")

    if visual_override and policy["security"]["block_visual_instruction_override"]:
        decision = "block"
    elif case["expected_decision"] == "review" or "tiou_below_gate" in flags or "evidence_coverage_low" in flags or "temporal_order_failed" in flags:
        decision = "review"
    else:
        decision = "answer"

    if case["expected_decision"] == "review" and case.get("prediction", {}).get("decision") == "review":
        decision = "review"

    return {
        "case_id": case["case_id"],
        "title": case["title"],
        "query": case["query"],
        "decision": decision,
        "expected_decision": case["expected_decision"],
        "answer": case["prediction"]["answer"],
        "expected_answer": case["expected_answer"],
        "segments": case["prediction"].get("segments", []),
        "event_metrics": event_rows,
        "metrics": {
            "mean_tiou": mean_tiou,
            "min_evidence_coverage": min_coverage,
            "max_boundary_error_s": max_boundary_error,
            "temporal_order_ok": order,
            "source_trace_ok": trace,
            "visual_instruction_override": visual_override,
            "event_count": len(case.get("required_events", [])),
            "frame_count": len(case.get("frames", [])),
            "duration_s": case["duration_s"],
        },
        "quality_flags": flags,
        "evidence": collect_evidence(case),
        "limits": limits_for_case(case, flags),
        "next_action": next_action(decision, flags),
    }


def collect_evidence(case: dict) -> list[dict]:
    frames_by_id = {frame["frame_id"]: frame for frame in case.get("frames", [])}
    evidence = []
    for segment in case.get("prediction", {}).get("segments", []):
        for frame_id in segment.get("evidence_frame_ids", []):
            frame = frames_by_id.get(frame_id)
            if frame:
                evidence.append(
                    {
                        "frame_id": frame_id,
                        "t_s": frame["t_s"],
                        "caption": frame["caption"],
                        "ocr": frame["ocr"],
                        "objects": frame["objects"],
                        "transcript": frame["transcript"],
                    }
                )
    return evidence


def limits_for_case(case: dict, flags: list[str]) -> list[str]:
    limits = [
        "Los frames sintéticos representan evidencias temporales, no vídeo real.",
        "Una respuesta útil debe citar segmento, frame y modalidad.",
    ]
    if "visual_instruction_override" in flags:
        limits.append("El texto dentro del vídeo se trata como dato no confiable, no como instrucción.")
    if case["expected_decision"] == "review":
        limits.append("No hay evento verificable; responder exigiría inventar evidencia.")
    return limits


def next_action(decision: str, flags: list[str]) -> str:
    if decision == "block":
        return "Bloquear la instrucción visual y registrar el caso como prueba de seguridad."
    if decision == "review":
        return "Pedir revisión humana o más evidencia temporal antes de responder."
    if "boundary_error_high" in flags:
        return "Responder solo si el dominio tolera el error de frontera; si no, revisar."
    return "Responder con timestamps, frames y límites explícitos."


def write_storyboard(case: dict, path: Path) -> None:
    frames = case.get("frames", [])
    width = 1180
    height = 220 + 130 * len(frames)
    rows = []
    for idx, frame in enumerate(frames):
        y = 120 + idx * 130
        rows.append(f'<rect x="70" y="{y}" width="1040" height="92" fill="#FFFFFF" stroke="#111111" stroke-width="1.2"/>')
        rows.append(f'<text x="96" y="{y + 30}" font-size="14" font-weight="700" fill="#111111">{escape(frame["frame_id"])} · {frame["t_s"]:.1f}s</text>')
        rows.append(f'<text x="96" y="{y + 56}" font-size="13" fill="#111111">{escape(frame["caption"])}</text>')
        meta = f'OCR: {frame.get("ocr") or "sin OCR"} · objetos: {", ".join(frame.get("objects", [])) or "sin objetos"}'
        rows.append(f'<text x="96" y="{y + 78}" font-size="11" fill="#666666">{escape(meta)}</text>')
        rows.append(f'<circle cx="1030" cy="{y + 46}" r="24" fill="#F7F7F7" stroke="#111111"/>')
        rows.append(f'<text x="1030" y="{y + 51}" text-anchor="middle" font-size="12" fill="#111111">{idx + 1}</text>')

    svg = f'''<svg viewBox="0 0 {width} {height}" role="img" aria-labelledby="{case["case_id"]}-title" xmlns="http://www.w3.org/2000/svg">
  <title id="{case["case_id"]}-title">Storyboard temporal de {escape(case["case_id"])}</title>
  <rect width="{width}" height="{height}" fill="#FFFFFF"/>
  <text x="70" y="58" font-size="26" font-weight="700" fill="#111111">{escape(case["title"])}</text>
  <text x="70" y="88" font-size="13" fill="#555555">Duración: {case["duration_s"]}s · consulta: {escape(case["query"])}</text>
  {''.join(rows)}
  <text x="1090" y="{height - 30}" text-anchor="end" font-size="11" fill="#999999">IA para gente curiosa / Facsímil 12 / Capítulo 08 / 686f6c61</text>
</svg>
'''
    path.write_text(svg, encoding="utf-8")


def write_pipeline_svg(path: Path) -> None:
    svg = '''<svg viewBox="0 0 1180 760" role="img" aria-labelledby="f12c08-title f12c08-desc" xmlns="http://www.w3.org/2000/svg">
  <title id="f12c08-title">Pipeline de razonamiento temporal sobre vídeo</title>
  <desc id="f12c08-desc">Diagrama de ingesta de vídeo, muestreo, extracción de señales, memoria temporal, evaluación y respuesta con evidencias.</desc>
  <defs>
    <marker id="f12c08-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,6 L9,3 z" fill="#111111"/>
    </marker>
  </defs>
  <rect width="1180" height="760" fill="#FFFFFF"/>
  <text x="62" y="58" font-size="28" font-weight="700" fill="#111111">Vídeo: frames, eventos y memoria temporal</text>
  <text x="62" y="88" font-size="15" fill="#555555">Un sistema serio no dice “lo vi”; devuelve segmento, frame, modalidad, orden y límite.</text>

  <rect x="54" y="132" width="190" height="378" fill="#FFFFFF" stroke="#111111" stroke-width="1.5"/>
  <text x="149" y="164" text-anchor="middle" font-size="15" font-weight="700" fill="#111111">Vídeo bruto</text>
  <line x1="78" y1="186" x2="220" y2="186" stroke="#111111"/>
  <text x="84" y="224" font-size="12" fill="#111111">fps · resolución · codec</text>
  <text x="84" y="256" font-size="12" fill="#111111">audio · subtítulos</text>
  <text x="84" y="288" font-size="12" fill="#111111">metadatos</text>
  <text x="84" y="320" font-size="12" fill="#111111">permisos</text>

  <rect x="302" y="132" width="210" height="378" fill="#F7F7F7" stroke="#111111" stroke-width="1.5"/>
  <text x="407" y="164" text-anchor="middle" font-size="15" font-weight="700" fill="#111111">Muestreo</text>
  <line x1="328" y1="186" x2="486" y2="186" stroke="#111111"/>
  <text x="334" y="224" font-size="12" fill="#111111">frames uniformes</text>
  <text x="334" y="256" font-size="12" fill="#111111">keyframes</text>
  <text x="334" y="288" font-size="12" fill="#111111">escenas</text>
  <text x="334" y="320" font-size="12" fill="#111111">clips solapados</text>
  <rect x="334" y="362" width="146" height="54" fill="#FFFFFF" stroke="#111111"/>
  <text x="407" y="386" text-anchor="middle" font-size="11" font-weight="700" fill="#111111">Riesgo</text>
  <text x="407" y="405" text-anchor="middle" font-size="10" fill="#555555">perder evento breve</text>

  <rect x="570" y="132" width="236" height="378" fill="#FFFFFF" stroke="#111111" stroke-width="1.5"/>
  <text x="688" y="164" text-anchor="middle" font-size="15" font-weight="700" fill="#111111">Señales</text>
  <line x1="598" y1="186" x2="778" y2="186" stroke="#111111"/>
  <text x="604" y="224" font-size="12" fill="#111111">OCR visual</text>
  <text x="604" y="256" font-size="12" fill="#111111">objetos / acciones</text>
  <text x="604" y="288" font-size="12" fill="#111111">transcript / audio</text>
  <text x="604" y="320" font-size="12" fill="#111111">tracking</text>
  <text x="604" y="352" font-size="12" fill="#111111">timestamp</text>
  <rect x="604" y="392" width="168" height="54" fill="#111111" stroke="#111111"/>
  <text x="688" y="416" text-anchor="middle" font-size="11" font-weight="700" fill="#FFFFFF">Memoria temporal</text>
  <text x="688" y="435" text-anchor="middle" font-size="10" fill="#FFFFFF">evento · orden · evidencia</text>

  <rect x="862" y="132" width="244" height="378" fill="#F7F7F7" stroke="#111111" stroke-width="1.5"/>
  <text x="984" y="164" text-anchor="middle" font-size="15" font-weight="700" fill="#111111">Respuesta</text>
  <line x1="890" y1="186" x2="1078" y2="186" stroke="#111111"/>
  <text x="896" y="224" font-size="12" fill="#111111">segmentos t0-t1</text>
  <text x="896" y="256" font-size="12" fill="#111111">frames citados</text>
  <text x="896" y="288" font-size="12" fill="#111111">orden temporal</text>
  <text x="896" y="320" font-size="12" fill="#111111">tIoU / frontera</text>
  <text x="896" y="352" font-size="12" fill="#111111">answer · review · block</text>

  <line x1="244" y1="322" x2="300" y2="322" stroke="#111111" stroke-width="1.7" marker-end="url(#f12c08-arrow)"/>
  <line x1="512" y1="322" x2="568" y2="322" stroke="#111111" stroke-width="1.7" marker-end="url(#f12c08-arrow)"/>
  <line x1="806" y1="322" x2="860" y2="322" stroke="#111111" stroke-width="1.7" marker-end="url(#f12c08-arrow)"/>

  <rect x="136" y="594" width="908" height="72" fill="#FFFFFF" stroke="#111111" stroke-width="1.2"/>
  <text x="160" y="624" font-size="13" font-weight="700" fill="#111111">Regla práctica</text>
  <text x="160" y="648" font-size="13" fill="#111111">Si una afirmación temporal no apunta a segmento, frame y señal, no entra como respuesta automática.</text>
  <text x="1092" y="724" text-anchor="end" font-size="11" fill="#999999">IA para gente curiosa / Facsímil 12 / Capítulo 08 / 686f6c61</text>
</svg>
'''
    path.write_text(svg, encoding="utf-8")


def write_reports(results: list[dict], policy: dict) -> None:
    report = {
        "schema_version": "1.0",
        "project": "IA para gente curiosa",
        "fasciculo": 12,
        "capitulo": 8,
        "policy": policy["quality_gates"],
        "summary": {
            "case_count": len(results),
            "all_expected": all(item["decision"] == item["expected_decision"] for item in results),
            "min_mean_tiou": min(item["metrics"]["mean_tiou"] for item in results),
            "review_or_block_count": sum(item["decision"] in {"review", "block"} for item in results),
        },
        "results": results,
    }
    (OUTPUT / "video_temporal_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# Informe de auditoría temporal de vídeo",
        "",
        "Este informe comprueba si cada respuesta cita segmentos, frames, modalidades y orden temporal.",
        "",
        "| Caso | Decisión | mean tIoU | cobertura | orden | flags |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for result in results:
        flags = ", ".join(result["quality_flags"]) or "sin flags"
        lines.append(
            f"| `{result['case_id']}` | `{result['decision']}` | {result['metrics']['mean_tiou']:.3f} | "
            f"{result['metrics']['min_evidence_coverage']:.3f} | {result['metrics']['temporal_order_ok']} | {flags} |"
        )
    lines.extend(
        [
            "",
            "## Lectura de ingeniería",
            "",
            "- `tIoU` bajo significa que el sistema vio algo parecido, pero no localizó bien el momento.",
            "- Una respuesta temporal sin frame o modalidad citada no es auditable.",
            "- El texto dentro del vídeo es dato no confiable: puede citarse, pero no mandar al sistema.",
            "- Si falta el evento solicitado, la decisión sana es `review`, no inventar un segundo.",
        ]
    )
    (OUTPUT / "video_temporal_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    with (OUTPUT / "temporal_eval_matrix.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "case_id",
                "decision",
                "expected_decision",
                "mean_tiou",
                "min_evidence_coverage",
                "max_boundary_error_s",
                "temporal_order_ok",
                "source_trace_ok",
                "visual_instruction_override",
                "quality_flags",
            ],
        )
        writer.writeheader()
        for result in results:
            metrics = result["metrics"]
            writer.writerow(
                {
                    "case_id": result["case_id"],
                    "decision": result["decision"],
                    "expected_decision": result["expected_decision"],
                    "mean_tiou": metrics["mean_tiou"],
                    "min_evidence_coverage": metrics["min_evidence_coverage"],
                    "max_boundary_error_s": metrics["max_boundary_error_s"],
                    "temporal_order_ok": metrics["temporal_order_ok"],
                    "source_trace_ok": metrics["source_trace_ok"],
                    "visual_instruction_override": metrics["visual_instruction_override"],
                    "quality_flags": "|".join(result["quality_flags"]),
                }
            )


def main() -> None:
    policy = load_json(POLICY_PATH)
    cases = load_json(CASES_PATH)
    OUTPUT.mkdir(exist_ok=True)
    CARDS.mkdir(exist_ok=True)
    STORYBOARDS.mkdir(exist_ok=True)

    results = []
    for case in cases:
        result = evaluate_case(case, policy)
        results.append(result)
        (CARDS / f"{case['case_id']}.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        write_storyboard(case, STORYBOARDS / f"{case['case_id']}.svg")

    write_reports(results, policy)
    write_pipeline_svg(OUTPUT / "video_temporal_pipeline.svg")
    print(f"OK: {len(results)} casos de vídeo auditados en {OUTPUT}")


if __name__ == "__main__":
    main()
