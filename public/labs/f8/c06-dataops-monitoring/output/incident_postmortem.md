# Postmortem DataOps

## Resumen

Estado de ingeniería: **block**.
Eventos revisados: `20`.
Eventos sin traza: `1`.
Eventos con spans obligatorios faltantes: `1`.

## Impacto

El gate operativo global queda en `block`. La ventana que requiere investigacion es `2026-06-08`, porque combina drift, latencia, perdida operativa y trazabilidad incompleta.

## Timeline técnico

| Paso | Evidencia |
|---|---|
| Deteccion | `monitor_dataops.py` genera alertas y scorecard. |
| Trazabilidad | `inspect_pipeline_engineering.py` revisa spans, orden, duracion e idempotencia. |
| Diagnóstico | Se cruzan slices críticos con eventos y trazas lentas o incompletas. |
| Accion | Se actualiza contrato, runbook o pipeline y se repite la ventana. |

## Señales técnicas

| Evento | Ventana | Problema |
|---|---|---|
| `p011` | `2026-06-08` | `trace_duration` |
| `p011` | `2026-06-08` | `slow_span: score` |
| `p012` | `2026-06-08` | `trace_duration` |
| `p012` | `2026-06-08` | `slow_span: score` |
| `p013` | `2026-06-08` | `missing_trace_id` |
| `p017` | `2026-06-08` | `missing_required_spans` |
| `p017` | `2026-06-08` | `slow_span: score` |

## Causa probable

La ventana combina un cambio fuerte de distribución con una versión de pipeline que pierde trazabilidad en al menos un evento y presenta spans de scoring lentos. No se concluye que el modelo sea el unico problema: también fallan operacion, cobertura y observabilidad.

## Acciones correctivas

1. Hacer `trace_id` obligatorio antes de emitir decisiones.
2. Anadir test de contrato para spans `ingest`, `validate`, `score`, `decide` y `emit`.
3. Revisar latencia de `score` en `pipe-1.4.2`.
4. Repetir la ventana en modo replay antes de aumentar automatización.
5. Mantener `2026-06-08` fuera de reentrenamiento hasta cerrar el gate.

## Criterio de cierre

El incidente se cierra cuando la misma ventana reprocesada tiene trazas completas, spans dentro de SLO o excepción documentada, slices críticos revisados y scorecard sin `block`.
