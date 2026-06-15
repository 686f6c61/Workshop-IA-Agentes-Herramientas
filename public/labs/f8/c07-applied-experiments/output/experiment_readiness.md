# Readiness del experimento

Estado readiness: **review**.

## MDE y muestra

Baseline: `0.58`.
Alpha: `0.05`.
Potencia: `0.8`.
MDE planificado: `0.05`.
n actual por variante: `12`.
n recomendado por variante: `1530`.
MDE aproximado con n actual: `0.564504`.

## Checklist operativo

| Check | Estado | Mensaje |
|---|---|---|
| `aa_test` | `review` | Ejecutar A/A antes del A/B para validar instrumentación, reparto y métricas. |
| `exposure_event` | `pass` | Registrar evento de exposición `experiment_exposure`. |
| `persistent_assignment` | `pass` | La unidad debe conservar variante durante la ventana de medición. |
| `planned_sample_size` | `review` | n actual por variante 12; n recomendado por variante para MDE 0.05: 1530. |
| `peeking_policy` | `pass` | No mirar para decidir antes de cerrar la ventana planificada. |
| `rollout_policy` | `pass` | Ramp inicial 5%, pasos [5, 25, 50, 100]. |

## Lectura

El experimento del kit sirve para aprender y detectar señal. Para publicar una decisión global con el MDE planificado, haría falta más muestra, A/A previo documentado y la misma política de peeking cerrada antes de iniciar.
