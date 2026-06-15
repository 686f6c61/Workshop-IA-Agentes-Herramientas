#!/usr/bin/env python3
import argparse
import hashlib
import json
import math
import re
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"
DATA_DIR = ROOT / "data"
CONTRACT_DIR = ROOT / "contracts"


def load_json(path):
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


CASES = load_json(DATA_DIR / "practice_cases.json")
POLICY = load_json(CONTRACT_DIR / "practice_policy.json")


def case_for(chapter):
    return CASES.get(chapter, {})


def policy_for(chapter):
    return POLICY.get("chapter_expectations", {}).get(chapter, {})


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def norm(vector):
    size = math.sqrt(sum(x * x for x in vector)) or 1.0
    return [x / size for x in vector]


def tokens(text):
    clean = re.sub(r"[^a-z0-9áéíóúüñ_]+", " ", text.lower())
    stop = {"a", "al", "con", "de", "del", "el", "en", "es", "la", "las", "los", "no", "por", "que", "se", "si", "un", "una", "y"}
    return [t for t in clean.split() if t not in stop and len(t) > 2]


def embed(text, dims=32):
    vector = [0.0] * dims
    for token in tokens(text):
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        for index in range(dims):
            vector[index] += (digest[index % len(digest)] / 255.0) * 2 - 1
    return norm(vector)


def status(valid, summary, **extra):
    return {"status": "valid" if valid else "review", "summary": summary, **extra}


def c01_intervention():
    data = case_for("c01")
    chapter_policy = policy_for("c01")
    interventions = data.get("interventions", {
        "prompt_schema": {"conocimiento_vivo": 0, "accion_externa": 0, "formato": 5, "conducta_repetida": 2, "privacidad_local": 1, "coste": 5},
        "rag": {"conocimiento_vivo": 5, "accion_externa": 1, "formato": 2, "conducta_repetida": 2, "privacidad_local": 3, "coste": 3},
        "tool": {"conocimiento_vivo": 4, "accion_externa": 5, "formato": 3, "conducta_repetida": 1, "privacidad_local": 3, "coste": 3},
        "ajuste_lora": {"conocimiento_vivo": 1, "accion_externa": 0, "formato": 4, "conducta_repetida": 5, "privacidad_local": 3, "coste": 2},
        "modelo_local": {"conocimiento_vivo": 1, "accion_externa": 0, "formato": 2, "conducta_repetida": 2, "privacidad_local": 5, "coste": 4},
    })
    case = data.get("case", {"conocimiento_vivo": 5, "accion_externa": 0, "formato": 3, "conducta_repetida": 2, "privacidad_local": 4, "coste": 3})
    expected_top = chapter_policy.get("expected_top", "rag")
    ranking = sorted(
        ((name, sum(values[k] * weight for k, weight in case.items())) for name, values in interventions.items()),
        key=lambda item: item[1],
        reverse=True,
    )
    return status(ranking[0][0] == expected_top, "RAG gana porque el conocimiento vivo pesa más que actuar fuera.", input_case=case, ranking=ranking, what_you_take=chapter_policy.get("what_you_take"))


def c02_api_payload():
    data = case_for("c02")
    chapter_policy = policy_for("c02")
    schema = {
        "required": ["categoria", "prioridad", "siguiente_paso", "confianza", "evidencias", "necesita_tool"],
        "additionalProperties": False,
    }
    payload = data.get("payload", {
        "model": "modelo-vigente",
        "instructions": "Clasifica la solicitud y usa tools solo si faltan datos.",
        "input": [{"role": "user", "content": [{"type": "input_text", "text": "Pago hecho, campus pendiente"}, {"type": "input_file", "file_id": "file_normativa"}, {"type": "input_image", "image_url": "https://example.edu/captura.png"}]}],
        "text": {"format": {"type": "json_schema", "strict": True, "schema": schema}},
        "tools": [{"type": "function", "name": "consultar_expediente", "parameters": {"type": "object", "required": ["id_alumno"]}}],
        "metadata": {"trace_id": "trc_00042", "feature": "matricula"},
        "temperature": 0.2,
        "top_p": 0.9,
        "max_output_tokens": 900,
        "parallel_tool_calls": False,
        "store": False,
    })
    schema = payload["text"]["format"].get("schema", schema)
    checks = {
        "schema_strict": payload["text"]["format"]["strict"] is True,
        "has_tool": bool(payload["tools"]),
        "has_trace": "trace_id" in payload["metadata"],
        "multimodal": {part["type"] for part in payload["input"][0]["content"]} >= {"input_text", "input_file", "input_image"},
        "low_temperature": payload["temperature"] <= 0.3,
    }
    required_checks = chapter_policy.get("required_payload_checks", checks.keys())
    return status(all(checks.get(name, False) for name in required_checks), "Payload de API con contrato, tool, metadata y entrada multimodal.", checks=checks, payload=payload, schema=schema, what_you_take=chapter_policy.get("what_you_take"))


def c03_token_budget():
    data = case_for("c03")
    chapter_policy = policy_for("c03")
    call = data.get("call", {"instructions": 700, "history": 1800, "documents": 14000, "tools_schema": 1200, "output_max": 1500, "output_real": 650, "cache_hit": 12000, "window": 32000})
    prices = data.get("prices", {"input": 2.0, "output": 8.0, "cache_read": 0.2})
    input_total = call["instructions"] + call["history"] + call["documents"] + call["tools_schema"]
    fresh_input = max(input_total - call["cache_hit"], 0)
    reserved = input_total + call["output_max"]
    cost = (fresh_input * prices["input"] + call["cache_hit"] * prices["cache_read"] + call["output_real"] * prices["output"]) / 1_000_000
    margin = call["window"] - reserved
    decision = "cabe; medir calidad y latencia" if margin >= 0 else "no cabe; reducir contexto o usar RAG"
    return status(margin >= 0 and cost > 0, decision, call=call, prices=prices, input_total=input_total, fresh_input=fresh_input, reserved=reserved, margin=margin, estimated_cost=round(cost, 6), what_you_take=chapter_policy.get("what_you_take"))


def c04_model_cards():
    data = case_for("c04")
    chapter_policy = policy_for("c04")
    models = data.get("models", [
        {"name": "closed_api_frontier", "quality": 0.94, "latency": 0.62, "cost": 0.40, "context": 0.95, "data_control": 0.55, "reproducibility": 0.50, "openness": 0.10, "ops_fit": 0.90, "privacy": True, "json": True, "license": True},
        {"name": "closed_api_mini", "quality": 0.84, "latency": 0.86, "cost": 0.78, "context": 0.70, "data_control": 0.55, "reproducibility": 0.55, "openness": 0.10, "ops_fit": 0.95, "privacy": True, "json": True, "license": True},
        {"name": "open_weight_permissive", "quality": 0.80, "latency": 0.70, "cost": 0.82, "context": 0.68, "data_control": 0.90, "reproducibility": 0.82, "openness": 0.85, "ops_fit": 0.55, "privacy": True, "json": True, "license": True},
    ])
    weights = data.get("weights", {"quality": 0.22, "latency": 0.12, "cost": 0.14, "context": 0.08, "data_control": 0.16, "reproducibility": 0.12, "openness": 0.10, "ops_fit": 0.06})
    hard_filters = chapter_policy.get("hard_filters", ["privacy", "json", "license"])
    expected_top = chapter_policy.get("expected_top", "open_weight_permissive")
    candidates = [m for m in models if all(m.get(field) for field in hard_filters)]
    scored = sorted(((m["name"], round(sum(m[k] * w for k, w in weights.items()), 3)) for m in candidates), key=lambda x: x[1], reverse=True)
    discarded = [m["name"] for m in models if m not in candidates]
    return status(
        bool(scored) and scored[0][0] == expected_top,
        "La matriz revela prioridades: no basta con calidad; apertura, licencia, datos y operación cambian la decisión.",
        weights=weights,
        hard_filters=hard_filters,
        kpis=list(weights.keys()),
        ranking=scored,
        discarded_by_filter=discarded,
        expected_top=expected_top,
        what_you_take=chapter_policy.get("what_you_take"),
    )


def c05_local_model():
    data = case_for("c05")
    chapter_policy = policy_for("c05")
    model = data.get("model", {"parameters_b": 8, "bits": 4, "context": 8192, "kv_cache_gb": 3.0, "runtime_margin_gb": 4.0, "vram_gb": 16})
    minimum_margin = chapter_policy.get("minimum_memory_margin_gb", 2)
    weights_gb = model["parameters_b"] * 1_000_000_000 * model["bits"] / 8 / 1_000_000_000
    total = weights_gb + model["kv_cache_gb"] + model["runtime_margin_gb"]
    checks = {"fits_memory": total <= model["vram_gb"], "has_margin": model["vram_gb"] - total >= minimum_margin, "context_declared": model["context"] >= 4096}
    return status(all(checks.values()), "Modelo local razonable para prototipo, no para prometer concurrencia.", model=model, weights_gb=weights_gb, estimated_total_gb=total, checks=checks, what_you_take=chapter_policy.get("what_you_take"))


def c06_cloud_local():
    data = case_for("c06")
    chapter_policy = policy_for("c06")
    options = data.get("options", {
        "cloud_api": {"privacy": 2, "latency": 4, "ops": 5, "elasticity": 5, "cost_predictability": 3},
        "local_server": {"privacy": 5, "latency": 3, "ops": 2, "elasticity": 2, "cost_predictability": 4},
        "hybrid": {"privacy": 4, "latency": 3, "ops": 3, "elasticity": 4, "cost_predictability": 3},
        "rented_gpu": {"privacy": 3, "latency": 4, "ops": 3, "elasticity": 4, "cost_predictability": 2},
    })
    weights = data.get("weights", {"privacy": 0.30, "latency": 0.20, "ops": 0.20, "elasticity": 0.20, "cost_predictability": 0.10})
    acceptable_top = set(chapter_policy.get("acceptable_top", ["hybrid", "cloud_api"]))
    ranking = sorted(((name, round(sum(values[k] * w for k, w in weights.items()), 3)) for name, values in options.items()), key=lambda x: x[1], reverse=True)
    return status(ranking[0][0] in acceptable_top, "Cloud/local se decide por restricciones, no por preferencia.", weights=weights, ranking=ranking, what_you_take=chapter_policy.get("what_you_take"))


def c07_embeddings():
    data = case_for("c07")
    chapter_policy = policy_for("c07")
    docs = data.get("docs", {"d1": "MFA y acceso al campus virtual", "d2": "Calendario de matrícula y pagos", "d3": "Receta de bizcocho"})
    query = data.get("query", "no puedo entrar al campus con doble factor")
    dims = data.get("dims", 48)
    expected = chapter_policy.get("expected_hit_at_1", "d1")
    ranking = sorted(((doc_id, dot(embed(query, dims), embed(text, dims))) for doc_id, text in docs.items()), key=lambda x: x[1], reverse=True)
    hit_at_1 = 1.0 if ranking[0][0] == expected else 0.0
    return status(hit_at_1 == 1.0, "La dimensión es el tamaño del vector y el ranking debe evaluarse con casos.", query=query, dims=dims, ranking=ranking, hit_at_1=hit_at_1, what_you_take=chapter_policy.get("what_you_take"))


def c08_vector_hybrid():
    data = case_for("c08")
    chapter_policy = policy_for("c08")
    docs = data.get("docs", {
        "doc-01": {"text": "Moodle requiere MFA y recuperación de contraseña", "year": 2026, "active": True},
        "doc-02": {"text": "Calendario de matrícula en septiembre", "year": 2026, "active": True},
        "doc-03": {"text": "Procedimiento antiguo de Moodle 2024", "year": 2024, "active": False},
    })
    query = data.get("query", "moodle mfa acceso")
    filters = data.get("filter", {"year": 2026, "active": True})
    expected = chapter_policy.get("expected_hybrid_top", "doc-01")
    filtered = {k: v for k, v in docs.items() if all(v.get(field) == value for field, value in filters.items())}
    dense = sorted(((k, dot(embed(query), embed(v["text"]))) for k, v in filtered.items()), key=lambda x: x[1], reverse=True)
    lexical = sorted(((k, len(set(tokens(query)) & set(tokens(v["text"])))) for k, v in filtered.items()), key=lambda x: x[1], reverse=True)
    rrf = defaultdict(float)
    for ranking in (dense, lexical):
        for pos, (doc_id, _score) in enumerate(ranking, 1):
            rrf[doc_id] += 1 / (60 + pos)
    hybrid = sorted(rrf.items(), key=lambda x: x[1], reverse=True)
    return status(hybrid[0][0] == expected, "El filtro evita que contenido antiguo gane por parecido superficial.", query=query, filter=filters, dense=dense, lexical=lexical, hybrid=hybrid, what_you_take=chapter_policy.get("what_you_take"))


def c09_mini_rag():
    data = case_for("c09")
    chapter_policy = policy_for("c09")
    docs = data.get("docs", {"norm#1": "La ampliación de matrícula se solicita en septiembre.", "norm#2": "No se admite si hay pagos pendientes vencidos."})
    cases = data.get("cases", [
        {"q": "cuando se solicita ampliación", "gold": ["norm#1"], "must_abstain": False},
        {"q": "puedo ampliar con pagos vencidos", "gold": ["norm#2"], "must_abstain": False},
        {"q": "cual es el teléfono del rectorado", "gold": [], "must_abstain": True},
    ])
    traces = []
    for case in cases:
        scores = sorted(((doc_id, len(set(tokens(case["q"])) & set(tokens(text)))) for doc_id, text in docs.items()), key=lambda x: x[1], reverse=True)
        gold = set(case["gold"])
        retrieved = {doc_id for doc_id, score in scores[:1] if score > 0}
        abstain = not retrieved
        traces.append({"question": case["q"], "gold": sorted(gold), "retrieved": sorted(retrieved), "abstain": abstain, "ok": (abstain == case["must_abstain"]) and (not gold or bool(retrieved & gold))})
    return status(all(t["ok"] for t in traces), "RAG mínimo: recuperar, citar o abstenerse.", traces=traces, what_you_take=chapter_policy.get("what_you_take"))


def c10_rag_eval():
    data = case_for("c10")
    chapter_policy = policy_for("c10")
    runs = data.get("runs", [
        {"retrieved": [["a", 2], ["b", 0]], "gold": ["a"], "citations": ["a"], "claims_supported": True},
        {"retrieved": [["b", 0], ["a", 2]], "gold": ["a"], "citations": ["b"], "claims_supported": False},
    ])
    minimum_metric = chapter_policy.get("minimum_metric", 0.5)
    normalized = []
    for run in runs:
        normalized.append({**run, "gold": set(run["gold"]), "citations": set(run["citations"])})
    runs = normalized
    hit_at_1 = sum(1 for r in runs if r["retrieved"][0][0] in r["gold"]) / len(runs)
    citation_precision = sum(1 for r in runs if r["citations"] <= r["gold"]) / len(runs)
    groundedness = sum(1 for r in runs if r["claims_supported"]) / len(runs)
    release = hit_at_1 >= minimum_metric and citation_precision >= minimum_metric and groundedness >= minimum_metric
    return status(release, "La evaluación separa retrieval, citas y soporte de afirmaciones.", runs=[{**r, "gold": sorted(r["gold"]), "citations": sorted(r["citations"])} for r in runs], hit_at_1=hit_at_1, citation_precision=citation_precision, groundedness=groundedness, what_you_take=chapter_policy.get("what_you_take"))


def c11_agentic_rag():
    data = case_for("c11")
    chapter_policy = policy_for("c11")
    graph = data.get("graph", [("beca pendiente", "no bloquea", "ampliación"), ("pago vencido", "bloquea", "ampliación"), ("version 4.2", "relacionada", "doble factor")])
    question = data.get("question", "compara beca pendiente y pago vencido para ampliar matrícula")
    steps = data.get("steps", ["descomponer", "buscar_texto", "buscar_grafo", "evaluar_evidencia", "responder_con_citas"])
    minimum_hits = chapter_policy.get("minimum_graph_hits", 2)
    graph_hits = [edge for edge in graph if len(set(tokens(question)) & set(tokens(" ".join(edge)))) >= 2]
    return status(len(graph_hits) >= minimum_hits, "Agentic RAG complica solo cuando necesita varias rutas de evidencia.", question=question, plan=steps, graph_hits=graph_hits, what_you_take=chapter_policy.get("what_you_take"))


def c12_text_to_sql():
    data = case_for("c12")
    chapter_policy = policy_for("c12")
    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE pagos (campus TEXT, estado TEXT, importe REAL)")
    con.executemany("INSERT INTO pagos VALUES (?, ?, ?)", data.get("rows", [("Norte", "pendiente", 420.0), ("Norte", "pendiente", 380.0), ("Sur", "pagado", 300.0), ("Sur", "pendiente", 120.0)]))
    sql = data.get("sql", "SELECT campus, SUM(importe) AS total FROM pagos WHERE estado='pendiente' GROUP BY campus ORDER BY total DESC LIMIT 3")
    expected = chapter_policy.get("expected_top_campus", "Norte")
    blocked = bool(re.search(r"\b(insert|update|delete|drop|alter|create)\b", sql, re.I))
    rows = [dict(zip(["campus", "total"], row)) for row in con.execute(sql).fetchall()]
    return status((not blocked) and rows and rows[0]["campus"] == expected, "Text-to-SQL requiere validación antes de ejecutar.", sql=sql, rows=rows, what_you_take=chapter_policy.get("what_you_take"))


def c14_architecture_review():
    data = case_for("c14")
    chapter_policy = policy_for("c14")
    proposal = data.get("proposal", {"problema_definido": True, "contrato_salida": True, "evidencia_verificable": True, "permisos_explicitos": True, "coste_estimado": True, "latencia_estimable": True, "evaluacion_offline": True, "trazas": True, "mantenimiento_asignado": False, "complejidad_justificada": True})
    weights = data.get("weights", {"problema_definido": 2, "contrato_salida": 2, "evidencia_verificable": 2, "permisos_explicitos": 2, "coste_estimado": 1, "latencia_estimable": 1, "evaluacion_offline": 2, "trazas": 2, "mantenimiento_asignado": 1, "complejidad_justificada": 2})
    minimum_ratio = chapter_policy.get("minimum_ratio", 0.85)
    score = sum(weights[k] for k, ok in proposal.items() if ok)
    total = sum(weights.values())
    ratio = score / total
    decision = "prototipo controlado" if ratio >= minimum_ratio else "cerrar huecos"
    return status(ratio >= minimum_ratio, "La recapitulación se convierte en gate de arquitectura.", proposal=proposal, score=score, total=total, ratio=round(ratio, 3), decision=decision, missing=[k for k, ok in proposal.items() if not ok], what_you_take=chapter_policy.get("what_you_take"))


CHAPTERS = {
    "c01": c01_intervention,
    "c02": c02_api_payload,
    "c03": c03_token_budget,
    "c04": c04_model_cards,
    "c05": c05_local_model,
    "c06": c06_cloud_local,
    "c07": c07_embeddings,
    "c08": c08_vector_hybrid,
    "c09": c09_mini_rag,
    "c10": c10_rag_eval,
    "c11": c11_agentic_rag,
    "c12": c12_text_to_sql,
    "c14": c14_architecture_review,
}


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def render_markdown(chapter, report):
    lines = [
        f"# Práctica F4 {chapter.upper()}",
        "",
        f"Estado: `{report['status']}`.",
        "",
        report["summary"],
        "",
    ]
    if report.get("what_you_take"):
        lines.extend([
            "## Qué te llevas",
            "",
            report["what_you_take"],
            "",
        ])
    lines.extend([
        "## Evidencia",
        "",
        "```json",
        json.dumps(report, ensure_ascii=False, indent=2),
        "```",
        "",
    ])
    return "\n".join(lines)


def run(chapters, write):
    results = {}
    for chapter in chapters:
        report = CHAPTERS[chapter]()
        results[chapter] = report
        if write:
            write_json(OUTPUT / f"{chapter}_report.json", report)
            (OUTPUT / f"{chapter}_decision.md").write_text(render_markdown(chapter, report), encoding="utf-8")
    if write and len(results) > 1:
        write_json(OUTPUT / "all_summary.json", results)
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--chapter", choices=sorted(CHAPTERS), help="Capítulo concreto: c01, c02...")
    parser.add_argument("--all", action="store_true", help="Ejecuta todas las prácticas del kit.")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-invalid", action="store_true")
    args = parser.parse_args()

    if args.all:
        selected = sorted(CHAPTERS)
    elif args.chapter:
        selected = [args.chapter]
    else:
        raise SystemExit("Usa --chapter c01 o --all.")

    results = run(selected, args.write)
    summary = {chapter: report["status"] for chapter, report in results.items()}
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if args.fail_on_invalid and any(report["status"] != "valid" for report in results.values()):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
