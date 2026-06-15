# Kit F6: laboratorio de operación

Este kit acompaña el laboratorio del facsímil 6. Convierte readiness, continuidad, rollback, EvalOps, handoff y postmortem en artefactos ejecutables.

## Reto 1: readiness de un asistente RAG

### Contexto

Vas a evaluar si un asistente RAG está listo para operar. El manifiesto incompleto debe fallar: esa es la gracia. En operación, un gate que no bloquea cuando faltan owner, SLO, rollback o evidencias no es un gate; es decoración.

Ejecuta primero el manifiesto incompleto:

```bash
python3 ops/operational_readiness.py --write
```

Debe quedar `not_ready`. Después ejecuta el manifiesto completo:

```bash
python3 ops/operational_readiness.py \
  --manifest contracts/readiness_manifest_complete.json \
  --output output/complete/operational_readiness.json \
  --decision-output output/complete/readiness_decision.md \
  --write
```

Una solución buena explica:

- qué secciones bloquean el manifiesto incompleto;
- qué evidencias convierten el manifiesto completo en operable;
- qué SLI/SLO se está midiendo;
- qué harías si el gate queda en `not_ready` una hora antes de release.

## Reto 2: continuidad con tres degradaciones

### Contexto

Ahora simulas degradaciones: latencia, error, fallback o pérdida de calidad. El objetivo no es esconder el fallo, sino demostrar que el sistema conserva trazas, activa mitigaciones, genera postmortem y crea un caso de regresión.

Ejecuta el drill inicial:

```bash
python3 ops/run_continuity_drill.py --write
python3 -m json.tool output/ci_continuity_gate.json
cat output/continuity_decision.md
```

Luego ejecuta la variante recuperada:

```bash
python3 ops/run_continuity_drill.py \
  --events data/continuity_events_recovered.jsonl \
  --output-dir output/recovered \
  --write
python3 -m json.tool output/recovered/ci_continuity_gate.json
```

Una solución buena explica:

- qué degradación aparece y cómo se detecta;
- qué acción operativa se toma;
- qué breach queda registrado;
- qué caso entra en EvalOps;
- por qué la variante recuperada pasa el gate.

## Validar entrega

La solución de referencia se valida así:

```bash
python3 ops/check_student_submission.py --submission-dir solutions/reference --write
```

Para una entrega propia:

```bash
python3 ops/check_student_submission.py --submission-dir solutions/mi-equipo --write --fail-on-missing
```

## Entrega mínima esperada

```text
operacion-release/
  operational_readiness.json
  readiness_decision.md
  continuity_report.json
  ci_continuity_gate.json
  continuity_decision.md
  postmortem.md
  regression_case.json
```

La entrega buena no dice solo que algo falla. Dice qué falta, qué acción se ejecuta, qué evidencia se preserva y qué caso entra en EvalOps para que no se repita el mismo fallo.

## Resultado esperado

| Pieza | Pregunta de defensa |
|---|---|
| `operational_readiness.json` | ¿El sistema está listo o qué lo bloquea? |
| `readiness_decision.md` | ¿Qué acciones concretas debe ejecutar el equipo? |
| `continuity_report.json` | ¿Qué degradaciones se detectaron? |
| `ci_continuity_gate.json` | ¿El drill publica, degrada o bloquea? |
| `postmortem.md` | ¿Hay causa, impacto, mitigación y aprendizaje? |
| `regression_case.json` | ¿El incidente se convierte en prueba futura? |

## Qué te llevas

Te llevas una práctica ejecutable sobre laboratorio de operación, con datos editables, sets de evaluación y rúbricas, contratos y umbrales, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/continuity_events.jsonl` y `data/continuity_events_recovered.jsonl`, contrastas la decisión contra `contracts/readiness_manifest_complete.json` y `contracts/readiness_manifest_incomplete.json` y ejecutas `ops/ai/operational_readiness.py` para generar `output/complete/readiness_decision.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/complete/readiness_decision.md` como línea base.
- Cambia o añade un caso en `data/continuity_events.jsonl` y `data/continuity_events_recovered.jsonl` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/readiness_manifest_complete.json` y `contracts/readiness_manifest_incomplete.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara antes/después en `output/complete/readiness_decision.md` y `output/continuity_decision.md` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/ai/operational_readiness.py`, abre `output/complete/readiness_decision.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/continuity_events.jsonl`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `Kit F6: laboratorio de operación`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/continuity_events.jsonl`, `data/continuity_events_recovered.jsonl`.
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/readiness_manifest_complete.json`, `contracts/readiness_manifest_incomplete.json`, `contracts/readiness_policy.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `evals/`: datasets, rúbricas o configuraciones de evaluación. Ejemplos dentro del ZIP: `evals/regression_cases.jsonl`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/ai/continuity_drill.md`, `ops/ai/oncall_handoff.md`, `ops/ai/rollback_plan.md`, `ops/ai/runbook_ai_service.md`, ....
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_lab_contract.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/complete/readiness_decision.md`, `output/continuity_decision.md`, `output/postmortem.md`, `output/readiness_decision.md`, ....
- `solutions/`: soluciones de referencia o carpeta para la entrega del alumno. Ejemplos dentro del ZIP: `solutions/mi-equipo/README.md`, `solutions/reference/continuity_decision.md`, `solutions/reference/postmortem.md`, `solutions/reference/readiness_decision.md`, ....

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/complete/readiness_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/continuity_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/postmortem.md`: lectura humana de la decisión, informe o runbook.
- `output/readiness_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/recovered/continuity_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/recovered/postmortem.md`: lectura humana de la decisión, informe o runbook.
- `output/student_submission_report.md`: lectura humana de la decisión, informe o runbook.
- `solutions/reference/continuity_decision.md`: lectura humana de la decisión, informe o runbook.
- `solutions/reference/postmortem.md`: lectura humana de la decisión, informe o runbook.
- `solutions/reference/readiness_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/ci_continuity_gate.json`: evidencia estructurada para validar o automatizar.
- `output/complete/operational_readiness.json`: evidencia estructurada para validar o automatizar.

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
6. Coloca tu versión en `solutions/mi-equipo/` y compárala contra la referencia o contra los tests.
7. Guarda los outputs finales y una nota breve con la decisión técnica que tomarías en un proyecto real.

### Criterio de validación

El kit está completo cuando se puede descargar, extraer, ejecutar con `make run`, validar con `make test` y explicar sin depender de ninguna carpeta externa. Si una práctica menciona código, datos, contrato, CSV, SQL, política o plantilla, ese contenido debe venir dentro del ZIP.
<!-- zip-quality-audit:end -->
