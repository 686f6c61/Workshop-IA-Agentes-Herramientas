# Plan de siguiente experimento

Slice prioritario: `language=en`.

## Hipótesis

Una plantilla guiada y una recuperación documental revisada para el slice prioritario reducirán fallos sin romper citas, latencia ni feedback.

## Diseño

| Pieza | Decisión |
|---|---|
| Unidad | `case_id`. |
| Tratamiento | Plantilla guiada + recuperación documental revisada. |
| Control | Flujo actual. |
| Métrica primaria | `resolved_day_7`. |
| Guardrails | `citation_valid`, `latency_ms`, `negative_feedback`, `cost_eur`. |
| Exposure event | `case_id`, variante, versión de prompt, versión de retriever y `trace_id`. |
| Decisión si queda en review | No rollout general; ampliar muestra, corregir instrumentación o limitar alcance. |

## Conexión con el capítulo 07

Este plan no demuestra causalidad por estar escrito. Debe ejecutarse con asignación, exposición real, ventana de maduración y regla de analisis definida antes de mirar resultados.
