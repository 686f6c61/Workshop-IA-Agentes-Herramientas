# Kit F10 C05: preferencias y post-training

Este kit acompaña el capítulo 05 del facsímil 10. Audita un dataset de preferencias antes de usarlo para DPO, reward modeling, RLHF o RLVR.

El objetivo no es entrenar un LLM. El objetivo es aprender a bloquear un dataset que enseñaría mal: pares contradictorios, bajo acuerdo, margen negativo, verificadores ausentes o sesgo de longitud.

## Ejecutar

Desde esta carpeta:

```bash
python3 ops/audit_preference_dataset.py --write
cat output/preference_dataset_decision.md
python3 -m json.tool output/preference_dataset_report.json
cat output/reward_card.md
```

Salida esperada:

```text
status=pass
pairs=12
```

Para el escenario que debe bloquear:

```bash
python3 ops/audit_preference_dataset.py \
  --pairs data/preference_pairs_bad.jsonl \
  --output output_bad \
  --write
cat output_bad/preference_dataset_decision.md
```

Salida esperada:

```text
status=block
pairs=6
```

## Archivos

| Archivo | Papel |
|---|---|
| `data/preference_pairs.jsonl` | Dataset sano de pares `prompt/chosen/rejected`. |
| `data/preference_pairs_bad.jsonl` | Dataset con contradicciones, bajo acuerdo y margen negativo. |
| `contracts/preference_dataset_contract.json` | Gate de calidad para decidir si el dataset puede pasar a experimento. |
| `schemas/preference_pair.schema.json` | Esquema JSON de referencia para cada par. |
| `guides/annotation_guide.md` | Guía para escribir pares de preferencia con criterio repetible. |
| `configs/dpo_minimal_config.yaml` | Configuración mínima de referencia para leer un experimento DPO/LoRA. |
| `ops/audit_preference_dataset.py` | Calcula métricas, checks, scorecard y tarjeta de señal. |
| `output/preference_dataset_report.json` | Reporte generado. |
| `output/pair_scorecard.csv` | Diagnóstico por par. |
| `output/preference_dataset_decision.md` | Decisión técnica. |
| `output/reward_card.md` | Tarjeta breve de la señal de preferencia. |

## Qué deberías mirar

1. `chosen_win_rate`: cuántas veces la respuesta elegida tiene mayor puntuación que la rechazada.
2. `avg_reward_margin`: margen medio entre elegida y rechazada.
3. `avg_agreement`: acuerdo medio de evaluadores o fuentes de revisión.
4. `low_agreement_rate`: proporción de pares ambiguos.
5. `verifier_coverage`: cuántos pares tienen un checker o grader disponible.
6. `reversed_conflicts`: pares donde el mismo prompt aparece con decisión contraria.
7. `length_bias_ratio`: si se está premiando longitud en vez de calidad.
8. `pair_scorecard.csv`: qué pares concretos explican el bloqueo.

## Cómo lo adaptas a un proyecto propio

1. Cambia `preference_pairs.jsonl` por pares reales de tu producto.
2. Mantén `preference_reason`; si no puedes explicar por qué gana una respuesta, el par es débil.
3. Separa familias de tarea: RAG, código, soporte, SQL, herramientas, privacidad.
4. Ajusta `preference_dataset_contract.json` a tu tolerancia.
5. Ejecuta el escenario roto como test de que el gate bloquea de verdad.
6. Convierte `reward_card.md` en parte del expediente de entrenamiento.
7. No pases a DPO, ORPO, KTO, reward modeling o RLHF si el status es `block`.

## Qué entregaría un alumno

1. Reporte JSON generado.
2. Scorecard CSV interpretado.
3. Decisión Markdown.
4. Reward card.
5. Propuesta de tres pares nuevos para una familia de tarea concreta.
6. Explicación de qué check falla en el dataset roto y cómo lo corregiría.

## Qué te llevas

Te llevas una práctica ejecutable sobre preferencias y post-training, con datos editables, contratos y umbrales, configuración ejecutable, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/preference_pairs.jsonl` y `data/preference_pairs_bad.jsonl`, contrastas la decisión contra `contracts/preference_dataset_contract.json` y ejecutas `ops/audit_preference_dataset.py` para generar `output/preference_dataset_decision.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/preference_dataset_decision.md` como línea base.
- Cambia o añade un caso en `data/preference_pairs.jsonl` y `data/preference_pairs_bad.jsonl` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/preference_dataset_contract.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara el caso que pasa con el caso roto o arriesgado y escribe qué señal lo bloquea.
- Compara antes/después en `output/preference_dataset_decision.md` y `output/reward_card.md` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/audit_preference_dataset.py`, abre `output/preference_dataset_decision.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/preference_pairs.jsonl`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `Kit F10 C05: preferencias y post-training`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/preference_pairs.jsonl`, `data/preference_pairs_bad.jsonl`, `data/preference_pairs_eval.jsonl`, `data/preference_pairs_train.jsonl`.
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/preference_dataset_contract.json`.
- `configs/`: configuración ejecutable del ejercicio. Ejemplos dentro del ZIP: `configs/dpo_minimal_config.yaml`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `guides/`: guías de lectura o explotación del resultado. Ejemplos dentro del ZIP: `guides/annotation_guide.md`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/audit_preference_dataset.py`.
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_lab_contract.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/preference_dataset_decision.md`, `output/reward_card.md`, `output/preference_dataset_report.json`, `output/pair_scorecard.csv`.
- `output_bad/`: salidas de fallo para aprender qué debe bloquearse. Ejemplos dentro del ZIP: `output_bad/preference_dataset_decision.md`, `output_bad/reward_card.md`, `output_bad/preference_dataset_report.json`, `output_bad/pair_scorecard.csv`.

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/preference_dataset_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/reward_card.md`: lectura humana de la decisión, informe o runbook.
- `output_bad/preference_dataset_decision.md`: lectura humana de la decisión, informe o runbook.
- `output_bad/reward_card.md`: lectura humana de la decisión, informe o runbook.
- `output/preference_dataset_report.json`: evidencia estructurada para validar o automatizar.
- `output_bad/preference_dataset_report.json`: evidencia estructurada para validar o automatizar.
- `output/pair_scorecard.csv`: tabla que puedes inspeccionar o cargar en un notebook.
- `output_bad/pair_scorecard.csv`: tabla que puedes inspeccionar o cargar en un notebook.

### Qué entregar

Una entrega útil no es una captura de pantalla. Debe incluir los artefactos generados, la modificación razonada que hayas hecho y una decisión escrita que explique qué harías en un sistema real.

Como mínimo:

1. Resultado de `make test`.
2. Artefactos de `output/` que sostienen tu decisión.
3. Cambio propio en datos, contrato, política, plantilla o código, según el objetivo del kit.
4. Nota técnica breve: qué has probado, qué ha fallado o pasado, y qué decisión tomarías.

### Cómo adaptarlo a tu caso

1. Ejecuta primero `make run` sin tocar nada para obtener la línea base reproducible.
2. Ejecuta `make test` antes de cambiar el ejercicio; así sabes que el ZIP llegó completo.
3. Sustituye o amplía los archivos de `data/` con casos de tu dominio manteniendo el mismo contrato de campos.
4. Ajusta `contracts/` cuando cambien tipos, campos obligatorios, umbrales o catálogos permitidos.
5. Usa `templates/` como base documental; no entregues una plantilla sin completar.
6. Guarda los outputs finales y una nota breve con la decisión técnica que tomarías en un proyecto real.

### Criterio de validación

El kit está completo cuando se puede descargar, extraer, ejecutar con `make run`, validar con `make test` y explicar sin depender de ninguna carpeta externa. Si una práctica menciona código, datos, contrato, CSV, SQL, política o plantilla, ese contenido debe venir dentro del ZIP.
<!-- zip-quality-audit:end -->
