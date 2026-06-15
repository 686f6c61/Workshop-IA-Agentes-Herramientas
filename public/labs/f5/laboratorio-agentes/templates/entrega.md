# Entrega del kit: Kit F5: laboratorio de agentes

## 0. Archivos del ZIP que he usado

- Entradas: `data/agent_requests.jsonl`, `data/agent_eval_cases.json`, `data/agent_runs_reference.json` y `data/agent_runs_regression.json`.
- Contratos o políticas: `contracts/agent_eval_contract.json` y `contracts/agent_runtime_policy.json`.
- Código ejecutado: `ops/check_student_submission.py`, `ops/evaluate_agent_routes.py` y `ops/run_agent_runtime.py`.
- Evidencias generadas: `output/agent_eval_decision.md`, `output/regression/agent_eval_decision.md`, `output/runtime_decision.md`, `output/student_submission_report.md`, `output/agent_eval_report.json` y `output/ci_agent_gate.json`.

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
