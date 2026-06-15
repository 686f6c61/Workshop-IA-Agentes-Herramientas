#!/usr/bin/env python3
import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def read_ppm(relative):
    tokens = []
    for line in (ROOT / relative).read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        tokens.extend(stripped.split())
    if tokens[0] != "P3":
        raise ValueError("solo se soporta PPM ASCII P3")
    width = int(tokens[1])
    height = int(tokens[2])
    max_value = int(tokens[3])
    raw = list(map(int, tokens[4:]))
    expected = width * height * 3
    if len(raw) != expected:
        raise ValueError(f"pixeles inesperados: {len(raw)} != {expected}")
    pixels = []
    index = 0
    for _y in range(height):
        row = []
        for _x in range(width):
            row.append(tuple(raw[index:index + 3]))
            index += 3
        pixels.append(row)
    return {"width": width, "height": height, "max": max_value, "pixels": pixels}


def normalize_rgb(rgb, norm):
    return [
        round(((channel / 255) - norm["mean"][idx]) / norm["std"][idx], 4)
        for idx, channel in enumerate(rgb)
    ]


def project_patch(mean_rgb, row, col, dimension):
    normalized = [value / 255 for value in mean_rgb]
    base = normalized + [(row + 1) / 10, (col + 1) / 10, 1.0]
    values = []
    for index in range(dimension):
        acc = 0.0
        for j, value in enumerate(base):
            weight = (((index + 1) * (j + 2)) % 7 - 3) / 5
            acc += value * weight
        values.append(round(acc, 4))
    return values


def patchify(image, patch_size, projection_dimension):
    width = image["width"]
    height = image["height"]
    if width % patch_size or height % patch_size:
        raise ValueError("la demo exige dimensiones divisibles por patch_size")
    patches = []
    patch_id = 0
    for y in range(0, height, patch_size):
        for x in range(0, width, patch_size):
            values = []
            for yy in range(y, y + patch_size):
                for xx in range(x, x + patch_size):
                    values.append(image["pixels"][yy][xx])
            mean_rgb = tuple(round(sum(pixel[c] for pixel in values) / len(values), 2) for c in range(3))
            row = y // patch_size
            col = x // patch_size
            patches.append(
                {
                    "patch_id": patch_id,
                    "row": row,
                    "col": col,
                    "x": x,
                    "y": y,
                    "size": patch_size,
                    "mean_rgb": mean_rgb,
                    "embedding_preview": project_patch(mean_rgb, row, col, projection_dimension),
                }
            )
            patch_id += 1
    return patches


def token_budget(height, width, patch_size):
    rows = math.ceil(height / patch_size)
    cols = math.ceil(width / patch_size)
    tokens = rows * cols
    padded_h = rows * patch_size
    padded_w = cols * patch_size
    original_area = height * width
    padded_area = padded_h * padded_w
    return {
        "height": height,
        "width": width,
        "patch_size": patch_size,
        "patch_rows": rows,
        "patch_cols": cols,
        "visual_tokens": tokens,
        "attention_pairs": tokens * tokens,
        "padded_height": padded_h,
        "padded_width": padded_w,
        "padding_ratio": round((padded_area - original_area) / original_area, 6),
    }


def svg_grid(image, patches):
    scale = 42
    width_px = image["width"] * scale
    height_px = image["height"] * scale
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width_px + 260} {height_px + 150}" role="img" aria-label="Rejilla de patches visuales">',
        '<rect width="100%" height="100%" fill="#FFFFFF"/>',
        '<text x="24" y="34" font-family="Inter, Arial, sans-serif" font-size="20" font-weight="700" fill="#111111">Imagen sintética dividida en patches</text>',
    ]
    for patch in patches:
        r, g, b = [int(round(v)) for v in patch["mean_rgb"]]
        x = 24 + patch["x"] * scale
        y = 60 + patch["y"] * scale
        size = patch["size"] * scale
        fill = f"rgb({r},{g},{b})"
        text_color = "#FFFFFF" if (r + g + b) / 3 < 120 else "#111111"
        lines.append(f'<rect x="{x}" y="{y}" width="{size}" height="{size}" fill="{fill}" stroke="#111111" stroke-width="1.3"/>')
        lines.append(f'<text x="{x + size / 2}" y="{y + size / 2 + 5}" text-anchor="middle" font-family="Inter, Arial, sans-serif" font-size="12" fill="{text_color}">p{patch["patch_id"]}</text>')
    info_x = 24 + width_px + 34
    lines.extend(
        [
            f'<rect x="{info_x}" y="60" width="190" height="{height_px}" rx="8" fill="#F7F7F7" stroke="#111111"/>',
            f'<text x="{info_x + 18}" y="92" font-family="Inter, Arial, sans-serif" font-size="14" font-weight="700" fill="#111111">Lectura</text>',
            f'<text x="{info_x + 18}" y="124" font-family="Inter, Arial, sans-serif" font-size="12" fill="#333333">Cada bloque es un token visual.</text>',
            f'<text x="{info_x + 18}" y="150" font-family="Inter, Arial, sans-serif" font-size="12" fill="#333333">El orden conserva posición.</text>',
            f'<text x="{info_x + 18}" y="176" font-family="Inter, Arial, sans-serif" font-size="12" fill="#333333">El embedding resume color y lugar.</text>',
            f'<text x="{width_px + 250}" y="{height_px + 126}" text-anchor="end" font-family="Inter, Arial, sans-serif" font-size="11" fill="#888888" opacity="0.55">IA para gente curiosa / Facsímil 12 / Capítulo 02 / 686f6c61</text>',
            "</svg>",
        ]
    )
    return "\n".join(lines)


def build_report(policy, resolutions):
    image = read_ppm(policy["image_path"])
    patch_size = policy["patch_size"]
    patches = patchify(image, patch_size, policy["projection_dimension"])
    demo_budget = token_budget(image["height"], image["width"], patch_size)
    normalized_preview = [
        {
            "patch_id": patch["patch_id"],
            "normalized_mean_rgb": normalize_rgb(patch["mean_rgb"], policy["normalization"]),
        }
        for patch in patches[:6]
    ]
    resolution_budgets = [
        {"name": item["name"], "why": item["why"], **token_budget(item["height"], item["width"], item["patch_size"])}
        for item in resolutions["cases"]
    ]
    base = next(item for item in resolution_budgets if item["name"] == "vit_base_224_p16")
    for item in resolution_budgets:
        item["token_ratio_vs_vit_224_p16"] = round(item["visual_tokens"] / base["visual_tokens"], 4)
        item["attention_pair_ratio_vs_vit_224_p16"] = round(item["attention_pairs"] / base["attention_pairs"], 4)

    issues = []
    gates = policy["gates"]
    if demo_budget["visual_tokens"] > gates["max_demo_visual_tokens"]:
        issues.append("too_many_demo_tokens")
    if demo_budget["attention_pairs"] > gates["max_attention_pairs_demo"]:
        issues.append("too_many_demo_attention_pairs")
    if any(item["padding_ratio"] > gates["max_padding_ratio"] for item in resolution_budgets):
        issues.append("padding_ratio_too_high")
    if len(resolution_budgets) < gates["require_resolution_cases"]:
        issues.append("too_few_resolution_cases")

    return {
        "image": {
            "path": policy["image_path"],
            "height": image["height"],
            "width": image["width"],
            "channels": 3,
        },
        "patch_size": patch_size,
        "patch_rows": demo_budget["patch_rows"],
        "patch_cols": demo_budget["patch_cols"],
        "visual_token_count": demo_budget["visual_tokens"],
        "attention_pairs": demo_budget["attention_pairs"],
        "projection_dimension": policy["projection_dimension"],
        "patches": patches,
        "normalized_preview": normalized_preview,
        "resolution_budgets": resolution_budgets,
        "engineering_decision": {
            "rule": "bajar patch_size aumenta detalle, pero tambien tokens visuales y coste cuadratico de atencion",
            "watch": ["visual_tokens", "attention_pairs", "padding_ratio", "texto_pequeno", "aspect_ratio"],
        },
        "valid": not issues,
        "issues": issues,
        "svg": svg_grid(image, patches),
    }


def markdown(report):
    lines = [
        "# Reporte de patches visuales",
        "",
        f"Imagen: `{report['image']['path']}` ({report['image']['width']}x{report['image']['height']}x{report['image']['channels']})",
        f"Patch size: `{report['patch_size']}`",
        f"Tokens visuales: `{report['visual_token_count']}`",
        f"Pares de atención si todos miran a todos: `{report['attention_pairs']}`",
        f"Gate válido: `{report['valid']}`",
        "",
        "## Primeros patches",
        "",
        "| Patch | Posición | RGB medio | Embedding de juguete |",
        "|---|---|---|---|",
    ]
    for patch in report["patches"][:8]:
        lines.append(
            f"| p{patch['patch_id']} | fila {patch['row']}, col {patch['col']} | {patch['mean_rgb']} | {patch['embedding_preview']} |"
        )
    lines.extend(
        [
            "",
            "## Presupuesto por resolución",
            "",
            "| Caso | Resolución | Patch | Tokens visuales | Pares atención | Ratio tokens | Ratio atención |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for item in report["resolution_budgets"]:
        lines.append(
            f"| {item['name']} | {item['width']}x{item['height']} | {item['patch_size']} | {item['visual_tokens']} | {item['attention_pairs']} | {item['token_ratio_vs_vit_224_p16']} | {item['attention_pair_ratio_vs_vit_224_p16']} |"
        )
    lines.extend(
        [
            "",
            "## Decisión de ingeniería",
            "",
            f"- Regla: {report['engineering_decision']['rule']}.",
            "- Vigila: " + ", ".join(report["engineering_decision"]["watch"]) + ".",
            "",
            "Si una captura contiene texto pequeño, quizá necesitas más resolución o patches más pequeños. Si solo necesitas una señal gruesa de producto, quizá puedes aceptar patches mayores y menos tokens.",
        ]
    )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-invalid", action="store_true")
    args = parser.parse_args()

    policy = load_json("contracts/patch_policy.json")
    resolutions = load_json("data/resolution_cases.json")
    report = build_report(policy, resolutions)

    if args.write:
        output = ROOT / "output"
        output.mkdir(exist_ok=True)
        svg = report.pop("svg")
        (output / "patch_report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (output / "patch_report.md").write_text(markdown(report), encoding="utf-8")
        (output / "patch_grid.svg").write_text(svg, encoding="utf-8")
    else:
        report_for_print = dict(report)
        report_for_print.pop("svg", None)
        print(json.dumps(report_for_print, ensure_ascii=False, indent=2))

    if args.fail_on_invalid and not report["valid"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
