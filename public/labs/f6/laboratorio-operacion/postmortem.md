# Postmortem: degradación controlada en `support-rag`

## Resumen

Durante un canary de `support-rag@1.9.0-rc1` se detectaron degradaciones en latencia, aceptación de citas y cola de revisión. El sistema conserva trazas suficientes para reconstruir la incidencia y proponer mitigaciones.

## Impacto

- La degradación afecta a tráfico canary.
- No se elimina evidencia.
- Las acciones persistentes quedan contenidas por handoff y fallback.

## Línea temporal

| Hora | Evento |
|---|---|
| 10:00 | Candidate entra en canary. |
| 10:08 | Latencia p95 supera SLO. |
| 10:12 | Caen citas aceptadas en RAG. |
| 10:15 | Se propone bajar canary y volver a índice estable. |

## Causas contribuyentes

- Índice candidato con más recuperación pero menor precisión.
- Router sin degradación temprana por coste/latencia.
- Cola humana sin modo reducido al empezar la degradación.

## Acciones

| Acción | Owner | Verificación |
|---|---|---|
| Añadir regresión RAG | EvalOps | `regression_case.json` en el laboratorio |
| Probar rollback de índice | plataforma IA | drill recuperado queda `recovered` |
| Ajustar gate de canary | plataforma IA | bloquea si coste o latencia suben juntas |
| Actualizar runbook | equipo IA | `runbook_ai_service.md` revisado |

## Aprendizaje

La operación mejora cuando cada incidente deja una pieza ejecutable: caso de regresión, consulta, gate o runbook. Sin eso, el postmortem queda como memoria narrativa y no como ingeniería.
