# Politica de trazabilidad de datos

## Alcance

Esta política aplica al mini sistema de priorizacion académica del laboratorio final del facsímil 8.

## Regla principal

Cada evento usado para evaluar o decidir debe poder reconstruirse. Eso exige:

- `case_id`: identificador estable del caso.
- `trace_id`: identificador de traza de la decisión.
- `split`: train, validation o test.
- `decision`: salida operativa producida.
- `experiment_variant`: variante vista por el caso.

## Criterio de cierre

El control de trazabilidad se cierra solo si `missing_trace_rate == 0.0`.
Una fila sin `trace_id` bloquea publicación porque no permite reconstruir la decisión.

## Evidencia esperada

- `output/final_review_report.json`
- `output/source_evidence_review.md`
- Dataset corregido con `trace_id` completo.
