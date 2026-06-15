# Riesgo residual de datos

## Aceptable con condiciones

| Condicion | Motivo | Owner |
|---|---|---|
| `latency_p95_ms` en revisión | Puede limitarse el piloto mientras se optimiza la ruta lenta. | `owner-ops` |
| `test_accuracy` en revisión | Puede permitir investigacion, no automatización. | `owner-eval` |

## No aceptable para publicar

| Condicion | Motivo |
|---|---|
| `missing_trace_rate > 0.0` | Sin traza no se reconstruye la decisión. |
| `missing_required_fields_rate > 0.0` | La ingesta permite datos incompletos. |

## Criterio

El riesgo residual se acepta solo con owner, fecha de repeticion del gate y alcance limitado.
