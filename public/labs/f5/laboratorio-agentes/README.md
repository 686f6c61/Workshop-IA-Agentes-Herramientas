# Kit F5: laboratorio de agentes

Este kit acompaña el laboratorio del facsímil 5. Convierte runtime, estado, idempotencia, aprobación, tools, trazas y evaluación de trayectorias en artefactos ejecutables.

## Reto 1: runtime mínimo

### Contexto

Vas a simular un agente que no solo responde texto: puede producir efectos, registrar trazas y quedarse esperando aprobación. El objetivo es aprender una regla profesional: si hay efectos, debe haber idempotencia, permisos y un libro de evidencias.

```bash
python3 ops/run_agent_runtime.py --write
python3 -m json.tool output/effect_ledger.json
cat output/runtime_decision.md
```

La salida debe mostrar:

- una run completada con efecto persistente,
- una petición duplicada que no repite efecto,
- una run esperando aprobación,
- una consulta de lectura,
- trazas reconstruibles.

Una solución buena explica:

- qué evento cambió estado;
- qué `idempotency_key` impidió duplicar un efecto;
- qué run quedó pendiente de aprobación;
- qué spans permiten reconstruir la ejecución;
- qué pasaría si la tool fallara a mitad.

## Reto 2: evaluación de trayectorias

### Contexto

Ahora no evaluamos una respuesta aislada. Evaluamos una trayectoria: ruta elegida, tools usadas, permisos, coste, latencia y trazas. Esto es lo que diferencia una demo de agentes de un sistema que se puede revisar.

```bash
python3 ops/evaluate_agent_routes.py --write
python3 -m json.tool output/ci_agent_gate.json
cat output/agent_eval_decision.md
```

Para probar un fallo:

```bash
python3 ops/evaluate_agent_routes.py \
  --runs data/agent_runs_regression.json \
  --output-dir output/regression \
  --write
python3 -m json.tool output/regression/ci_agent_gate.json
```

Una solución buena explica:

- por qué una trayectoria pasa;
- qué falla en la regresión;
- qué gate bloquearía una release;
- qué métrica no basta por sí sola;
- cómo añadirías un caso nuevo de evaluación.

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
agent-release/
  runtime_report.json
  runtime_trace.jsonl
  effect_ledger.json
  runtime_decision.md
  agent_eval_report.json
  ci_agent_gate.json
  agent_eval_decision.md
```

La entrega buena demuestra que el agente no es solo una cadena de prompts. Tiene estado, permisos, tools versionadas, trazas, coste, latencia y criterios de avance.

## Resultado esperado

| Pieza | Pregunta de defensa |
|---|---|
| `runtime_report.json` | ¿Qué runs terminaron, cuáles esperaron aprobación y cuáles no duplicaron efecto? |
| `runtime_trace.jsonl` | ¿Puedo reconstruir la ejecución paso a paso? |
| `effect_ledger.json` | ¿Hay efectos persistentes y claves de idempotencia? |
| `agent_eval_report.json` | ¿Las rutas, tools y permisos fueron correctos? |
| `ci_agent_gate.json` | ¿Publicaría o bloquearía esta versión? |
| `student_submission_report.md` | ¿La entrega contiene todo lo exigido? |

## Qué te llevas

Te llevas una práctica ejecutable sobre laboratorio de agentes, con datos editables, contratos y umbrales, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/agent_requests.jsonl` y `data/agent_eval_cases.json`, contrastas la decisión contra `contracts/agent_eval_contract.json` y `contracts/agent_runtime_policy.json` y ejecutas `ops/check_student_submission.py` para generar `output/agent_eval_decision.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/agent_eval_decision.md` como línea base.
- Cambia o añade un caso en `data/agent_requests.jsonl` y `data/agent_eval_cases.json` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/agent_eval_contract.json` y `contracts/agent_runtime_policy.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara antes/después en `output/agent_eval_decision.md` y `output/regression/agent_eval_decision.md` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/check_student_submission.py`, abre `output/agent_eval_decision.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/agent_requests.jsonl`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `Kit F5: laboratorio de agentes`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/agent_eval_cases.json`, `data/agent_runs_reference.json`, `data/agent_runs_regression.json`, `data/agent_requests.jsonl`.
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/agent_eval_contract.json`, `contracts/agent_runtime_policy.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/check_student_submission.py`, `ops/evaluate_agent_routes.py`, `ops/run_agent_runtime.py`.
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_lab_contract.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/agent_eval_decision.md`, `output/regression/agent_eval_decision.md`, `output/runtime_decision.md`, `output/student_submission_report.md`, ....
- `solutions/`: soluciones de referencia o carpeta para la entrega del alumno. Ejemplos dentro del ZIP: `solutions/mi-equipo/README.md`, `solutions/reference/agent_eval_decision.md`, `solutions/reference/runtime_decision.md`, `solutions/reference/agent_eval_report.json`, ....

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/agent_eval_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/regression/agent_eval_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/runtime_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/student_submission_report.md`: lectura humana de la decisión, informe o runbook.
- `solutions/reference/agent_eval_decision.md`: lectura humana de la decisión, informe o runbook.
- `solutions/reference/runtime_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/agent_eval_report.json`: evidencia estructurada para validar o automatizar.
- `output/ci_agent_gate.json`: evidencia estructurada para validar o automatizar.
- `output/effect_ledger.json`: evidencia estructurada para validar o automatizar.
- `output/regression/agent_eval_report.json`: evidencia estructurada para validar o automatizar.
- `output/regression/ci_agent_gate.json`: evidencia estructurada para validar o automatizar.
- `output/runtime_report.json`: evidencia estructurada para validar o automatizar.

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
