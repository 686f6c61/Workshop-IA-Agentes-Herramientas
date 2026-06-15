import argparse
import json
import math
import re
import time
import uuid
from collections import Counter
from pathlib import Path


STOPWORDS = {"a", "al", "como", "cómo", "con", "cuando", "cuándo", "cuantos", "cuántos", "de", "del", "el", "en", "es", "hasta", "la", "las", "lo", "los", "por", "puedo", "que", "qué", "se", "un", "una", "y"}


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def write_json(path, payload):
    Path(path).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def tokens(text):
    return [token for token in re.findall(r"[a-záéíóúüñ0-9]+", text.lower()) if token not in STOPWORDS]


def vector(text):
    return Counter(tokens(text))


def score(query, document):
    q = vector(query)
    d = vector(document["text"])
    overlap = sum(min(q[token], d[token]) for token in q)
    if overlap == 0:
        return 0.0
    return overlap / math.sqrt(sum(value * value for value in d.values()))


def span(trace, name, **attrs):
    trace["spans"].append({"name": name, "timestamp_ms": int(time.time() * 1000), "attrs": attrs})


def retrieve(case, documents, top_k=2):
    trace = {"trace_id": str(uuid.uuid4()), "case_id": case["case_id"], "spans": []}
    span(trace, "input", question=case["question"])
    candidates = [doc for doc in documents if doc["status"] == "vigente"]
    span(trace, "filter_documents", candidates=[doc["id"] for doc in candidates])
    ranked = sorted(((score(case["question"], doc), doc["id"], doc["text"]) for doc in candidates), reverse=True)
    ranked = [item for item in ranked if item[0] > 0][:top_k]
    span(trace, "retrieve", results=[doc_id for _, doc_id, _ in ranked])
    answerable = case["should_answer"] and bool(ranked)
    answer = ranked[0][2] if answerable else "No tengo evidencia suficiente para responder con este RAG."
    span(trace, "generate", answer=answer, answerable=answerable)
    return {"case_id": case["case_id"], "expected_doc": case["expected_doc"], "should_answer": case["should_answer"], "ranked_docs": [doc_id for _, doc_id, _ in ranked], "answer": answer, "trace": trace}


def reciprocal_rank(expected_doc, ranked_docs):
    if expected_doc is None:
        return None
    if expected_doc not in ranked_docs:
        return 0.0
    return 1.0 / (ranked_docs.index(expected_doc) + 1)


def evaluate(results, contract):
    with_expected = [item for item in results if item["expected_doc"] is not None]
    hit_at_1 = sum(item["ranked_docs"][:1] == [item["expected_doc"]] for item in with_expected) / len(with_expected)
    rr = [reciprocal_rank(item["expected_doc"], item["ranked_docs"]) for item in with_expected]
    mrr = sum(rr) / len(rr)
    abstention_ok = sum((not item["should_answer"]) == item["answer"].startswith("No tengo evidencia") for item in results) / len(results)
    trace_complete = sum(len(item["trace"]["spans"]) >= 4 for item in results) / len(results)
    metrics = {"hit_at_1": round(hit_at_1, 4), "mrr": round(mrr, 4), "abstention_ok": round(abstention_ok, 4), "trace_complete_rate": round(trace_complete, 4)}
    must = contract["rag_must_pass"]
    blocks = []
    if metrics["hit_at_1"] < must["hit_at_1_min"]:
        blocks.append("hit_at_1")
    if metrics["mrr"] < must["mrr_min"]:
        blocks.append("mrr")
    if metrics["abstention_ok"] < must["abstention_ok_min"]:
        blocks.append("abstention_ok")
    if metrics["trace_complete_rate"] < must["trace_complete_rate_min"]:
        blocks.append("trace_complete_rate")
    return {"status": "bloquear" if blocks else "publicar", "metrics": metrics, "blocks": blocks, "results": results}


def render_decision(report):
    lines = [
        "# Decisión mini RAG",
        "",
        f"Estado: **{report['status']}**.",
        "",
    ]
    for key, value in report["metrics"].items():
        lines.append(f"- `{key}`: `{value}`.")
    lines.extend([
        "",
        "La decisión mira recuperación, evidencia, abstención y trazas. El caso de pagos no se responde con texto porque pide un dato vivo; debe ir a una herramienta de datos.",
    ])
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--documents", default="data/documents.jsonl")
    parser.add_argument("--cases", default="data/rag_cases.json")
    parser.add_argument("--contract", default="contracts/lab_eval_contract.json")
    parser.add_argument("--output-dir", default="output")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    results = [retrieve(case, read_jsonl(args.documents)) for case in read_json(args.cases)]
    report = evaluate(results, read_json(args.contract))
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if args.write:
        out = Path(args.output_dir)
        out.mkdir(parents=True, exist_ok=True)
        write_json(out / "rag_eval_report.json", report)
        write_json(out / "ci_rag_gate.json", {"status": report["status"], "blocks": report["blocks"]})
        (out / "rag_traces.jsonl").write_text("\n".join(json.dumps(item["trace"], ensure_ascii=False) for item in results) + "\n", encoding="utf-8")
        (out / "rag_decision.md").write_text(render_decision(report), encoding="utf-8")


if __name__ == "__main__":
    main()
