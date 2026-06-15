# Kit F7: prácticas de evaluación por capítulo

Este kit materializa las prácticas de los capítulos 01 a 04 del facsímil 7. Los capítulos 05 y 06 tienen kits propios porque requieren artefactos más grandes:

- `labs/f7/c05-calibracion/`
- `labs/f7/c06-interpretabilidad-laboratorio/`
- `labs/f7/laboratorio-cierre/`

## Ejecutar todo

```bash
python3 ops/run_f7_practices.py --all --write --fail-on-invalid
```

## Ejecutar un capítulo

```bash
python3 ops/run_f7_practices.py --chapter c03 --write --fail-on-invalid
```

Cada práctica produce un JSON y una decisión Markdown en `output/`.

## Qué cubre cada capítulo

| Capítulo | Artefacto generado | Qué debe aprender el alumno |
|---|---|---|
| C01 | `output/eval_scorecard.json` y `output/decision.md` | Una eval no es una nota general: permite tomar una decisión de release, revisión o bloqueo. |
| C02 | `output/threshold_scorecard.json` y `output/threshold_decision.md` | La matriz de confusión se convierte en coste de error, umbral y decisión por política. |
| C03 | `output/rag_scorecard.json` y `output/rag_decision.md` | RAG se evalúa separando retrieval, citas, groundedness y abstención. |
| C04 | `output/evaluator_audit_report.json` y `output/evaluator_audit_decision.md` | Un evaluador LLM también se audita: rúbrica, acuerdo, coste, sesgos y trazas. |

## Qué deberías mirar

1. El JSON de cada capítulo: ahí están los checks que sostienen la decisión.
2. El Markdown de decisión: debe poder leerse en una revisión técnica sin abrir el código.
3. Los ficheros de `evals/`: casos, rúbricas, hipótesis y guías de etiquetado.
4. Las políticas de `ops/ai/`: umbrales, taxonomía de error y manifest de ejecución.
5. Qué parte pasaría a un gate de CI y qué parte exige revisión humana.

## Qué entregaría un alumno

Para cada capítulo trabajado:

1. `output/cXX_decision.md` explicado con sus palabras.
2. `output/cXX_report.json` o scorecard equivalente.
3. Un caso nuevo o una modificación de rúbrica/política.
4. Una decisión: publicar, revisar, bloquear o pedir más datos.
5. Una frase sobre qué error del sistema detecta esta eval y qué error todavía no detecta.

## Qué te llevas

Te llevas una práctica ejecutable sobre prácticas de evaluación por capítulo, con sets de evaluación y rúbricas, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `evals/classification_cases.jsonl` y `evals/eval_cases.jsonl`, contrastas la decisión contra `ops/ai/error_taxonomy.json` y `ops/ai/eval_policy.json` y ejecutas `ops/ai/eval_runner.py` para generar `output/c01_decision.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/c01_decision.md` como línea base.
- Cambia o añade un caso en `evals/classification_cases.jsonl` y `evals/eval_cases.jsonl` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `ops/ai/error_taxonomy.json` y `ops/ai/eval_policy.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara antes/después en `output/c01_decision.md` y `output/c02_decision.md` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/ai/eval_runner.py`, abre `output/c01_decision.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `evals/classification_cases.jsonl`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `Kit F7: prácticas de evaluación por capítulo`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `evals/`: datasets, rúbricas o configuraciones de evaluación. Ejemplos dentro del ZIP: `evals/labeling_guide.md`, `evals/eval_hypothesis.json`, `evals/evaluator_calibration_cases.json`, `evals/evaluator_outputs.json`, ....
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/ai/error_taxonomy.json`, `ops/ai/eval_policy.json`, `ops/ai/eval_run_manifest.json`, `ops/ai/rag_eval_policy.json`, ....
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_lab_contract.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/c01_decision.md`, `output/c02_decision.md`, `output/c03_decision.md`, `output/c04_decision.md`, ....

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/c01_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/c02_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/c03_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/c04_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/decision.md`: lectura humana de la decisión, informe o runbook.
- `output/evaluator_audit_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/rag_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/threshold_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/all_summary.json`: evidencia estructurada para validar o automatizar.
- `output/c01_report.json`: evidencia estructurada para validar o automatizar.
- `output/c02_report.json`: evidencia estructurada para validar o automatizar.
- `output/c03_report.json`: evidencia estructurada para validar o automatizar.

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
3. Usa `templates/` como base documental; no entregues una plantilla sin completar.
4. Guarda los outputs finales y una nota breve con la decisión técnica que tomarías en un proyecto real.

### Criterio de validación

El kit está completo cuando se puede descargar, extraer, ejecutar con `make run`, validar con `make test` y explicar sin depender de ninguna carpeta externa. Si una práctica menciona código, datos, contrato, CSV, SQL, política o plantilla, ese contenido debe venir dentro del ZIP.
<!-- zip-quality-audit:end -->
