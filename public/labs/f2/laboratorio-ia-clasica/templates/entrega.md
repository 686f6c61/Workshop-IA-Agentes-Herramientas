# Entrega del kit: F2 · Laboratorio de IA clásica

## 0. Archivos del ZIP que he usado

- Entradas: `data/csp_schedule.json` y `data/support_graph.json`.
- Contratos o políticas: `contracts/ia_clasica_lab_contract.json`.
- Código ejecutado: `ops/check_student_submission.py`, `ops/evaluate_symbolic_plan.py` y `ops/solve_csp_schedule.py`.
- Evidencias generadas: `output/csp_decision.md`, `output/symbolic_plan_decision.md`, `output/csp_solution.json`, `output/symbolic_plan_report.json`, `output/csp_trace.jsonl` y `output/symbolic_plan_trace.jsonl`.

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
