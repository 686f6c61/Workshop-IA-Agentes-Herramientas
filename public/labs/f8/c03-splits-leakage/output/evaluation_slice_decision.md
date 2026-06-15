# Decisión de evaluación por slices

Split evaluado: `test`.
Estrategia de split: `time_group_holdout`.
Decisión: `review_test_too_small`.

## Métrica global

- n: 4
- accuracy: 0.75
- intervalo aproximado 95%: {'low': 0.3256, 'high': 1.0, 'standard_error': 0.2165}
- latencia media: 942.5 ms

## Fallos

- `s023`: esperado `escalate`, predicho `answer`, producto `matricula`.

## Lectura

Esta evaluación es útil como ejercicio operativo, pero el test es pequeño. No cierres una afirmacion publica con está muestra: aumenta el holdout o repite la medición con más casos versionados.
