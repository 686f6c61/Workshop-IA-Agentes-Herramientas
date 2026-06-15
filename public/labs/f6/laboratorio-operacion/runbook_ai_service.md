# Runbook de operación: `support-rag`

Este documento es la versión legible para el equipo. Resume qué mirar, qué decidir y qué artefactos generar durante un problema de operación.

## Primero mirar

- `output/operational_readiness.json` para saber si el servicio estaba listo.
- `output/continuity_report.json` para ver síntomas, estado y mitigaciones.
- `output/ci_continuity_gate.json` para decidir si el sistema se recuperó.
- `incident_state.md` para no duplicar decisiones durante la incidencia.

## Decisiones posibles

| Decisión | Cuándo |
|---|---|
| Mantener vigilancia | Todo pasa y hay trazas completas. |
| Pausar canary | Hay señal dudosa pero impacto limitado. |
| Rollback | Hay breach de SLO, coste, citas o contrato. |
| Modo degradado | La cola humana o proveedor externo impide cumplir SLO. |

## Salida esperada

Al cerrar, deben existir:

- `postmortem.md`
- `regression_cases.json`
- `rollback_plan.md`
- `output/recovered/ci_continuity_gate.json`

La pregunta final no es “¿volvió a funcionar?”, sino “¿qué dejamos para que el siguiente fallo sea más pequeño?”.
