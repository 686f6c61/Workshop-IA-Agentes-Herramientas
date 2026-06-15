# On-call handoff: servicio support-rag

## Estado actual

- Servicio: `support-rag`
- Versión estable: `support-rag@1.9.0`
- Versión candidata: `support-rag@2.0.0`
- Riesgo principal: degradación simultánea de latencia, citas y cola de revisión.

## Señales que debe mirar la siguiente persona

1. `latency_p95_ms` por proveedor.
2. `citation_acceptance_rate` por `index_version`.
3. `review_queue_age_p95_minutes`.
4. Eventos nuevos en `output/continuity_report.json`.
5. Casos añadidos a `evals/regression_cases.jsonl`.

## Decisiones ya tomadas

- Si cae aceptación de citas, volver a índice estable.
- Si sube latencia de `provider_a`, mover ruta crítica a `provider_b`.
- Si envejece la cola, activar modo `review_queue_only`.

## Pendientes

- Ejecutar `python3 ops/check_student_submission.py` antes de cerrar el laboratorio.
- Confirmar que el caso de regresión añadido protege el fallo observado.
- Completar `postmortem.md` con causa contribuyente y acción preventiva.
