#!/usr/bin/env python3
"""Audita un ranking imagen-texto tipo CLIP con vectores sintéticos."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "catalog_pairs.json"
POLICY_PATH = ROOT / "contracts" / "retrieval_policy.json"
OUTPUT_DIR = ROOT / "output"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def norm(v: list[float]) -> float:
    return math.sqrt(sum(x * x for x in v))


def normalize(v: list[float]) -> list[float]:
    n = norm(v)
    if n == 0:
        raise ValueError("embedding con norma cero")
    return [x / n for x in v]


def cosine(a: list[float], b: list[float]) -> float:
    return dot(normalize(a), normalize(b))


def softmax(values: list[float]) -> list[float]:
    m = max(values)
    exps = [math.exp(v - m) for v in values]
    total = sum(exps)
    return [v / total for v in exps]


def cross_entropy(probability: float) -> float:
    return -math.log(max(probability, 1e-12))


def rank_scores(query: list[float], candidates: Iterable[dict], field: str) -> list[dict]:
    rows = []
    for candidate in candidates:
        rows.append(
            {
                "id": candidate["id"],
                "title": candidate.get("image_title") or candidate.get("text") or candidate["id"],
                "score": round(cosine(query, candidate[field]), 6),
            }
        )
    return sorted(rows, key=lambda row: row["score"], reverse=True)


def build_matrix(pairs: list[dict]) -> list[list[float]]:
    return [
        [round(cosine(image["image_embedding"], text["text_embedding"]), 6) for text in pairs]
        for image in pairs
    ]


def recall_at_k(matrix: list[list[float]], k: int, axis: str) -> float:
    hits = 0
    n = len(matrix)
    if axis == "image_to_text":
        for i, row in enumerate(matrix):
            ranked = sorted(range(n), key=lambda j: row[j], reverse=True)
            hits += int(i in ranked[:k])
    elif axis == "text_to_image":
        for j in range(n):
            col = [matrix[i][j] for i in range(n)]
            ranked = sorted(range(n), key=lambda i: col[i], reverse=True)
            hits += int(j in ranked[:k])
    else:
        raise ValueError(axis)
    return round(hits / n, 4)


def symmetric_infonce(matrix: list[list[float]], temperature: float) -> dict:
    n = len(matrix)
    image_losses = []
    text_losses = []
    for i, row in enumerate(matrix):
        probs = softmax([score / temperature for score in row])
        image_losses.append(cross_entropy(probs[i]))
    for j in range(n):
        col = [matrix[i][j] for i in range(n)]
        probs = softmax([score / temperature for score in col])
        text_losses.append(cross_entropy(probs[j]))
    return {
        "image_to_text_loss": round(sum(image_losses) / n, 6),
        "text_to_image_loss": round(sum(text_losses) / n, 6),
        "symmetric_loss": round((sum(image_losses) + sum(text_losses)) / (2 * n), 6),
    }


def hard_negatives(pairs: list[dict], matrix: list[list[float]]) -> list[dict]:
    rows = []
    for i, pair in enumerate(pairs):
        row = matrix[i]
        ranked = sorted(range(len(row)), key=lambda j: row[j], reverse=True)
        best = ranked[0]
        second = ranked[1]
        margin = row[i] - row[second] if second != i else row[i] - row[ranked[2]]
        if best != i or margin < 0.08:
            rows.append(
                {
                    "image_id": pair["id"],
                    "positive_text": pair["text"],
                    "top_text_id": pairs[best]["id"],
                    "top_text": pairs[best]["text"],
                    "positive_score": round(row[i], 6),
                    "top_score": round(row[best], 6),
                    "margin_vs_next": round(margin, 6),
                    "reason": "top1_incorrecto" if best != i else "margen_bajo",
                }
            )
    return rows


def query_rankings(pairs: list[dict], queries: list[dict]) -> list[dict]:
    results = []
    for query in queries:
        ranking = rank_scores(query["text_embedding"], pairs, "image_embedding")
        expected_rank = next(
            index + 1 for index, row in enumerate(ranking) if row["id"] == query["expected_image_id"]
        )
        results.append(
            {
                "query_id": query["query_id"],
                "text": query["text"],
                "expected_image_id": query["expected_image_id"],
                "expected_rank": expected_rank,
                "top_3": ranking[:3],
            }
        )
    return results


def write_matrix_csv(path: Path, pairs: list[dict], matrix: list[list[float]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["image_id", *[pair["id"] for pair in pairs]])
        for pair, row in zip(pairs, matrix):
            writer.writerow([pair["id"], *row])


def write_errors_csv(path: Path, errors: list[dict]) -> None:
    fieldnames = [
        "image_id",
        "positive_text",
        "top_text_id",
        "top_text",
        "positive_score",
        "top_score",
        "margin_vs_next",
        "reason",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(errors)


def matrix_svg(path: Path, pairs: list[dict], matrix: list[list[float]]) -> None:
    size = 72
    left = 220
    top = 150
    width = left + size * len(pairs) + 90
    height = top + size * len(pairs) + 150
    cells = []
    for i, row in enumerate(matrix):
        for j, score in enumerate(row):
            shade = int(255 - max(0, min(1, score)) * 180)
            fill = f"rgb({shade},{shade},{shade})"
            stroke = "#111111" if i == j else "#DDDDDD"
            cells.append(
                f'<rect x="{left + j*size}" y="{top + i*size}" width="{size}" height="{size}" fill="{fill}" stroke="{stroke}" stroke-width="1.2"/>'
                f'<text x="{left + j*size + size/2}" y="{top + i*size + 42}" text-anchor="middle" font-size="12" fill="{"#FFFFFF" if shade < 100 else "#111111"}" font-family="Inter, Arial, sans-serif">{score:.2f}</text>'
            )
    labels = []
    for idx, pair in enumerate(pairs):
        labels.append(
            f'<text x="{left - 16}" y="{top + idx*size + 43}" text-anchor="end" font-size="12" fill="#111111" font-family="Inter, Arial, sans-serif">{pair["id"]}</text>'
        )
        labels.append(
            f'<text transform="translate({left + idx*size + 42},{top - 18}) rotate(-35)" text-anchor="start" font-size="12" fill="#111111" font-family="Inter, Arial, sans-serif">{pair["id"]}</text>'
        )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="Matriz de similitud imagen texto con diagonal positiva">
  <rect width="{width}" height="{height}" fill="#FFFFFF"/>
  <text x="44" y="56" font-size="24" font-weight="700" fill="#111111" font-family="Inter, Arial, sans-serif">Matriz imagen-texto</text>
  <text x="44" y="84" font-size="14" fill="#555555" font-family="Inter, Arial, sans-serif">La diagonal debería ser alta. Las celdas oscuras fuera de diagonal son negativos duros.</text>
  <text x="{left + size*len(pairs)/2}" y="{top - 70}" text-anchor="middle" font-size="13" fill="#111111" font-family="Inter, Arial, sans-serif">Textos candidatos</text>
  <text x="76" y="{top + size*len(pairs)/2}" text-anchor="middle" font-size="13" fill="#111111" font-family="Inter, Arial, sans-serif" transform="rotate(-90 76 {top + size*len(pairs)/2})">Imágenes</text>
  {''.join(labels)}
  {''.join(cells)}
  <rect x="{left}" y="{top + size*len(pairs) + 24}" width="260" height="48" rx="8" fill="#F7F7F7" stroke="#111111"/>
  <text x="{left + 130}" y="{top + size*len(pairs) + 54}" text-anchor="middle" font-size="12" fill="#111111" font-family="Inter, Arial, sans-serif">oscuro = mayor similitud coseno</text>
  <text x="{width - 48}" y="{height - 32}" text-anchor="end" font-size="11" fill="#888888" opacity="0.55" font-family="Inter, Arial, sans-serif">IA para gente curiosa / Facsímil 12 / Capítulo 03 / 686f6c61</text>
</svg>
'''
    path.write_text(svg, encoding="utf-8")


def render_report(report: dict) -> str:
    lines = [
        "# Reporte de ranking contrastivo imagen-texto",
        "",
        f"Dataset: `{report['dataset_id']}`",
        f"Temperatura: `{report['temperature']}`",
        f"Recall@1 imagen->texto: `{report['metrics']['image_to_text_recall_at_1']}`",
        f"Recall@1 texto->imagen: `{report['metrics']['text_to_image_recall_at_1']}`",
        f"Pérdida simétrica InfoNCE: `{report['loss']['symmetric_loss']}`",
        f"Gate: `{report['gate']}`",
        "",
        "## Métricas",
        "",
        "| Métrica | Valor |",
        "|---|---:|",
    ]
    for key, value in report["metrics"].items():
        lines.append(f"| {key} | {value} |")
    lines.extend(["", "## Negativos duros", ""])
    if report["hard_negatives"]:
        lines.append("| Imagen | Top incorrecto o margen bajo | Margen | Razón |")
        lines.append("|---|---|---:|---|")
        for row in report["hard_negatives"]:
            lines.append(
                f"| {row['image_id']} | {row['top_text_id']} | {row['margin_vs_next']} | {row['reason']} |"
            )
    else:
        lines.append("No se han detectado negativos duros con la política actual.")
    lines.extend(["", "## Consultas externas", ""])
    lines.append("| Query | Esperado | Rank | Top 3 |")
    lines.append("|---|---|---:|---|")
    for row in report["query_rankings"]:
        top = ", ".join(f"{item['id']} ({item['score']})" for item in row["top_3"])
        lines.append(f"| {row['query_id']} | {row['expected_image_id']} | {row['expected_rank']} | {top} |")
    lines.extend(
        [
            "",
            "## Decisión de ingeniería",
            "",
            "- Si el Recall@1 baja, revisa descripciones, embeddings, negativos duros y dominio.",
            "- Si la diagonal de la matriz no destaca, los pares positivos no están suficientemente separados.",
            "- Si hay celdas oscuras fuera de diagonal, no lo escondas: son los casos que debes enseñar al alumno y probar en producción.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-invalid", action="store_true")
    args = parser.parse_args()

    data = load_json(DATA_PATH)
    policy = load_json(POLICY_PATH)
    pairs = data["pairs"]
    dimension = policy["embedding_dimension"]
    for pair in pairs:
        for field in ("image_embedding", "text_embedding"):
            if len(pair[field]) != dimension:
                raise ValueError(f"{pair['id']} tiene dimensión inválida en {field}")

    matrix = build_matrix(pairs)
    loss = symmetric_infonce(matrix, policy["temperature"])
    hard = hard_negatives(pairs, matrix)
    query_rows = query_rankings(pairs, data["queries"])
    positive_margins = []
    for i, row in enumerate(matrix):
        negatives = [score for j, score in enumerate(row) if j != i]
        positive_margins.append(row[i] - max(negatives))
    metrics = {
        "image_to_text_recall_at_1": recall_at_k(matrix, 1, "image_to_text"),
        "image_to_text_recall_at_3": recall_at_k(matrix, 3, "image_to_text"),
        "text_to_image_recall_at_1": recall_at_k(matrix, 1, "text_to_image"),
        "text_to_image_recall_at_3": recall_at_k(matrix, 3, "text_to_image"),
        "mean_positive_margin": round(sum(positive_margins) / len(positive_margins), 6),
        "query_recall_at_1": round(sum(1 for row in query_rows if row["expected_rank"] == 1) / len(query_rows), 4),
    }
    gate_ok = (
        metrics["image_to_text_recall_at_1"] >= policy["minimum_recall_at_1"]
        and metrics["text_to_image_recall_at_1"] >= policy["minimum_recall_at_1"]
        and metrics["mean_positive_margin"] >= policy["minimum_mean_positive_margin"]
    )
    report = {
        "dataset_id": data["dataset_id"],
        "temperature": policy["temperature"],
        "metrics": metrics,
        "loss": loss,
        "hard_negatives": hard,
        "query_rankings": query_rows,
        "gate": "pass" if gate_ok else "review",
        "gate_ok": gate_ok,
        "matrix": matrix,
    }

    if args.write:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        (OUTPUT_DIR / "clip_ranking_report.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        (OUTPUT_DIR / "clip_ranking_report.md").write_text(render_report(report), encoding="utf-8")
        write_matrix_csv(OUTPUT_DIR / "similarity_matrix.csv", pairs, matrix)
        write_errors_csv(OUTPUT_DIR / "retrieval_errors.csv", hard)
        matrix_svg(OUTPUT_DIR / "contrastive_matrix.svg", pairs, matrix)

    print(json.dumps({"gate": report["gate"], "metrics": metrics, "loss": loss}, indent=2, ensure_ascii=False))

    if args.fail_on_invalid and not gate_ok:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
