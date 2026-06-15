# Entrega · F12 C10 · Evaluación multimodal

## Contexto

- Sistema o flujo evaluado:
- Modalidades implicadas:
- Decisión que quiero tomar:
- Versión del modelo, prompt o pipeline:
- Fecha de ejecución:

## Ejecución

Comandos ejecutados:

```bash
make run
make test
```

Archivos revisados:

- `output/eval_report.md`
- `output/case_scores.csv`
- `output/slice_scores.csv`
- `output/annotation_queue.csv`
- `output/regression_gate.md`
- `output/multimodal_eval_dashboard.svg`

## Lectura de resultados

- Decisión global del gate:
- Score global:
- Slices débiles:
- Casos que van a revisión:
- Caso que más me preocupa:
- Evidencia que falta o queda incompleta:
- Coste y latencia que aceptaría en producción:

## Cambio realizado

Describe qué has cambiado:

- Caso nuevo añadido en `data/eval_cases.json`:
- Gate modificado en `contracts/eval_policy.json`:
- Métrica o umbral que has tocado:

## Decisión técnica

Marca una opción y justifica:

- [ ] Publicaría.
- [ ] Publicaría con condiciones.
- [ ] Revisaría antes de publicar.
- [ ] Bloquearía el release.

Justificación:

## Límites

- Qué no mide esta eval:
- Qué podría estar sesgado:
- Qué caso real falta todavía:
- Qué revisaría una persona experta:

## Próximo paso

- Nuevo caso de regresión:
- Nuevo slice:
- Nueva evidencia obligatoria:
- Nueva métrica:
