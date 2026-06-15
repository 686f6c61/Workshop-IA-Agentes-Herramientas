#!/usr/bin/env python3
import argparse
import hashlib
import json
import math
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOKEN_RE = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ_]+|\d+|[^\s]")
SYNONYMS = {
    "gato": "animal_gato",
    "felino": "animal_gato",
    "doméstico": "hogar",
    "domestico": "hogar",
    "casa": "hogar",
    "machine": "ml",
    "learning": "ml",
    "aprendizaje": "ml",
    "automático": "ml",
    "automatico": "ml",
    "function": "funcion",
    "def": "funcion",
    "getuser": "obtener_usuario",
    "get_user": "obtener_usuario",
    "desarrolladores": "desarrollo",
    "desa": "desarrollo",
    "rroll": "desarrollo",
    "adore": "desarrollo",
    "responsables": "responsable"
}


def load_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def split_long_word(token):
    if len(token) <= 12 or "_" in token:
        return [token]
    pieces = [token[:4]]
    rest = token[4:]
    while rest:
        pieces.append(rest[:5])
        rest = rest[5:]
    return pieces


def tokenize(text):
    raw = TOKEN_RE.findall(text)
    tokens = []
    for token in raw:
        if token.isalpha() and len(token) > 8:
            tokens.extend(split_long_word(token.lower()))
        else:
            tokens.append(token.lower())
    return tokens


def stable_id(token):
    digest = hashlib.sha1(token.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % 50000


def canonical(token):
    return SYNONYMS.get(token.lower(), token.lower())


def embedding(tokens, dimensions):
    vector = [0.0] * dimensions
    for token in tokens:
        key = canonical(token)
        digest = hashlib.sha256(key.encode("utf-8")).digest()
        index = digest[0] % dimensions
        sign = 1 if digest[1] % 2 == 0 else -1
        vector[index] += sign
    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [value / norm for value in vector]


def cosine(a, b):
    return sum(x * y for x, y in zip(a, b))


def inspect_text(text, dimensions, price):
    tokens = tokenize(text)
    ids = [stable_id(token) for token in tokens]
    return {
        "text": text,
        "tokens": tokens,
        "token_ids": ids,
        "token_count": len(tokens),
        "estimated_cost_usd": round(len(tokens) / 1000 * price, 8),
        "embedding_preview": [round(v, 3) for v in embedding(tokens, dimensions)[:8]]
    }


def inspect_case(case, policy):
    dimensions = policy["embedding_dimensions"]
    price = policy["example_price_per_1k_tokens_usd"]
    inspected = [inspect_text(text, dimensions, price) for text in case["texts"]]
    vectors = [embedding(item["tokens"], dimensions) for item in inspected]
    similarity = cosine(vectors[0], vectors[1]) if len(vectors) >= 2 else None
    must_be_similar = case.get("must_be_similar", True)
    return {
        "id": case["id"],
        "expected": case["expected"],
        "must_be_similar": must_be_similar,
        "texts": inspected,
        "cosine_similarity": round(similarity, 4) if similarity is not None else None,
        "passes_similarity_threshold": (not must_be_similar) or similarity is None or similarity >= policy["similarity_threshold"],
        "token_budget_warning": any(item["token_count"] > policy["token_budget_warning"] for item in inspected)
    }


def write_markdown(results):
    lines = [
        "# Inspección de tokens y embeddings",
        "",
        "Este informe usa un tokenizador y un embedding de juguete. La lectura importante es el mecanismo, no los números exactos.",
        "",
    ]
    for item in results:
        lines.extend([
            f"## {item['id']}",
            "",
            f"- Objetivo: {item['expected']}.",
            f"- Este caso exige similitud alta: {'sí' if item['must_be_similar'] else 'no'}.",
            f"- Similitud coseno: `{item['cosine_similarity']}`.",
            f"- Aviso de presupuesto de tokens: {'sí' if item['token_budget_warning'] else 'no'}."
        ])
        for text in item["texts"]:
            lines.append(f"- `{text['text']}` -> {text['token_count']} tokens: `{text['tokens']}`.")
        lines.append("")
    lines.append("En producción repetirías este ejercicio con el tokenizador y el modelo de embedding reales. Este kit te prepara para entender qué estás midiendo.")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-invalid", action="store_true")
    args = parser.parse_args()

    cases = load_json("data/text_cases.json")
    policy = load_json("contracts/token_embedding_policy.json")
    results = [inspect_case(case, policy) for case in cases]
    report = {"results": results, "invalid": [r["id"] for r in results if not r["passes_similarity_threshold"]]}

    if args.write:
        (ROOT / "output").mkdir(exist_ok=True)
        (ROOT / "output/token_embedding_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        (ROOT / "output/token_embedding_decision.md").write_text(write_markdown(results), encoding="utf-8")

    print(json.dumps(report, indent=2, ensure_ascii=False))
    if args.fail_on_invalid and report["invalid"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
