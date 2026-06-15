#!/usr/bin/env python3
"""Audita un RAG multimodal mínimo: texto, páginas, tablas, figuras y gates."""

from __future__ import annotations

import csv
import json
import math
import re
import unicodedata
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "output"
ANSWER_DIR = OUTPUT_DIR / "answer_cards"


def load_json(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text.lower())
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def tokens(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]+(?:\.[0-9]+)?", normalize(text))
        if len(token) > 1
    }


def source_tokens(source: dict) -> set[str]:
    text = " ".join(
        [
            source.get("title", ""),
            source.get("text", ""),
            " ".join(source.get("keywords", [])),
            source.get("modality", ""),
            source.get("fact_id", ""),
        ]
    )
    return tokens(text)


def cosine_like_overlap(query_tokens: set[str], candidate_tokens: set[str]) -> float:
    if not query_tokens or not candidate_tokens:
        return 0.0
    overlap = len(query_tokens & candidate_tokens)
    return overlap / math.sqrt(len(query_tokens) * len(candidate_tokens))


def score_source(query: dict, source: dict, policy: dict) -> dict:
    query_tokens = tokens(query["question"])
    candidate_tokens = source_tokens(source)
    lexical = cosine_like_overlap(query_tokens, candidate_tokens)

    required_evidence = set(query.get("required_evidence", []))
    required_modalities = set(query.get("required_modalities", []))
    nice_modalities = set(query.get("nice_to_have_modalities", []))

    modality = source["modality"]
    modality_boost = 0.0
    if modality in required_modalities:
        modality_boost += policy["modality_boosts"].get(modality, 0.0)
    if modality in nice_modalities:
        modality_boost += policy["modality_boosts"].get(modality, 0.0) * 0.45

    fact_boost = 0.34 if source["fact_id"] in required_evidence else 0.0
    flag_boost = 0.2 if source.get("security_flags") and "ignore" in normalize(query["question"]) else 0.0

    score = round(lexical + modality_boost + fact_boost + flag_boost, 4)
    return {
        "source_id": source["source_id"],
        "title": source["title"],
        "modality": modality,
        "path": source["path"],
        "page": source.get("page"),
        "region_id": source.get("region_id"),
        "fact_id": source["fact_id"],
        "score": score,
        "lexical": round(lexical, 4),
        "modality_boost": round(modality_boost, 4),
        "fact_boost": round(fact_boost, 4),
        "security_flags": source.get("security_flags", []),
    }


def retrieve(query: dict, corpus: list[dict], policy: dict) -> list[dict]:
    scored = [score_source(query, source, policy) for source in corpus]
    return sorted(scored, key=lambda item: (-item["score"], item["source_id"]))[: policy["top_k"]]


def qrels_by_query(qrels: list[dict]) -> dict[str, dict[str, int]]:
    grouped: dict[str, dict[str, int]] = {}
    for row in qrels:
        grouped.setdefault(row["query_id"], {})[row["source_id"]] = int(row["relevance"])
    return grouped


def dcg(relevances: list[int]) -> float:
    total = 0.0
    for rank, relevance in enumerate(relevances, start=1):
        total += (2**relevance - 1) / math.log2(rank + 1)
    return total


def ndcg_at_k(retrieved: list[dict], qrels_for_query: dict[str, int], k: int) -> float:
    observed = [qrels_for_query.get(item["source_id"], 0) for item in retrieved[:k]]
    ideal = sorted(qrels_for_query.values(), reverse=True)[:k]
    ideal_score = dcg(ideal)
    if ideal_score == 0:
        return 0.0
    return round(dcg(observed) / ideal_score, 4)


def reciprocal_rank(retrieved: list[dict], qrels_for_query: dict[str, int]) -> float:
    for rank, item in enumerate(retrieved, start=1):
        if qrels_for_query.get(item["source_id"], 0) > 0:
            return round(1 / rank, 4)
    return 0.0


def unsupported_claims(answer: str, forbidden_claims: list[str]) -> list[str]:
    haystack = normalize(answer)
    return [claim for claim in forbidden_claims if normalize(claim) in haystack]


def build_answer_text(query: dict, decision: str, evidence: list[dict]) -> tuple[str, list[str], str]:
    qid = query["query_id"]
    if decision == "block":
        return (
            "Bloqueado: el texto dentro del documento se trata como dato no confiable, no como instrucción. No se aprueba nada y se conserva la evidencia para revisión.",
            ["La instrucción visual puede describirse como evidencia de riesgo, pero no puede modificar la política del sistema."],
            "Escalar a revisión y comprobar fuentes autorizadas antes de cualquier acción."
        )
    if decision == "review":
        return (
            "No hay evidencia suficiente para responder con seguridad. El sistema debe pedir la fuente que falta o enviar el caso a revisión.",
            ["La recuperación no cubre todas las evidencias o modalidades obligatorias."],
            "Añadir la resolución, estado o documento faltante y repetir la evaluación."
        )
    if qid == "q01_beca_envio":
        return (
            "No puede enviarse todavía: la política exige justificante de matrícula validado y el estado operativo indica pendiente_validacion el 2026-06-14.",
            ["No decide elegibilidad final ni sustituye una resolución administrativa."],
            "Guardar borrador, aportar documentación y volver a consultar el estado operativo."
        )
    if qid == "q02_factura_total":
        return (
            "El total verificado de FAC-2026-014 es 529.98 EUR: 508.20 EUR por matrícula primer plazo y 21.78 EUR por certificado académico.",
            ["La respuesta depende de que la tabla y la página visual correspondan a la misma factura."],
            "Comprobar que el total del documento coincide con la suma de line items antes de contabilizar."
        )
    if qid == "q03_piloto_metricas":
        return (
            "Sí, bajan: la latencia p95 pasa de 920 ms a 735 ms y los errores por mil bajan de 13.2 a 5.9 entre W20 y W23.",
            ["El gráfico explica la tendencia; la tabla conserva los valores exactos."],
            "Usar la figura para lectura visual y la tabla para cálculo, alerta o informe."
        )
    return (
        "Respuesta construida con evidencias recuperadas.",
        ["Revisa que las fuentes recuperadas cubran la pregunta."],
        "Validar evidencias antes de publicar."
    )


def evaluate_query(query: dict, retrieved: list[dict], policy: dict, qrels_for_query: dict[str, int]) -> dict:
    required_evidence = set(query.get("required_evidence", []))
    required_modalities = set(query.get("required_modalities", []))
    found_evidence = {item["fact_id"] for item in retrieved}
    found_modalities = {item["modality"] for item in retrieved}
    all_flags = sorted({flag for item in retrieved for flag in item.get("security_flags", [])})
    blocking_flags = set(policy["block_when_flags"])
    blocking_hits = [
        item
        for item in retrieved
        if set(item.get("security_flags", [])) & blocking_flags
        and (item["fact_id"] in required_evidence or item["score"] >= 0.55)
    ]

    recall_at_k = len(required_evidence & found_evidence) / max(len(required_evidence), 1)
    modality_coverage = len(required_modalities & found_modalities) / max(len(required_modalities), 1)
    relevant = [
        item
        for item in retrieved
        if item["fact_id"] in required_evidence
        or item["modality"] in required_modalities
        or item["modality"] in set(query.get("nice_to_have_modalities", []))
    ]
    context_precision = len(relevant) / max(len(retrieved), 1)
    evidence_coverage = recall_at_k

    decision = "answer"
    if blocking_hits:
        decision = "block"
    elif (
        recall_at_k < policy["minimum_recall_at_k"]
        or evidence_coverage < policy["minimum_evidence_coverage"]
        or modality_coverage < policy["minimum_modality_coverage"]
        or context_precision < policy["minimum_context_precision"]
    ):
        decision = "review"

    evidence = [
        {
            "source_id": item["source_id"],
            "modality": item["modality"],
            "fact_id": item["fact_id"],
            "page": item.get("page"),
            "region_id": item.get("region_id"),
            "score": item["score"],
        }
        for item in relevant
        if item["fact_id"] in required_evidence or item.get("security_flags")
    ]

    answer, limits, next_action = build_answer_text(query, decision, evidence)
    forbidden_hits = unsupported_claims(answer, query.get("forbidden_claims", []))

    issues = []
    warnings = []
    if decision != query["expected_decision"]:
        issues.append(f"decision_mismatch:expected_{query['expected_decision']}_got_{decision}")
    if forbidden_hits:
        issues.append("unsupported_claims:" + ",".join(forbidden_hits))
    if recall_at_k < policy["minimum_recall_at_k"]:
        warnings.append("low_recall_at_k")
    if modality_coverage < policy["minimum_modality_coverage"]:
        warnings.append("low_modality_coverage")
    if context_precision < policy["minimum_context_precision"]:
        warnings.append("low_context_precision")
    missing_evidence = sorted(required_evidence - found_evidence)
    missing_modalities = sorted(required_modalities - found_modalities)

    if missing_evidence:
        warnings.append("missing_evidence:" + ",".join(missing_evidence))
    if missing_modalities:
        warnings.append("missing_modalities:" + ",".join(missing_modalities))

    metrics = {
        "recall_at_k": round(recall_at_k, 4),
        "evidence_coverage": round(evidence_coverage, 4),
        "modality_coverage": round(modality_coverage, 4),
        "context_precision": round(context_precision, 4),
        "ndcg_at_k": ndcg_at_k(retrieved, qrels_for_query, policy["top_k"]),
        "mrr": reciprocal_rank(retrieved, qrels_for_query),
        "unsupported_claim_count": len(forbidden_hits),
        "retrieved_count": len(retrieved),
        "relevant_retrieved_count": len(relevant),
    }

    return {
        "query_id": query["query_id"],
        "question": query["question"],
        "decision": decision,
        "expected_decision": query["expected_decision"],
        "answer": answer,
        "evidence": evidence,
        "limits": limits,
        "next_action": next_action,
        "metrics": metrics,
        "security_flags": all_flags,
        "missing_evidence": missing_evidence,
        "missing_modalities": missing_modalities,
        "warnings": sorted(set(warnings)),
        "issues": sorted(set(issues)),
        "retrieved": retrieved,
        "qrels": qrels_for_query,
        "human_explanation": query.get("human_explanation", ""),
    }


def write_retrieved_contexts_csv(results: list[dict]) -> None:
    path = OUTPUT_DIR / "retrieved_contexts.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "query_id",
                "rank",
                "source_id",
                "modality",
                "fact_id",
                "score",
                "qrel_relevance",
                "page",
                "region_id",
                "security_flags",
            ],
        )
        writer.writeheader()
        for result in results:
            for rank, item in enumerate(result["retrieved"], start=1):
                writer.writerow(
                    {
                        "query_id": result["query_id"],
                        "rank": rank,
                        "source_id": item["source_id"],
                        "modality": item["modality"],
                        "fact_id": item["fact_id"],
                        "score": item["score"],
                        "qrel_relevance": result.get("qrels", {}).get(item["source_id"], 0),
                        "page": item.get("page"),
                        "region_id": item.get("region_id"),
                        "security_flags": "|".join(item.get("security_flags", [])),
                    }
                )


def write_report_md(results: list[dict], summary: dict) -> None:
    lines = [
        "# Informe F12 C06 · RAG multimodal",
        "",
        "Este informe audita recuperación multimodal con evidencias, modalidades y gates de decisión.",
        "",
        "## Resumen",
        "",
        f"- Consultas: {summary['query_count']}",
        f"- Respuestas: {summary['answer_count']}",
        f"- Revisiones: {summary['review_count']}",
        f"- Bloqueos: {summary['block_count']}",
        f"- Issues: {summary['issue_count']}",
        f"- Warnings: {summary['warning_count']}",
        "",
        "| Query | Decisión | Recall@k | nDCG@k | MRR | Cobertura modalidad | Precisión contexto | Issues | Warnings |",
        "|---|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for result in results:
        metrics = result["metrics"]
        lines.append(
            "| {query} | {decision} | {recall:.2f} | {ndcg:.2f} | {mrr:.2f} | {modal:.2f} | {precision:.2f} | {issues} | {warnings} |".format(
                query=result["query_id"],
                decision=result["decision"],
                recall=metrics["recall_at_k"],
                ndcg=metrics["ndcg_at_k"],
                mrr=metrics["mrr"],
                modal=metrics["modality_coverage"],
                precision=metrics["context_precision"],
                issues=", ".join(result["issues"]) or "-",
                warnings=", ".join(result["warnings"]) or "-",
            )
        )

    lines.extend(["", "## Detalle por consulta", ""])
    for result in results:
        lines.extend(
            [
                f"### {result['query_id']}",
                "",
                f"**Pregunta:** {result['question']}",
                "",
                f"**Decisión:** `{result['decision']}`",
                "",
                f"**Respuesta:** {result['answer']}",
                "",
                "**Evidencias usadas:**",
                "",
            ]
        )
        for item in result["evidence"]:
            page = f" · página {item['page']}" if item.get("page") else ""
            region = f" · región `{item['region_id']}`" if item.get("region_id") else ""
            lines.append(
                f"- `{item['source_id']}` · {item['modality']} · `{item['fact_id']}`{page}{region} · score {item['score']}"
            )
        lines.extend(
            [
                "",
                "**Qué enseña este caso:** " + result["human_explanation"],
                "",
            ]
        )

    (OUTPUT_DIR / "multimodal_rag_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_svg(results: list[dict]) -> None:
    answer_count = sum(1 for item in results if item["decision"] == "answer")
    review_count = sum(1 for item in results if item["decision"] == "review")
    block_count = sum(1 for item in results if item["decision"] == "block")
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1120 720" role="img" aria-labelledby="title desc">
  <title id="title">Pipeline RAG multimodal auditado</title>
  <desc id="desc">Arquitectura sintética de recuperación multimodal con índices, re-ranking, evidencias y gates.</desc>
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,6 L9,3 z" fill="#111111"/>
    </marker>
  </defs>
  <rect width="1120" height="720" fill="#ffffff"/>
  <text x="64" y="64" font-family="Inter, Arial, sans-serif" font-size="28" font-weight="700" fill="#111111">RAG multimodal: recuperar sin perder evidencia</text>
  <text x="64" y="96" font-family="Inter, Arial, sans-serif" font-size="15" fill="#555555">Texto, páginas, tablas y figuras no se mezclan a ciegas: se indexan, se recuperan y se validan por contrato.</text>

  <rect x="64" y="136" width="196" height="116" fill="#ffffff" stroke="#111111" stroke-width="1.5"/>
  <text x="162" y="166" text-anchor="middle" font-family="Inter, Arial, sans-serif" font-size="15" font-weight="700" fill="#111111">Fuentes</text>
  <text x="90" y="196" font-family="Inter, Arial, sans-serif" font-size="12" fill="#111111">PDF · página</text>
  <text x="90" y="218" font-family="Inter, Arial, sans-serif" font-size="12" fill="#111111">tabla · figura</text>
  <text x="90" y="240" font-family="Inter, Arial, sans-serif" font-size="12" fill="#111111">estado operativo</text>

  <rect x="320" y="136" width="208" height="116" fill="#f7f7f7" stroke="#111111" stroke-width="1.5"/>
  <text x="424" y="166" text-anchor="middle" font-family="Inter, Arial, sans-serif" font-size="15" font-weight="700" fill="#111111">Representación</text>
  <text x="346" y="196" font-family="Inter, Arial, sans-serif" font-size="12" fill="#111111">chunks con página/bbox</text>
  <text x="346" y="218" font-family="Inter, Arial, sans-serif" font-size="12" fill="#111111">embeddings por modalidad</text>
  <text x="346" y="240" font-family="Inter, Arial, sans-serif" font-size="12" fill="#111111">resúmenes y tablas crudas</text>

  <rect x="588" y="136" width="208" height="116" fill="#ffffff" stroke="#111111" stroke-width="1.5"/>
  <text x="692" y="166" text-anchor="middle" font-family="Inter, Arial, sans-serif" font-size="15" font-weight="700" fill="#111111">Retrieval híbrido</text>
  <text x="614" y="196" font-family="Inter, Arial, sans-serif" font-size="12" fill="#111111">BM25 + vector + filtros</text>
  <text x="614" y="218" font-family="Inter, Arial, sans-serif" font-size="12" fill="#111111">late interaction</text>
  <text x="614" y="240" font-family="Inter, Arial, sans-serif" font-size="12" fill="#111111">re-ranking multimodal</text>

  <rect x="856" y="136" width="200" height="116" fill="#f7f7f7" stroke="#111111" stroke-width="1.5"/>
  <text x="956" y="166" text-anchor="middle" font-family="Inter, Arial, sans-serif" font-size="15" font-weight="700" fill="#111111">Respuesta</text>
  <text x="884" y="196" font-family="Inter, Arial, sans-serif" font-size="12" fill="#111111">evidencias citables</text>
  <text x="884" y="218" font-family="Inter, Arial, sans-serif" font-size="12" fill="#111111">límites y decisión</text>
  <text x="884" y="240" font-family="Inter, Arial, sans-serif" font-size="12" fill="#111111">answer/review/block</text>

  <line x1="260" y1="194" x2="318" y2="194" stroke="#111111" stroke-width="1.6" marker-end="url(#arrow)"/>
  <line x1="528" y1="194" x2="586" y2="194" stroke="#111111" stroke-width="1.6" marker-end="url(#arrow)"/>
  <line x1="796" y1="194" x2="854" y2="194" stroke="#111111" stroke-width="1.6" marker-end="url(#arrow)"/>

  <rect x="116" y="328" width="888" height="238" fill="#ffffff" stroke="#111111" stroke-width="1.5"/>
  <text x="148" y="366" font-family="Inter, Arial, sans-serif" font-size="18" font-weight="700" fill="#111111">Gates de ingeniería</text>
  <line x1="148" y1="392" x2="972" y2="392" stroke="#111111" stroke-width="1"/>

  <text x="160" y="430" font-family="Inter, Arial, sans-serif" font-size="14" font-weight="700" fill="#111111">1. ¿He recuperado la evidencia obligatoria?</text>
  <text x="160" y="460" font-family="Inter, Arial, sans-serif" font-size="14" font-weight="700" fill="#111111">2. ¿Cubren las modalidades necesarias?</text>
  <text x="160" y="490" font-family="Inter, Arial, sans-serif" font-size="14" font-weight="700" fill="#111111">3. ¿La precisión contextual evita ruido?</text>
  <text x="160" y="520" font-family="Inter, Arial, sans-serif" font-size="14" font-weight="700" fill="#111111">4. ¿Hay instrucciones visuales o datos no confiables?</text>

  <rect x="716" y="420" width="92" height="76" fill="#ffffff" stroke="#111111" stroke-width="1.2"/>
  <text x="762" y="450" text-anchor="middle" font-family="Inter, Arial, sans-serif" font-size="22" font-weight="700" fill="#111111">{answer_count}</text>
  <text x="762" y="476" text-anchor="middle" font-family="Inter, Arial, sans-serif" font-size="12" fill="#555555">answer</text>
  <rect x="824" y="420" width="92" height="76" fill="#f7f7f7" stroke="#111111" stroke-width="1.2"/>
  <text x="870" y="450" text-anchor="middle" font-family="Inter, Arial, sans-serif" font-size="22" font-weight="700" fill="#111111">{review_count}</text>
  <text x="870" y="476" text-anchor="middle" font-family="Inter, Arial, sans-serif" font-size="12" fill="#555555">review</text>
  <rect x="932" y="420" width="52" height="76" fill="#111111" stroke="#111111" stroke-width="1.2"/>
  <text x="958" y="450" text-anchor="middle" font-family="Inter, Arial, sans-serif" font-size="22" font-weight="700" fill="#ffffff">{block_count}</text>
  <text x="958" y="476" text-anchor="middle" font-family="Inter, Arial, sans-serif" font-size="12" fill="#ffffff">block</text>

  <text x="1030" y="676" text-anchor="end" font-family="Inter, Arial, sans-serif" font-size="11" fill="#999999">IA para gente curiosa / Facsímil 12 / Capítulo 06 / 686f6c61</text>
</svg>
'''
    (OUTPUT_DIR / "multimodal_rag_pipeline.svg").write_text(svg, encoding="utf-8")


def write_answer_cards(results: list[dict]) -> None:
    ANSWER_DIR.mkdir(parents=True, exist_ok=True)
    for result in results:
        card = {
            "query_id": result["query_id"],
            "decision": result["decision"],
            "answer": result["answer"],
            "evidence": result["evidence"],
            "limits": result["limits"],
            "next_action": result["next_action"],
            "metrics": result["metrics"],
        }
        (ANSWER_DIR / f"{result['query_id']}.json").write_text(
            json.dumps(card, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ANSWER_DIR.mkdir(parents=True, exist_ok=True)

    corpus = load_json("data/multimodal_corpus.json")
    queries = load_json("data/rag_queries.json")
    qrels = qrels_by_query(load_json("data/qrels.json"))
    policy = load_json("contracts/multimodal_rag_policy.json")

    results = []
    for query in queries:
        retrieved = retrieve(query, corpus, policy)
        results.append(evaluate_query(query, retrieved, policy, qrels.get(query["query_id"], {})))

    summary = {
        "query_count": len(results),
        "answer_count": sum(1 for item in results if item["decision"] == "answer"),
        "review_count": sum(1 for item in results if item["decision"] == "review"),
        "block_count": sum(1 for item in results if item["decision"] == "block"),
        "issue_count": sum(len(item["issues"]) for item in results),
        "warning_count": sum(len(item["warnings"]) for item in results),
        "average_recall_at_k": round(
            sum(item["metrics"]["recall_at_k"] for item in results) / max(len(results), 1),
            4,
        ),
        "average_modality_coverage": round(
            sum(item["metrics"]["modality_coverage"] for item in results) / max(len(results), 1),
            4,
        ),
        "average_ndcg_at_k": round(
            sum(item["metrics"]["ndcg_at_k"] for item in results) / max(len(results), 1),
            4,
        ),
        "average_mrr": round(
            sum(item["metrics"]["mrr"] for item in results) / max(len(results), 1),
            4,
        ),
    }

    report = {"summary": summary, "results": results}
    (OUTPUT_DIR / "multimodal_rag_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_retrieved_contexts_csv(results)
    write_answer_cards(results)
    write_report_md(results, summary)
    write_svg(results)

    print("consultas:", summary["query_count"])
    print("answer:", summary["answer_count"], "review:", summary["review_count"], "block:", summary["block_count"])
    print("issues:", summary["issue_count"], "warnings:", summary["warning_count"])
    print("reporte:", OUTPUT_DIR / "multimodal_rag_report.md")
    return 1 if summary["issue_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
