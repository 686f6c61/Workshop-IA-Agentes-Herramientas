# Decisión del experimento

Estado: **review**.

## Lectura

ATE observado en `resolved`: `0.25`.
Intervalo 95%: `[-0.115224, 0.615224]`.
Efecto CUPED: `0.25` con covariable `historical_resolution_rate`.

## Motivos

- readiness en revisión: aa_test.
- readiness en revisión: planned_sample_size.
- efecto prometedor pero intervalo aún cruza el efecto mínimo.

## Decisión operativa

No se publica automáticamente como cambio global. La señal es positiva, los guardrails pasan y la asignación está equilibrada, pero el intervalo sigue siendo ancho. El siguiente paso es ampliar muestra o repetir una ventana con el mismo contrato.

## Entregable de ingeniería

Guardar `experiment_report.json`, `slice_effects.csv`, `experiment_scorecard.csv` y este documento junto a la versión de producto que se estaba evaluando.
