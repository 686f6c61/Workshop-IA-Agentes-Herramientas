# Reward card

Escenario: `rag_internal_policy_reward`
Version: `1.0.0`
Estado: `pass`

## Objetivo

Premiar respuestas correctas, con evidencia, formato validable, abstencion cuando falta fuente y coste razonable.

## Terminos

| Termino | Peso | Categoria | Verificador |
|---|---:|---|---|
| `correctness` | 0.4 | `objective` | `human_or_task_grader_v1` |
| `evidence` | 0.22 | `objective` | `citation_support_v1` |
| `format` | 0.13 | `guardrail` | `json_schema_v1` |
| `abstention` | 0.12 | `guardrail` | `answerability_v1` |
| `latency_cost` | -0.07 | `cost` | `trace_metrics_v1` |
| `token_cost` | -0.04 | `cost` | `trace_metrics_v1` |
| `tool_cost` | -0.02 | `cost` | `trace_metrics_v1` |

## Normalizacion

| Termino | Metodo | Fuente |
|---|---|---|
| `latency_cost` | `minmax_by_slice` | `trace_metrics_v1` |
| `token_cost` | `minmax_by_slice` | `trace_metrics_v1` |
| `tool_cost` | `count_to_unit_interval` | `trace_metrics_v1` |

## Restricciones duras

| Restriccion | Verificador | Motivo |
|---|---|---|
| `valid_output_contract` | `json_schema_v1` | La salida debe ser parseable antes de puntuar estilo o coste. |
| `supported_claims` | `citation_support_v1` | Una respuesta con afirmaciones de política interna debe estar soportada por documentos recuperados. |
| `answerability_or_abstention` | `answerability_v1` | Si no hay evidencia suficiente, la respuesta correcta es abstenerse y explicar la falta de fuente. |

## Casos

| Caso | Slice | Ganador | Esperado | Estado |
|---|---|---|---|---|
| `rag_cita_valida` | `rag` | `a` | `a` | `pass` |
| `rag_sin_fuente` | `rag` | `b` | `b` | `pass` |
| `json_contrato` | `salida_estructurada` | `b` | `b` | `pass` |
| `sql_ejecutable` | `sql` | `a` | `a` | `pass` |
| `coste_controlado` | `coste` | `a` | `a` | `pass` |
| `herramienta_timeout` | `herramientas` | `b` | `b` | `pass` |
| `privacidad_minimizacion` | `privacidad` | `a` | `a` | `pass` |
| `formato_y_evidencia` | `salida_estructurada` | `a` | `a` | `pass` |
| `sensibilidad_evidencia` | `rag` | `a` | `a` | `pass` |

## Limites

- La recompensa es una aproximacion, no una prueba de verdad.
- Los pesos deben revisarse si cambia el producto, el RAG, el modelo base o el contrato de salida.
- Los casos ocultos deben rotar para evitar que la reward card solo mida fixtures conocidos.
