# Reward card

Escenario: `rag_internal_policy_reward_bad`
Version: `0.1.0`
Estado: `block`

## Objetivo

Recompensa rota: premia longitud, estilo y coste por encima de evidencia.

## Terminos

| Termino | Peso | Categoria | Verificador |
|---|---:|---|---|
| `correctness` | 0.24 | `objective` | `human_or_task_grader_v1` |
| `evidence` | 0.06 | `objective` | `citation_support_v1` |
| `format` | 0.05 | `guardrail` | `json_schema_v1` |
| `style` | 0.22 | `proxy` | `none` |
| `length_bonus` | 0.28 | `proxy` | `none` |
| `latency_cost` | -0.03 | `cost` | `trace_metrics_v1` |

## Normalizacion

| Termino | Metodo | Fuente |
|---|---|---|
| `latency_cost` | `raw_ms_bucket` | `trace_metrics_v1` |

## Restricciones duras

| Restriccion | Verificador | Motivo |
|---|---|---|
| `valid_output_contract` | `none` | Declarado, pero no conectado a una prueba reproducible. |

## Casos

| Caso | Slice | Ganador | Esperado | Estado |
|---|---|---|---|---|
| `rag_cita_valida` | `rag` | `b` | `a` | `review` |
| `sin_fuente` | `rag` | `b` | `a` | `review` |
| `json_contrato` | `salida_estructurada` | `b` | `a` | `review` |
| `coste_controlado` | `coste` | `b` | `a` | `review` |

## Limites

- La recompensa es una aproximacion, no una prueba de verdad.
- Los pesos deben revisarse si cambia el producto, el RAG, el modelo base o el contrato de salida.
- Los casos ocultos deben rotar para evitar que la reward card solo mida fixtures conocidos.
