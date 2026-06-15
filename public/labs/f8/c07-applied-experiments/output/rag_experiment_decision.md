# Decisión experimento RAG

Estado: **review**.

| Métrica | Control | Treatment | Delta |
|---|---:|---:|---:|
| `answer_accepted` | `0.625` | `0.875` | `0.25` |
| `citation_valid` | `0.75` | `0.875` | `0.125` |
| `retrieval_precision` | `0.575` | `0.75125` | `0.17625` |
| `latency_ms` | `848.75` | `1012.5` | `163.75` |
| `cost_eur` | `0.023125` | `0.031` | `0.007875` |

## Motivos

- el reranker mejora aceptacion y precision, pero aumenta coste y latencia.
- la metrica citation_valid no mejora de forma perfecta y debe ser guardrail.
- hay pocos ejemplos por tipo de consulta.

## Decisión

No se publica globalmente. Se amplia muestra y se mantiene citation_valid como guardrail antes de probar rollout.
