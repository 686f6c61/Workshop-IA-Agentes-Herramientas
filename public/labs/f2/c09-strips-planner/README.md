# Kit F2 C09: planificador STRIPS mínimo

Este kit acompaña el capítulo 09 del facsímil 2. Convierte dominio, problema, precondiciones y efectos en un plan ejecutable con búsqueda en anchura.

El objetivo es que el alumno vea la diferencia entre una lista de pasos y un plan verificable: cada acción debe tener precondiciones satisfechas, efectos positivos, efectos negativos y un estado final que cumpla el objetivo.

## Ejecutar

Desde esta carpeta:

```bash
python3 ops/solve_strips_plan.py --write
cat output/strips_plan_decision.md
```

Como gate:

```bash
python3 ops/solve_strips_plan.py --write --fail-on-invalid
```

## Archivos

| Archivo | Papel |
|---|---|
| `data/planning_problem.json` | Estado inicial, objetivo, acciones STRIPS y planes candidatos. |
| `contracts/planning_policy.json` | Longitud máxima, hechos obligatorios y checks mínimos. |
| `ops/solve_strips_plan.py` | Planificador BFS, validador de planes y generador de informe. |
| `output/strips_plan_report.json` | Plan encontrado, estados intermedios, candidatos válidos e inválidos. |
| `output/strips_plan_decision.md` | Lectura técnica del plan y de los fallos. |

## Qué deberías mirar

1. Por qué `enviar_factura` no puede ejecutarse antes de `validar_factura`.
2. Qué hecho desaparece cuando una acción tiene efecto negativo.
3. Qué diferencia hay entre encontrar un plan y validar un plan escrito a mano.
4. Por qué el estado final importa más que la lista textual de pasos.
5. Cómo añadir una aprobación humana como precondición dura.

## Qué entregaría un alumno

1. El Markdown generado.
2. Una acción nueva añadida al JSON.
3. Un plan candidato inválido y la explicación de por qué falla.
4. Una decisión: qué precondición falta para que el plan sea seguro en un proceso real.

## Qué te llevas

Te llevas una práctica ejecutable sobre planificador STRIPS mínimo, con datos editables, contratos y umbrales, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/planning_problem.json`, contrastas la decisión contra `contracts/planning_policy.json` y ejecutas `ops/solve_strips_plan.py` para generar `output/strips_plan_decision.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/strips_plan_decision.md` como línea base.
- Cambia o añade un caso en `data/planning_problem.json` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/planning_policy.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara antes/después en `output/strips_plan_decision.md` y `output/strips_plan_report.json` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/solve_strips_plan.py`, abre `output/strips_plan_decision.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/planning_problem.json`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `Kit F2 C09: planificador STRIPS mínimo`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/planning_problem.json`.
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/planning_policy.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/solve_strips_plan.py`.
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_lab_contract.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/strips_plan_decision.md`, `output/strips_plan_report.json`.

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/strips_plan_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/strips_plan_report.json`: evidencia estructurada para validar o automatizar.

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
