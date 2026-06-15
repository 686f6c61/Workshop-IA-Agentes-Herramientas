# Entrega del kit: Kit F7: prácticas de evaluación por capítulo

## 0. Archivos del ZIP que he usado

- Entradas: `evals/classification_cases.jsonl`, `evals/eval_cases.jsonl`, `evals/eval_hypothesis.json` y `evals/evaluator_calibration_cases.json`.
- Contratos o políticas: `ops/ai/error_taxonomy.json`, `ops/ai/eval_policy.json`, `ops/ai/rag_eval_policy.json` y `ops/ai/threshold_policy.json`.
- Código ejecutado: `ops/ai/eval_runner.py`, `ops/ai/evaluator_audit.py`, `ops/ai/rag_eval.py` y `ops/ai/threshold_eval.py`.
- Evidencias generadas: `output/c01_decision.md`, `output/c02_decision.md`, `output/c03_decision.md`, `output/c04_decision.md`, `output/decision.md` y `output/evaluator_audit_decision.md`.

## 1. Contexto

Describe en tres o cuatro líneas qué caso has decidido estudiar y por qué se parece a un problema real de clase, producto, datos, operación o investigación aplicada.

## 2. Qué he ejecutado

```bash
make run
make test
```

Anota si ambos comandos pasan. Si algo falla, explica qué falla antes de interpretar resultados.

## 3. Qué he cambiado

Indica qué dato, contrato, política, plantilla, umbral o código has tocado. No basta decir "he cambiado el JSON": explica qué representa ese cambio y qué pasaría si ese supuesto apareciera en un sistema real.

## 4. Resultado

Resume los artefactos generados en `output/`: decisión, métricas, trazas, tablas, gates o informes.

## 5. Decisión técnica

Escribe qué harías en un proyecto real: publicar, bloquear, pedir revisión humana, recoger más datos, cambiar un umbral, repetir evaluación o preparar un piloto.

## 6. Riesgos y límites

Explica qué no demuestra el kit, qué supuesto podría romperse y qué dato adicional pedirías antes de confiar más.

## 7. Próximo paso

Propón una mejora pequeña y ejecutable: un caso nuevo, un test, una métrica, una consulta, una política, un runbook o un gate de CI.
