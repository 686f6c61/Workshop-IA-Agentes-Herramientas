# Plan de corrección de datos

| Prioridad | Problema | Estado | Acción | Capítulo |
|---:|---|---|---|---|
| 1 | `missing_trace_rate` | `block` | Completar `trace_id` y comprobar que toda decision se puede reconstruir. | `08.06` |
| 2 | `missing_required_fields_rate` | `block` | Bloquear ingesta incompleta antes de crear el dataset de evaluación. | `08.02` |
| 3 | `latency_p95_ms` | `review` | Revisar ruta lenta, RAG, proveedor o fallback antes de ampliar alcance. | `08.06` |
| 4 | `test_accuracy` | `review` | Revisar split, umbral, errores y representatividad del test. | `08.03` |
| 5 | `critical_slice_miss_rate:language=en` | `review` | Analizar el slice como unidad de decisión, no esconderlo en la media global. | `08.05` |
| 6 | `critical_slice_miss_rate:segment=practicas` | `review` | Analizar el slice como unidad de decisión, no esconderlo en la media global. | `08.05` |
| 7 | `critical_slice_miss_rate:source=form` | `review` | Analizar el slice como unidad de decisión, no esconderlo en la media global. | `08.05` |

## Criterio de cierre

Una corrección se cierra cuando se regenera el reporte con el mismo contrato y el check deja de bloquear o queda justificado como alcance limitado.

La entrega no puede cambiar `final_review_contract.json` para parecer mejor. Debe demostrar que `trace_id` permite reconstruir cada decisión y que `has_required_fields` bloquea filas incompletas antes de crear el dataset de evaluación.
