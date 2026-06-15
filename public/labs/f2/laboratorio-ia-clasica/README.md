# F2 · Laboratorio de IA clásica

Este kit convierte el laboratorio del facsímil 2 en dos prácticas ejecutables: resolver un CSP pequeño y tomar una decisión con plan, reglas y grafo de conocimiento.

## Ejecutar

```bash
python3 ops/solve_csp_schedule.py --write
python3 ops/evaluate_symbolic_plan.py --write
```

Como gate:

```bash
python3 ops/solve_csp_schedule.py --write --fail-on-no-solution
python3 ops/evaluate_symbolic_plan.py --write --fail-on-review
```

Generar solución de referencia:

```bash
python3 ops/solve_csp_schedule.py --output-dir solutions/reference --write
python3 ops/evaluate_symbolic_plan.py --output-dir solutions/reference --write
python3 ops/check_student_submission.py --submission-dir solutions/reference --write --fail-on-missing
```

## Entradas

| Archivo | Uso |
|---|---|
| `contracts/ia_clasica_lab_contract.json` | Gates para CSP y plan simbólico. |
| `data/csp_schedule.json` | Sesiones, huecos, salas y restricciones del horario. |
| `data/support_graph.json` | Tripletas del ticket, persona, aprobacion, recurso y rol. |

## Salidas

| Archivo | Qué demuestra |
|---|---|
| `csp_solution.json` | Asignación válida y número de eventos de búsqueda. |
| `csp_decision.md` | Justificación legible de restricciones cumplidas. |
| `csp_trace.jsonl` | Selección de variables, pruebas de valores y poda. |
| `symbolic_plan_report.json` | Checks, acción y plan final. |
| `symbolic_plan_decision.md` | Decisión explicada con precondiciones. |
| `symbolic_plan_trace.jsonl` | Trazas de entidades, grafo, validación y registro. |

## Entrega esperada

La entrega debe demostrar que la solución no sale de una frase bonita: sale de variables, dominios, restricciones, hechos consultables y precondiciones verificadas.

## Reto 1: horario con restricciones

El primer reto parte de `data/csp_schedule.json`. El alumno debe resolver tres sesiones (`repaso`, `practica`, `tutoria`) colocando cada una en una hora y una sala. No basta con encontrar una combinación: debe justificar que cumple restricciones duras y explicar qué ha podado la búsqueda.

Pasos mínimos:

1. Ejecutar `python3 ops/solve_csp_schedule.py --write`.
2. Leer `output/csp_decision.md` y comprobar qué sesión queda en cada hueco.
3. Abrir `output/csp_trace.jsonl` y localizar al menos tres eventos: elección de variable, prueba de valor y poda.
4. Cambiar una restricción en `data/csp_schedule.json`, volver a ejecutar y explicar si el problema sigue teniendo solución.

Resultado esperado: una asignación válida, un informe Markdown y una traza que permita defender la solución ante otra persona.

## Reto 2: decisión simbólica con grafo

El segundo reto usa `data/support_graph.json`. El caso simula una decisión de acceso temporal: el sistema debe resolver entidades, consultar hechos, validar rol, validar aprobación y registrar la decisión. La gracia del reto es separar lo que podría redactar un LLM de lo que debe decidir una capa verificable.

Pasos mínimos:

1. Ejecutar `python3 ops/evaluate_symbolic_plan.py --write`.
2. Leer `output/symbolic_plan_decision.md` y comprobar qué precondiciones pasan.
3. Abrir `output/symbolic_plan_trace.jsonl` y seguir el plan paso a paso.
4. Modificar una tripleta de `data/support_graph.json`, por ejemplo quitando la aprobación del responsable, y comprobar que la decisión ya no debería conceder acceso.

Resultado esperado: una decisión trazable, un plan legible y una explicación de qué hecho del grafo sostiene cada paso.

## Cómo saber si está bien

El checker no evalúa opiniones: comprueba artefactos. Para pasar, la carpeta de entrega debe contener la solución CSP, la decisión CSP, la traza CSP, el informe simbólico, la decisión simbólica y la traza simbólica.

```bash
python3 ops/check_student_submission.py --submission-dir solutions/reference --write --fail-on-missing
```

Una entrega fuerte añade una variación propia: cambia una restricción, una tripleta o una precondición, vuelve a ejecutar y explica qué ha cambiado. Eso convierte el laboratorio en una práctica real de modelado, no en copiar una salida.

## Qué te llevas

Te llevas una práctica ejecutable sobre F2 · Laboratorio de IA clásica, con datos editables, contratos y umbrales, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/csp_schedule.json` y `data/support_graph.json`, contrastas la decisión contra `contracts/ia_clasica_lab_contract.json` y ejecutas `ops/check_student_submission.py` para generar `output/csp_decision.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/csp_decision.md` como línea base.
- Cambia o añade un caso en `data/csp_schedule.json` y `data/support_graph.json` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/ia_clasica_lab_contract.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara antes/después en `output/csp_decision.md` y `output/symbolic_plan_decision.md` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/check_student_submission.py`, abre `output/csp_decision.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/csp_schedule.json`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `F2 · Laboratorio de IA clásica`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/csp_schedule.json`, `data/support_graph.json`.
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/ia_clasica_lab_contract.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/check_student_submission.py`, `ops/evaluate_symbolic_plan.py`, `ops/solve_csp_schedule.py`.
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_lab_contract.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/csp_decision.md`, `output/symbolic_plan_decision.md`, `output/csp_solution.json`, `output/symbolic_plan_report.json`, ....
- `solutions/`: soluciones de referencia o carpeta para la entrega del alumno. Ejemplos dentro del ZIP: `solutions/reference/csp_decision.md`, `solutions/reference/symbolic_plan_decision.md`, `solutions/reference/csp_solution.json`, `solutions/reference/symbolic_plan_report.json`, ....

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/csp_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/symbolic_plan_decision.md`: lectura humana de la decisión, informe o runbook.
- `solutions/reference/csp_decision.md`: lectura humana de la decisión, informe o runbook.
- `solutions/reference/symbolic_plan_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/csp_solution.json`: evidencia estructurada para validar o automatizar.
- `output/symbolic_plan_report.json`: evidencia estructurada para validar o automatizar.
- `solutions/reference/csp_solution.json`: evidencia estructurada para validar o automatizar.
- `solutions/reference/symbolic_plan_report.json`: evidencia estructurada para validar o automatizar.
- `output/csp_trace.jsonl`: eventos o registros línea a línea.
- `output/symbolic_plan_trace.jsonl`: eventos o registros línea a línea.
- `solutions/reference/csp_trace.jsonl`: eventos o registros línea a línea.
- `solutions/reference/symbolic_plan_trace.jsonl`: eventos o registros línea a línea.

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
6. Usa `solutions/` como contraste de calidad, no como sustituto de tu razonamiento.
7. Guarda los outputs finales y una nota breve con la decisión técnica que tomarías en un proyecto real.

### Criterio de validación

El kit está completo cuando se puede descargar, extraer, ejecutar con `make run`, validar con `make test` y explicar sin depender de ninguna carpeta externa. Si una práctica menciona código, datos, contrato, CSV, SQL, política o plantilla, ese contenido debe venir dentro del ZIP.
<!-- zip-quality-audit:end -->
