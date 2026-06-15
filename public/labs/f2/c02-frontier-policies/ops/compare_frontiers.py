#!/usr/bin/env python3
import argparse
import heapq
import json
from collections import deque
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def reconstruct(parent, goal):
    if goal not in parent:
        return []
    path = [goal]
    while parent[path[-1]] is not None:
        path.append(parent[path[-1]])
    return list(reversed(path))


def path_cost(graph, path):
    if not path:
        return None
    cost = 0
    for left, right in zip(path, path[1:]):
        for edge in graph["edges"].get(left, []):
            if edge["to"] == right:
                cost += edge["cost"]
                break
        else:
            return None
    return cost


def result(name, graph, parent, trace, generated, max_frontier):
    path = reconstruct(parent, graph["goal"])
    cost = path_cost(graph, path)
    return {
        "algorithm": name,
        "found": bool(path),
        "path": path,
        "depth": max(len(path) - 1, 0) if path else None,
        "cost": cost,
        "expanded": len(trace),
        "generated": generated,
        "max_frontier": max_frontier,
        "trace": trace,
    }


def bfs(graph):
    start, goal = graph["start"], graph["goal"]
    frontier = deque([start])
    visited = {start}
    parent = {start: None}
    trace = []
    generated = 1
    max_frontier = 1
    while frontier:
        current = frontier.popleft()
        trace.append(current)
        if current == goal:
            break
        for edge in graph["edges"].get(current, []):
            nxt = edge["to"]
            if nxt not in visited:
                visited.add(nxt)
                parent[nxt] = current
                frontier.append(nxt)
                generated += 1
        max_frontier = max(max_frontier, len(frontier))
    return result("BFS", graph, parent, trace, generated, max_frontier)


def dfs(graph):
    start, goal = graph["start"], graph["goal"]
    frontier = [start]
    visited = {start}
    parent = {start: None}
    trace = []
    generated = 1
    max_frontier = 1
    while frontier:
        current = frontier.pop()
        trace.append(current)
        if current == goal:
            break
        # Reversed push keeps the listed successor order as the first DFS branch.
        for edge in reversed(graph["edges"].get(current, [])):
            nxt = edge["to"]
            if nxt not in visited:
                visited.add(nxt)
                parent[nxt] = current
                frontier.append(nxt)
                generated += 1
        max_frontier = max(max_frontier, len(frontier))
    return result("DFS", graph, parent, trace, generated, max_frontier)


def ucs(graph):
    start, goal = graph["start"], graph["goal"]
    counter = 0
    frontier = [(0, counter, start)]
    parent = {start: None}
    best = {start: 0}
    trace = []
    generated = 1
    max_frontier = 1
    closed = set()
    while frontier:
        cost, _, current = heapq.heappop(frontier)
        if current in closed:
            continue
        closed.add(current)
        trace.append(current)
        if current == goal:
            break
        for edge in graph["edges"].get(current, []):
            nxt = edge["to"]
            new_cost = cost + edge["cost"]
            if nxt not in best or new_cost < best[nxt]:
                best[nxt] = new_cost
                parent[nxt] = current
                counter += 1
                heapq.heappush(frontier, (new_cost, counter, nxt))
                generated += 1
        max_frontier = max(max_frontier, len(frontier))
    return result("UCS", graph, parent, trace, generated, max_frontier)


def depth_limited(graph, limit):
    start, goal = graph["start"], graph["goal"]
    stack = [(start, 0, [start], 0)]
    trace = []
    generated = 1
    max_frontier = 1
    while stack:
        current, depth, path, cost = stack.pop()
        trace.append(current)
        if current == goal:
            parent = {path[0]: None}
            for left, right in zip(path, path[1:]):
                parent[right] = left
            return result(f"IDS_L{limit}", graph, parent, trace, generated, max_frontier)
        if depth == limit:
            continue
        for edge in reversed(graph["edges"].get(current, [])):
            nxt = edge["to"]
            if nxt not in path:
                stack.append((nxt, depth + 1, path + [nxt], cost + edge["cost"]))
                generated += 1
        max_frontier = max(max_frontier, len(stack))
    return {
        "algorithm": f"IDS_L{limit}",
        "found": False,
        "path": [],
        "depth": None,
        "cost": None,
        "expanded": len(trace),
        "generated": generated,
        "max_frontier": max_frontier,
        "trace": trace,
    }


def ids(graph, max_depth):
    total_expanded = 0
    total_generated = 0
    max_frontier = 0
    full_trace = []
    for limit in range(max_depth + 1):
        current = depth_limited(graph, limit)
        total_expanded += current["expanded"]
        total_generated += current["generated"]
        max_frontier = max(max_frontier, current["max_frontier"])
        full_trace.extend([f"L{limit}:{node}" for node in current["trace"]])
        if current["found"]:
            current["algorithm"] = "IDS"
            current["expanded"] = total_expanded
            current["generated"] = total_generated
            current["max_frontier"] = max_frontier
            current["trace"] = full_trace
            return current
    return {
        "algorithm": "IDS",
        "found": False,
        "path": [],
        "depth": None,
        "cost": None,
        "expanded": total_expanded,
        "generated": total_generated,
        "max_frontier": max_frontier,
        "trace": full_trace,
    }


def render_markdown(graph, rows):
    lines = [
        "# Decisión: políticas de frontera",
        "",
        f"Grafo: `{graph['name']}`. Inicio `{graph['start']}`, meta `{graph['goal']}`.",
        "",
        "| Algoritmo | Camino | Profundidad | Coste | Expandidos | Generados | Frontera máx. |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        path = " -> ".join(row["path"]) if row["path"] else "sin solución"
        lines.append(
            f"| {row['algorithm']} | {path} | {row['depth']} | {row['cost']} | "
            f"{row['expanded']} | {row['generated']} | {row['max_frontier']} |"
        )

    lines.extend(["", "## Trazas", ""])
    for row in rows:
        trace = " -> ".join(row["trace"])
        lines.append(f"- **{row['algorithm']}**: {trace}")

    valid = [row for row in rows if row["found"]]
    cheapest = min(valid, key=lambda row: row["cost"]) if valid else None
    shallowest = min(valid, key=lambda row: row["depth"]) if valid else None
    lines.extend(["", "## Lectura técnica", ""])
    if cheapest:
        lines.append(f"- El menor coste encontrado lo da **{cheapest['algorithm']}** con coste {cheapest['cost']}.")
    if shallowest:
        lines.append(f"- La menor profundidad encontrada la da **{shallowest['algorithm']}** con profundidad {shallowest['depth']}.")
    lines.extend(
        [
            "- BFS optimiza pasos solo cuando los costes son uniformes.",
            "- DFS depende del orden de sucesores y no debería usarse sin límite en espacios infinitos.",
            "- UCS ordena por coste acumulado y es la referencia cuando los costes son positivos y no hay heurística.",
            "- IDS reexplora nodos, pero controla memoria con límites crecientes.",
        ]
    )
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--fail-on-invalid", action="store_true")
    args = parser.parse_args()

    graph = load_json(ROOT / "data" / "weighted_graph.json")
    policy = load_json(ROOT / "contracts" / "frontier_policy.json")
    rows = [bfs(graph), dfs(graph), ucs(graph), ids(graph, policy["ids_max_depth"])]

    output_dir = ROOT / "output"
    if args.write:
        output_dir.mkdir(exist_ok=True)
        (output_dir / "frontier_report.json").write_text(
            json.dumps(rows, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (output_dir / "frontier_decision.md").write_text(
            render_markdown(graph, rows) + "\n",
            encoding="utf-8",
        )

    invalid = [row for row in rows if not row["found"]]
    print(f"algoritmos: {len(rows)}")
    print(f"sin_solucion: {len(invalid)}")
    print(f"salida: {output_dir if args.write else 'no escrita'}")
    if args.fail_on_invalid and invalid:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
