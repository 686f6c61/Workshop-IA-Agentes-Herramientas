# Kit F1 C03: elegir el principio de IA adecuado

Este kit acompaña el capítulo 03 del facsímil 1. Convierte los cinco principios del capítulo en una decisión técnica: supervisado, no supervisado, post-training, atención/contexto o scaling/coste.

No entrena modelos. Construye una matriz defendible para decidir qué tipo de enfoque tiene sentido antes de pedir presupuesto, datos o GPUs.

## Ejecutar

Desde esta carpeta:

```bash
python3 ops/route_ai_principles.py --write
cat output/principle_decision.md
```

Como gate:

```bash
python3 ops/route_ai_principles.py --write --fail-on-review
```

## Archivos

| Archivo | Papel |
|---|---|
| `data/project_cases.json` | Casos realistas de producto, datos y arquitectura. |
| `contracts/principle_policy.json` | Política de decisión: umbrales, riesgos y entregables mínimos. |
| `ops/route_ai_principles.py` | Script sin dependencias externas. |
| `output/principle_report.json` | Matriz estructurada por caso. |
| `output/principle_decision.md` | Decisión legible para clase o revisión técnica. |

## Qué deberías mirar

1. `primary_principle`: principio dominante del caso.
2. `supporting_principles`: principios secundarios que no conviene olvidar.
3. `required_artifacts`: qué deberías producir antes de construir.
4. `review_flags`: riesgos que bloquean una decisión rápida.
5. `next_chapter`: dónde se profundiza en el facsímil.

## Qué entregaría un alumno

1. El Markdown generado.
2. Dos casos propios añadidos a `project_cases.json`.
3. Una justificación de por qué el principio dominante no basta por sí solo.
4. Un cambio de política en `principle_policy.json` y su efecto en la decisión.

## Qué te llevas

Te llevas una práctica ejecutable sobre elegir el principio de IA adecuado, con datos editables, contratos y umbrales, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/project_cases.json`, contrastas la decisión contra `contracts/principle_policy.json` y ejecutas `ops/route_ai_principles.py` para generar `output/principle_decision.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/principle_decision.md` como línea base.
- Cambia o añade un caso en `data/project_cases.json` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/principle_policy.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara antes/después en `output/principle_decision.md` y `output/principle_report.json` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/route_ai_principles.py`, abre `output/principle_decision.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/project_cases.json`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `Kit F1 C03: elegir el principio de IA adecuado`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/project_cases.json`.
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/principle_policy.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/route_ai_principles.py`.
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_principle_router.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/principle_decision.md`, `output/principle_report.json`.

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/principle_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/principle_report.json`: evidencia estructurada para validar o automatizar.

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
