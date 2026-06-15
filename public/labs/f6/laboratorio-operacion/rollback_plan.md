# Plan de rollback

## Cuándo se ejecuta

- `ci_continuity_gate.status` no es `recovered`.
- `latency_p95_ms` o `review_queue_age_p95_minutes` rompen SLO.
- El índice candidato reduce aceptación de citas.
- Faltan atributos de traza para reconstruir la run.

## Qué vuelve

| Capa | Valor de vuelta |
|---|---|
| Tráfico | `candidate_weight=0` |
| Release | `support-rag@1.8.0` |
| Prompt | `prompt_v12` |
| Índice RAG | `rag_index_2026_05` |
| Router | `route_catalog@31` |
| Handoff | modo `critical_only` si la cola se satura |

## Verificación

1. Ejecutar `python3 ops/run_continuity_drill.py --events data/continuity_events_recovered.jsonl --output-dir output/recovered --write`.
2. Comprobar `output/recovered/ci_continuity_gate.json`.
3. Ejecutar `python3 ops/ai/release_gate.py --write`.
4. Confirmar que el caso entra en `regression_cases.json`.
