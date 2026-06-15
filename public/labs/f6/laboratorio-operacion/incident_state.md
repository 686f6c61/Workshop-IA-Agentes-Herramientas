# Estado vivo de incidencia

Servicio: `support-rag`.
Release afectada: `support-rag@1.9.0-rc1`.
Severidad inicial: `SEV-2`.
Owner de guardia: `equipo-ia`.
Cadencia de actualización: 15 minutos.

## Síntomas

- `latency_p95_ms` supera el SLO durante canary.
- `citation_acceptance_rate` cae por debajo del mínimo esperado.
- `review_queue_age_p95_minutes` aumenta por acumulación de casos enviados a revisión.

## Hipótesis actuales

1. El índice candidato recupera más documentos, pero también introduce ruido.
2. El router mantiene tráfico en una ruta cara durante degradación.
3. La cola de revisión no entra aún en modo degradado.

## Acciones en curso

| Acción | Owner | Estado | Verificación |
|---|---|---|---|
| Bajar canary a 0% | plataforma IA | preparado | `release_id` vuelve a baseline en trazas |
| Activar ruta segura | plataforma IA | preparado | p95 baja por debajo de SLO |
| Añadir caso de regresión | EvalOps | pendiente | `regression_case.json` creado |
| Ejecutar postmortem | equipo IA | pendiente | acciones con dueño y fecha |

## No tocar sin coordinar

- No cambiar prompt y modelo a la vez.
- No reconstruir el índice durante la mitigación.
- No borrar trazas ni payloads ya anonimizados.

## Próxima actualización

Revisar `output/ci_continuity_gate.json`, confirmar si el estado es `recovered` y decidir si se mantiene rollback o se abre nueva candidata.
