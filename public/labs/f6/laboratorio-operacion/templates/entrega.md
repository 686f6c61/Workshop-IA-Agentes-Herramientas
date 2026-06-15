# Entrega del kit: Kit F6: laboratorio de operación

## 0. Archivos del ZIP que he usado

- Entradas: `data/continuity_events.jsonl` y `data/continuity_events_recovered.jsonl`.
- Contratos o políticas: `contracts/readiness_manifest_complete.json`, `contracts/readiness_manifest_incomplete.json`, `contracts/readiness_policy.json` y `ops/ai/slo_policy.yaml`.
- Código ejecutado: `ops/ai/operational_readiness.py`, `ops/ai/release_gate.py`, `ops/check_student_submission.py` y `ops/operational_readiness.py`.
- Evidencias generadas: `output/complete/readiness_decision.md`, `output/continuity_decision.md`, `output/postmortem.md`, `output/readiness_decision.md`, `output/recovered/continuity_decision.md` y `output/recovered/postmortem.md`.

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
