# Kit F4: laboratorio de tools, RAG y evals

Este kit acompaña el laboratorio del facsímil 4. Convierte el mini RAG y el router de herramientas en scripts ejecutables con trazas y gates.

## Reto 1: evaluar mini RAG

### Contexto

Tienes un corpus pequeño de documentos internos y varias preguntas. Algunas tienen evidencia suficiente; otras deben producir abstención. El objetivo no es que el modelo “responda bonito”, sino que el sistema recupere el documento correcto, cite evidencia y no conteste cuando falta soporte.

```bash
python3 ops/evaluate_mini_rag.py --write
python3 -m json.tool output/ci_rag_gate.json
cat output/rag_decision.md
```

El RAG debe recuperar documentos vigentes, abstenerse cuando no hay evidencia suficiente y dejar trazas por caso.

Una solución buena explica:

- qué documento recuperó cada caso;
- si la cita sostiene la respuesta;
- cuándo abstenerse mejora el sistema;
- qué métrica bloquearía una publicación;
- qué caso añadirías antes de llevarlo a producción.

## Reto 2: decidir ruta entre RAG, SQL, clasificador y código

### Contexto

No todo debe ir al mismo modelo ni a la misma herramienta. Una pregunta documental pide RAG; una consulta de datos vivos puede pedir SQL; una etiqueta simple puede pedir clasificador; un cálculo exacto puede pedir código. Este reto entrena el router mínimo: elegir ruta, ejecutar una comprobación y dejar traza.

```bash
python3 ops/evaluate_router.py --write
python3 -m json.tool output/ci_router_gate.json
cat output/router_decision.md
```

El router debe mandar preguntas documentales a RAG, datos vivos a SQL, etiquetas a clasificador y cálculos exactos a código.

Una solución buena explica:

- por qué cada caso fue a una herramienta concreta;
- qué validación evita usar la herramienta equivocada;
- qué campos mínimos debe tener una traza;
- qué errores deberían bloquear despliegue;
- cómo añadirías una herramienta nueva sin romper el contrato.

## Validar entrega

```bash
python3 ops/check_student_submission.py --submission-dir solutions/reference --write
```

Para una entrega propia:

```bash
python3 ops/check_student_submission.py --submission-dir solutions/mi-equipo --write --fail-on-missing
```

## Entrega esperada

```text
tools-evals-release/
  rag_eval_report.json
  ci_rag_gate.json
  rag_traces.jsonl
  rag_decision.md
  router_eval_report.json
  ci_router_gate.json
  router_traces.jsonl
  router_decision.md
```

## Resultado esperado

Una entrega completa no termina en `status=publicar`. Termina cuando puedes defender por qué publicarías o no publicarías:

| Pieza | Pregunta de defensa |
|---|---|
| `rag_eval_report.json` | ¿El retriever encuentra evidencia suficiente? |
| `rag_traces.jsonl` | ¿Puedo reconstruir cada decisión caso por caso? |
| `router_eval_report.json` | ¿El router elige la herramienta correcta? |
| `router_traces.jsonl` | ¿Hay input, ruta, salida y veredicto? |
| `student_submission_report.md` | ¿La entrega contiene todo lo exigido? |

## Qué te llevas

Te llevas una práctica ejecutable sobre laboratorio de tools, RAG y evals, con datos editables, contratos y umbrales, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/documents.jsonl` y `data/rag_cases.json`, contrastas la decisión contra `contracts/lab_eval_contract.json` y ejecutas `ops/check_student_submission.py` para generar `output/rag_decision.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/rag_decision.md` como línea base.
- Cambia o añade un caso en `data/documents.jsonl` y `data/rag_cases.json` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/lab_eval_contract.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara antes/después en `output/rag_decision.md` y `output/router_decision.md` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/check_student_submission.py`, abre `output/rag_decision.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/documents.jsonl`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `Kit F4: laboratorio de tools, RAG y evals`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/rag_cases.json`, `data/router_cases.json`, `data/documents.jsonl`.
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/lab_eval_contract.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/check_student_submission.py`, `ops/evaluate_mini_rag.py`, `ops/evaluate_router.py`.
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_lab_contract.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/rag_decision.md`, `output/router_decision.md`, `output/student_submission_report.md`, `output/ci_rag_gate.json`, ....
- `solutions/`: soluciones de referencia o carpeta para la entrega del alumno. Ejemplos dentro del ZIP: `solutions/mi-equipo/README.md`, `solutions/reference/rag_decision.md`, `solutions/reference/router_decision.md`, `solutions/reference/ci_rag_gate.json`, ....

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/rag_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/router_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/student_submission_report.md`: lectura humana de la decisión, informe o runbook.
- `solutions/reference/rag_decision.md`: lectura humana de la decisión, informe o runbook.
- `solutions/reference/router_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/ci_rag_gate.json`: evidencia estructurada para validar o automatizar.
- `output/ci_router_gate.json`: evidencia estructurada para validar o automatizar.
- `output/rag_eval_report.json`: evidencia estructurada para validar o automatizar.
- `output/router_eval_report.json`: evidencia estructurada para validar o automatizar.
- `solutions/reference/ci_rag_gate.json`: evidencia estructurada para validar o automatizar.
- `solutions/reference/ci_router_gate.json`: evidencia estructurada para validar o automatizar.
- `solutions/reference/rag_eval_report.json`: evidencia estructurada para validar o automatizar.

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
