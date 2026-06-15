# Decisión de release evaluada

Estado: **publicar_con_condiciones**.

## Lectura técnica

Esta decisión no sale de una sola métrica. Cruza RAG, metaevaluación del evaluador, calibración e interpretabilidad.
El paquete sirve para decidir si la release puede publicarse, publicarse con condiciones o bloquearse hasta corregir evidencia.

## Resumen de checks

- checks correctos: 13
- checks en revisión: 2
- checks bloqueantes: 0

## Hallazgos

- `rag_eval_report.json` / `long_tail_coverage` queda en `review`: observado `0.72`, requerido `>= 0.75`.
- `calibration_manifest.json` / `auto_error_wilson_upper` queda en `review`: observado `0.3604`, requerido `<= 0.28`.

## Decisión profesional

Publicaría solo con condiciones: canary pequeño, monitorización reforzada y revisión de los puntos marcados.

## Acciones siguientes

1. Convertir todo check bloqueante en tarea con owner y fecha.
2. Mantener los hashes de datos y política junto a la release.
3. Repetir calibración si cambian modelo, prompt, retrieval o mezcla de casos.
4. Revisar el contrato de explicación antes de ampliar consumidores.
