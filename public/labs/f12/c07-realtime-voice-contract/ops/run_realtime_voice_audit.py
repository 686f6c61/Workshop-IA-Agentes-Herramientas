from __future__ import annotations

import csv
import json
import math
import re
import struct
import wave
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "contracts/realtime_voice_policy.json"
CASES_PATH = ROOT / "data/voice_cases.json"
OUTPUT = ROOT / "output"
CARDS = OUTPUT / "turn_cards"
AUDIO = OUTPUT / "audio"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_words(text: str) -> list[str]:
    cleaned = re.sub(r"[^a-záéíóúüñ0-9 ]+", " ", text.lower())
    return [word for word in cleaned.split() if word]


def levenshtein_counts(reference: list[str], hypothesis: list[str]) -> dict[str, int | float]:
    rows = len(reference) + 1
    cols = len(hypothesis) + 1
    matrix: list[list[tuple[int, int, int, int]]] = [
        [(0, 0, 0, 0) for _ in range(cols)] for _ in range(rows)
    ]

    for i in range(1, rows):
        cost, subs, dels, ins = matrix[i - 1][0]
        matrix[i][0] = (cost + 1, subs, dels + 1, ins)
    for j in range(1, cols):
        cost, subs, dels, ins = matrix[0][j - 1]
        matrix[0][j] = (cost + 1, subs, dels, ins + 1)

    for i in range(1, rows):
        for j in range(1, cols):
            candidates: list[tuple[int, int, int, int]] = []
            diagonal = matrix[i - 1][j - 1]
            if reference[i - 1] == hypothesis[j - 1]:
                candidates.append(diagonal)
            else:
                cost, subs, dels, ins = diagonal
                candidates.append((cost + 1, subs + 1, dels, ins))

            cost, subs, dels, ins = matrix[i - 1][j]
            candidates.append((cost + 1, subs, dels + 1, ins))

            cost, subs, dels, ins = matrix[i][j - 1]
            candidates.append((cost + 1, subs, dels, ins + 1))
            matrix[i][j] = min(candidates, key=lambda item: (item[0], item[1], item[2], item[3]))

    cost, substitutions, deletions, insertions = matrix[-1][-1]
    denominator = max(len(reference), 1)
    return {
        "wer": round(cost / denominator, 4),
        "substitutions": substitutions,
        "deletions": deletions,
        "insertions": insertions,
        "reference_words": len(reference),
        "hypothesis_words": len(hypothesis),
    }


def redact_pii(text: str, patterns: dict[str, str]) -> tuple[str, list[str]]:
    redacted = text
    found: list[str] = []
    for name, pattern in patterns.items():
        regex = re.compile(pattern)
        if regex.search(redacted):
            found.append(name)
            redacted = regex.sub(f"[{name.upper()}]", redacted)
    return redacted, found


def mean_energy(segments: list[dict]) -> float:
    total_ms = 0
    weighted = 0.0
    for segment in segments:
        duration = segment["end_ms"] - segment["start_ms"]
        total_ms += duration
        weighted += duration * segment["energy"]
    if total_ms == 0:
        return 0.0
    return round(weighted / total_ms, 4)


def has_confirmation_phrase(text: str, phrases: list[str]) -> bool:
    normalized = " ".join(normalize_words(text))
    return any(phrase in normalized for phrase in phrases)


def critical_slot_metrics(case: dict) -> dict[str, int | float | list[dict]]:
    slots = case.get("critical_slots", [])
    mismatches = [
        slot
        for slot in slots
        if normalize_words(slot.get("reference", "")) != normalize_words(slot.get("hypothesis", ""))
    ]
    return {
        "critical_slot_count": len(slots),
        "critical_slot_errors": len(mismatches),
        "critical_slot_error_rate": round(len(mismatches) / max(len(slots), 1), 4),
        "critical_slot_mismatches": mismatches,
    }


def partial_stability(case: dict) -> dict[str, int | float]:
    partials = case.get("partial_hypotheses", [])
    if len(partials) <= 1:
        return {"partial_count": len(partials), "partial_revision_count": 0, "partial_stability": 1.0}

    revisions = 0
    previous = normalize_words(partials[0]["text"])
    for partial in partials[1:]:
        current = normalize_words(partial["text"])
        if previous and current[: len(previous)] != previous:
            revisions += 1
        previous = current

    return {
        "partial_count": len(partials),
        "partial_revision_count": revisions,
        "partial_stability": round(1 - revisions / max(len(partials) - 1, 1), 4),
    }


def decide(case: dict, policy: dict, metrics: dict, pii_found: list[str]) -> tuple[str, list[str], str]:
    gates = policy["quality_gates"]
    tool_policy = policy["tool_policy"]
    flags: list[str] = []

    if metrics["wer"] > gates["max_wer_for_automatic_decision"]:
        flags.append("wer_above_gate")
    if metrics["critical_slot_error_rate"] > gates["max_critical_slot_error_rate"]:
        flags.append("critical_slot_error")
    if metrics["mean_energy"] < gates["min_mean_energy"] or case["audio_quality"] == "noisy":
        flags.append("audio_quality_low")
    if metrics["endpoint_delay_ms"] > gates["max_endpoint_delay_ms"]:
        flags.append("endpoint_delay_high")
    if metrics["first_audio_latency_ms"] > gates["max_first_audio_latency_ms"]:
        flags.append("first_audio_latency_high")
    if metrics.get("barge_in_stop_latency_ms") is not None:
        if metrics["barge_in_stop_latency_ms"] <= gates["max_barge_in_stop_latency_ms"]:
            flags.append("barge_in_respected")
        else:
            flags.append("barge_in_too_slow")
    if pii_found:
        flags.append("pii_redacted_before_logging")

    if "barge_in_respected" in flags:
        return "stop_and_answer", flags, "Detener reproducción, cancelar salida anterior y reabrir el turno."

    if "wer_above_gate" in flags or "critical_slot_error" in flags or "audio_quality_low" in flags:
        return "ask_repeat", flags, "Pedir repetición o pasar a canal escrito antes de ejecutar cambios."

    if case["requires_tool"] and case["tool_name"] in tool_policy["confirmation_required_for"]:
        if not has_confirmation_phrase(case["confirmation_phrase"], tool_policy["confirmation_phrases"]):
            flags.append("tool_requires_explicit_confirmation")
            return "confirm_before_tool", flags, "Solicitar confirmación explícita y registrar evidencia antes de ejecutar la tool."

    return "answer", flags, "Responder con límites, evidencias y sin ejecutar acciones fuera de política."


def case_metrics(case: dict, policy: dict) -> dict:
    timings = case["timings_ms"]
    speech_end = max(segment["end_ms"] for segment in case["speech_segments"])
    speech_start = min(segment["start_ms"] for segment in case["speech_segments"])
    wer_counts = levenshtein_counts(
        normalize_words(case["reference_transcript"]),
        normalize_words(case["asr_hypothesis"]),
    )
    metrics = {
        **wer_counts,
        **critical_slot_metrics(case),
        **partial_stability(case),
        "speech_start_ms": speech_start,
        "speech_end_ms": speech_end,
        "mean_energy": mean_energy(case["speech_segments"]),
        "endpoint_delay_ms": timings["asr_final"] - speech_end,
        "first_audio_latency_ms": timings["tts_first_audio"] - speech_end,
        "total_turn_latency_ms": timings["tts_completed"] - speech_start,
        "sample_rate_hz": policy["audio"]["sample_rate_hz"],
        "endpoint_silence_ms": policy["audio"]["endpoint_silence_ms"],
    }
    if "user_barge_in" in timings and "tts_stop" in timings:
        metrics["barge_in_stop_latency_ms"] = timings["tts_stop"] - timings["user_barge_in"]
    else:
        metrics["barge_in_stop_latency_ms"] = None
    return metrics


def generate_wav(path: Path, case: dict, sample_rate: int) -> None:
    duration_ms = max(case["timings_ms"]["tts_completed"], 1000)
    total_samples = int(sample_rate * duration_ms / 1000)
    segments = case["speech_segments"]

    def amplitude_for_ms(ms: float) -> float:
        for segment in segments:
            if segment["start_ms"] <= ms <= segment["end_ms"]:
                return min(segment["energy"] * 2.4, 0.28)
        return 0.002

    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        for index in range(total_samples):
            ms = index * 1000 / sample_rate
            amp = amplitude_for_ms(ms)
            value = amp * math.sin(2 * math.pi * 210 * index / sample_rate)
            value += (amp / 4) * math.sin(2 * math.pi * 420 * index / sample_rate)
            wav.writeframes(struct.pack("<h", int(max(min(value, 1.0), -1.0) * 32767)))


def write_svg(path: Path) -> None:
    svg = """<svg viewBox="0 0 1180 760" role="img" aria-labelledby="f12c07-title f12c07-desc" xmlns="http://www.w3.org/2000/svg">
  <title id="f12c07-title">Contrato operativo de voz en tiempo real</title>
  <desc id="f12c07-desc">Pipeline de audio con captura, VAD, ASR, gestor de turnos, herramientas, TTS, reproducción, trazas y evaluación.</desc>
  <defs>
    <marker id="f12c07-arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,6 L9,3 z" fill="#111111"/>
    </marker>
  </defs>
  <rect width="1180" height="760" fill="#FFFFFF"/>
  <text x="62" y="58" font-size="28" font-weight="700" fill="#111111">Voz realtime: no es solo STT + LLM + TTS</text>
  <text x="62" y="88" font-size="15" fill="#555555">Cada turno tiene audio, incertidumbre, latencia, interrupciones, herramientas y privacidad.</text>

  <rect x="54" y="128" width="178" height="380" fill="#FFFFFF" stroke="#111111" stroke-width="1.5"/>
  <text x="143" y="160" text-anchor="middle" font-size="15" font-weight="700" fill="#111111">Entrada</text>
  <line x1="78" y1="184" x2="208" y2="184" stroke="#111111"/>
  <text x="82" y="224" font-size="12" fill="#111111">micrófono</text>
  <text x="82" y="254" font-size="12" fill="#111111">16 kHz / PCM / Opus</text>
  <text x="82" y="284" font-size="12" fill="#111111">eco y ruido</text>
  <text x="82" y="314" font-size="12" fill="#111111">frames 20 ms</text>
  <rect x="82" y="352" width="104" height="52" fill="#F7F7F7" stroke="#111111"/>
  <text x="134" y="375" text-anchor="middle" font-size="11" font-weight="700" fill="#111111">VAD</text>
  <text x="134" y="393" text-anchor="middle" font-size="10" fill="#555555">habla / silencio</text>

  <rect x="284" y="128" width="214" height="380" fill="#F7F7F7" stroke="#111111" stroke-width="1.5"/>
  <text x="391" y="160" text-anchor="middle" font-size="15" font-weight="700" fill="#111111">ASR streaming</text>
  <line x1="310" y1="184" x2="472" y2="184" stroke="#111111"/>
  <text x="314" y="224" font-size="12" fill="#111111">parciales</text>
  <text x="314" y="254" font-size="12" fill="#111111">final de turno</text>
  <text x="314" y="284" font-size="12" fill="#111111">WER / confianza</text>
  <text x="314" y="314" font-size="12" fill="#111111">timestamp</text>
  <rect x="314" y="352" width="154" height="72" fill="#FFFFFF" stroke="#111111"/>
  <text x="391" y="377" text-anchor="middle" font-size="11" font-weight="700" fill="#111111">Gates de calidad</text>
  <text x="391" y="397" text-anchor="middle" font-size="10" fill="#555555">repetir · seguir · revisar</text>

  <rect x="550" y="128" width="230" height="380" fill="#FFFFFF" stroke="#111111" stroke-width="1.5"/>
  <text x="665" y="160" text-anchor="middle" font-size="15" font-weight="700" fill="#111111">Gestor de turno</text>
  <line x1="576" y1="184" x2="754" y2="184" stroke="#111111"/>
  <text x="580" y="224" font-size="12" fill="#111111">estado conversacional</text>
  <text x="580" y="254" font-size="12" fill="#111111">barge-in</text>
  <text x="580" y="284" font-size="12" fill="#111111">política de tools</text>
  <text x="580" y="314" font-size="12" fill="#111111">confirmaciones</text>
  <text x="580" y="344" font-size="12" fill="#111111">redacción de PII</text>
  <rect x="580" y="384" width="170" height="58" fill="#111111" stroke="#111111"/>
  <text x="665" y="408" text-anchor="middle" font-size="11" font-weight="700" fill="#FFFFFF">Contrato</text>
  <text x="665" y="428" text-anchor="middle" font-size="10" fill="#FFFFFF">answer · repeat · confirm</text>

  <rect x="836" y="128" width="246" height="380" fill="#F7F7F7" stroke="#111111" stroke-width="1.5"/>
  <text x="959" y="160" text-anchor="middle" font-size="15" font-weight="700" fill="#111111">Salida</text>
  <line x1="864" y1="184" x2="1054" y2="184" stroke="#111111"/>
  <text x="868" y="224" font-size="12" fill="#111111">LLM / tools / RAG</text>
  <text x="868" y="254" font-size="12" fill="#111111">TTS first audio</text>
  <text x="868" y="284" font-size="12" fill="#111111">playout y jitter</text>
  <text x="868" y="314" font-size="12" fill="#111111">cancelación si interrumpen</text>
  <text x="868" y="344" font-size="12" fill="#111111">trazas y evals</text>
  <rect x="868" y="384" width="180" height="58" fill="#FFFFFF" stroke="#111111"/>
  <text x="958" y="408" text-anchor="middle" font-size="11" font-weight="700" fill="#111111">SLIs</text>
  <text x="958" y="428" text-anchor="middle" font-size="10" fill="#555555">WER · latencia · barge-in</text>

  <line x1="232" y1="320" x2="282" y2="320" stroke="#111111" stroke-width="1.6" marker-end="url(#f12c07-arrow)"/>
  <line x1="498" y1="320" x2="548" y2="320" stroke="#111111" stroke-width="1.6" marker-end="url(#f12c07-arrow)"/>
  <line x1="780" y1="320" x2="834" y2="320" stroke="#111111" stroke-width="1.6" marker-end="url(#f12c07-arrow)"/>

  <rect x="132" y="572" width="916" height="82" fill="#FFFFFF" stroke="#111111" stroke-width="1.2"/>
  <text x="158" y="604" font-size="13" font-weight="700" fill="#111111">Regla práctica</text>
  <text x="158" y="628" font-size="13" fill="#111111">Una tool no se ejecuta porque “el audio parecía decirlo”; se ejecuta cuando el contrato de turno, calidad y permisos lo permite.</text>
  <text x="1092" y="724" text-anchor="end" font-size="11" fill="#999999">IA para gente curiosa / Facsímil 12 / Capítulo 07 / 686f6c61</text>
</svg>
"""
    path.write_text(svg, encoding="utf-8")


def build_turn_card(case: dict, decision: str, flags: list[str], metrics: dict, redacted: str) -> dict:
    limits = [
        "La transcripción de voz no se trata como verdad absoluta.",
        "Las herramientas con efecto externo requieren política y confirmación.",
    ]
    if "pii_redacted_before_logging" in flags:
        limits.append("Los datos personales se redactan antes de guardar trazas.")
    if decision == "ask_repeat":
        next_action = "Pedir repetición, mostrar resumen escrito y evitar tool calls."
    elif decision == "confirm_before_tool":
        next_action = "Pedir confirmación explícita y revisión humana antes de ejecutar la acción."
    elif decision == "stop_and_answer":
        next_action = "Detener TTS, cancelar la salida anterior y continuar desde la nueva intención."
    else:
        next_action = "Responder con evidencias y registrar métricas del turno."

    return {
        "case_id": case["case_id"],
        "title": case["title"],
        "decision": decision,
        "expected_decision": case["expected_decision"],
        "redacted_transcript": redacted,
        "answer": case["expected_answer"],
        "metrics": metrics,
        "quality_flags": flags,
        "evidence": case["required_evidence"],
        "limits": limits,
        "next_action": next_action,
    }


def write_reports(results: list[dict], policy: dict) -> None:
    summary = {
        "cases": len(results),
        "decisions": {result["case_id"]: result["decision"] for result in results},
        "all_expected": all(result["decision"] == result["expected_decision"] for result in results),
        "max_first_audio_latency_ms": max(result["metrics"]["first_audio_latency_ms"] for result in results),
        "max_wer": max(result["metrics"]["wer"] for result in results),
    }
    report = {
        "schema_version": "1.0",
        "project": "IA para gente curiosa",
        "fasciculo": 12,
        "capitulo": 7,
        "policy": {
            "max_wer_for_automatic_decision": policy["quality_gates"]["max_wer_for_automatic_decision"],
            "max_first_audio_latency_ms": policy["quality_gates"]["max_first_audio_latency_ms"],
            "max_barge_in_stop_latency_ms": policy["quality_gates"]["max_barge_in_stop_latency_ms"],
        },
        "summary": summary,
        "results": results,
    }
    (OUTPUT / "realtime_voice_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    lines = [
        "# Informe de voz en tiempo real",
        "",
        "Este informe comprueba si cada turno cumple calidad mínima de audio, latencia, privacidad y política de herramientas.",
        "",
        "| Caso | Decisión | WER | Latencia primera voz | Flags |",
        "|---|---:|---:|---:|---|",
    ]
    for result in results:
        flags = ", ".join(result["quality_flags"]) or "sin flags"
        lines.append(
            f"| `{result['case_id']}` | `{result['decision']}` | "
            f"{result['metrics']['wer']:.3f} | {result['metrics']['first_audio_latency_ms']} ms | {flags} |"
        )
    lines.extend(
        [
            "",
            "## Lectura de ingeniería",
            "",
            "- Si sube el WER, el sistema debe pedir repetición antes de cambiar datos o ejecutar tools.",
            "- Si hay barge-in, la salida anterior debe cancelarse rápido y quedar registrado.",
            "- Si aparece PII, la traza humana y la salida estructurada deben quedar redactadas.",
            "- Si la tool tiene efecto externo, una transcripción no basta: hace falta confirmación explícita.",
        ]
    )
    (OUTPUT / "realtime_voice_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    with (OUTPUT / "latency_budget.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "case_id",
                "decision",
                "wer",
                "mean_energy",
                "endpoint_delay_ms",
                "first_audio_latency_ms",
                "barge_in_stop_latency_ms",
                "total_turn_latency_ms",
            ],
        )
        writer.writeheader()
        for result in results:
            metrics = result["metrics"]
            writer.writerow(
                {
                    "case_id": result["case_id"],
                    "decision": result["decision"],
                    "wer": metrics["wer"],
                    "mean_energy": metrics["mean_energy"],
                    "endpoint_delay_ms": metrics["endpoint_delay_ms"],
                    "first_audio_latency_ms": metrics["first_audio_latency_ms"],
                    "barge_in_stop_latency_ms": metrics["barge_in_stop_latency_ms"],
                    "total_turn_latency_ms": metrics["total_turn_latency_ms"],
                }
            )

    with (OUTPUT / "voice_eval_matrix.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "case_id",
                "decision",
                "expected_decision",
                "wer",
                "critical_slot_error_rate",
                "critical_slot_errors",
                "partial_revision_count",
                "partial_stability",
                "quality_flags",
                "should_be_manual_or_confirmed",
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
                    "wer": metrics["wer"],
                    "critical_slot_error_rate": metrics["critical_slot_error_rate"],
                    "critical_slot_errors": metrics["critical_slot_errors"],
                    "partial_revision_count": metrics["partial_revision_count"],
                    "partial_stability": metrics["partial_stability"],
                    "quality_flags": "|".join(result["quality_flags"]),
                    "should_be_manual_or_confirmed": result["decision"] in {"ask_repeat", "confirm_before_tool", "review"},
                }
            )


def main() -> None:
    policy = load_json(POLICY_PATH)
    cases = load_json(CASES_PATH)
    OUTPUT.mkdir(exist_ok=True)
    CARDS.mkdir(exist_ok=True)
    AUDIO.mkdir(exist_ok=True)

    results: list[dict] = []
    patterns = policy["privacy"]["pii_patterns"]
    sample_rate = policy["audio"]["sample_rate_hz"]

    for case in cases:
        metrics = case_metrics(case, policy)
        redacted, pii_found = redact_pii(case["asr_hypothesis"], patterns)
        decision, flags, action = decide(case, policy, metrics, pii_found)
        card = build_turn_card(case, decision, flags, metrics, redacted)
        card["audit_action"] = action
        (CARDS / f"{case['case_id']}.json").write_text(
            json.dumps(card, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        generate_wav(AUDIO / f"{case['case_id']}.wav", case, sample_rate)
        results.append(card)

    write_reports(results, policy)
    write_svg(OUTPUT / "realtime_voice_pipeline.svg")
    print(f"OK: {len(results)} turnos auditados en {OUTPUT}")


if __name__ == "__main__":
    main()
