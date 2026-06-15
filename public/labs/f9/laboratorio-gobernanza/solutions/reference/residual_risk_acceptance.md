# Aceptacion de riesgo residual

## Aceptable con condiciones

| Condición | Por que se puede aceptar temporalmente | Owner | Próxima revisión |
|---|---|---|---|
| `post_deployment_monitoring` | El asistente académico ya está en producción, pero necesita reporte mensual automatizado. | `owner-ops` | 21 días |
| `memory_ttl_and_source_integrity` | La memoria queda limitada por política, pero falta prueba completa de purga. | `owner-privacy` | 21 días |

## No aceptable para ampliar alcance

| Condición | Motivo |
|---|---|
| `least_agency_tool_boundary` | Si no se separa preparar de ejecutar, el agente conserva demasiada capacidad operativa. |
| `dpia_retention_decision` | Sin decisión formal de retención, no se debe ampliar un flujo con datos personales. |

## Criterio

El riesgo residual solo se acepta con owner, fecha, evidencia esperada y nuevo gate.
