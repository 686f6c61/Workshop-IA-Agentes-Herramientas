# Decisión de release evaluada

Estado: **bloquear**.

## Lectura técnica

Esta decisión no sale de una sola métrica. Cruza RAG, metaevaluación del evaluador, calibración e interpretabilidad.
El paquete sirve para decidir si la release puede publicarse, publicarse con condiciones o bloquearse hasta corregir evidencia.

## Resumen de checks

- checks correctos: 7
- checks en revisión: 3
- checks bloqueantes: 5

## Hallazgos

- `rag_eval_report.json` / `groundedness` queda en `block`: observado `0.88`, requerido `>= 0.9`.
- `rag_eval_report.json` / `citation_acceptance` queda en `block`: observado `0.85`, requerido `>= 0.88`.
- `rag_eval_report.json` / `abstention_ok` queda en `block`: observado `0.84`, requerido `>= 0.86`.
- `rag_eval_report.json` / `long_tail_coverage` queda en `review`: observado `0.68`, requerido `>= 0.75`.
- `evaluator_metaeval.json` / `agreement` queda en `block`: observado `0.76`, requerido `>= 0.78`.
- `evaluator_metaeval.json` / `undue_pass_rate` queda en `block`: observado `0.09`, requerido `<= 0.08`.
- `evaluator_metaeval.json` / `borderline_overturn_rate` queda en `review`: observado `0.2`, requerido `<= 0.18`.
- `calibration_manifest.json` / `auto_error_wilson_upper` queda en `review`: observado `0.3604`, requerido `<= 0.28`.

## Decisión profesional

No publicaría la release. Corregiría primero los checks bloqueantes y repetiría el paquete completo.

## Acciones siguientes

1. Convertir todo check bloqueante en tarea con owner y fecha.
2. Mantener los hashes de datos y política junto a la release.
3. Repetir calibración si cambian modelo, prompt, retrieval o mezcla de casos.
4. Revisar el contrato de explicación antes de ampliar consumidores.
