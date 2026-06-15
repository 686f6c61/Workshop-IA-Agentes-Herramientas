# Entrega del kit: F11 · Laboratorio de producto y UX

## 0. Archivos del ZIP que he usado

- Entradas: `data/feature_candidates.csv`, `data/ux_review_sessions.csv` y `data/eval_snapshot.json`.
- Contratos o políticas: `contracts/product_ai_release_policy.json`.
- Código ejecutado: `ops/check_student_submission.py`, `ops/review_ux_flows.py` y `ops/score_product_readiness.py`.
- Evidencias generadas: `output/final_product_packet.md`, `output/metric_tree.md`, `output/nota_de_decision.md`, `output/product_release_decision.md`, `output/student_submission_report.md` y `output/ux_contract.md`.

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
