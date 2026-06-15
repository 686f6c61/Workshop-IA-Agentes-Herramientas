# Kit F1 C05: presupuesto y contrato de una red neuronal

Este kit acompaña el capítulo 05 del facsímil 1. Sirve para auditar arquitecturas MLP antes de entrenarlas: formas de capas, número de parámetros, memoria aproximada y riesgo básico por relación entre ejemplos y parámetros.

La práctica no busca ganar un benchmark. Busca que puedas defender una arquitectura con números antes de gastar tiempo, GPU o paciencia.

## Ejecutar

Desde esta carpeta:

```bash
python3 ops/audit_architectures.py --write
cat output/architecture_decision.md
```

Como comprobación estricta:

```bash
python3 ops/audit_architectures.py --write --fail-on-invalid
```

## Archivos

| Archivo | Papel |
|---|---|
| `data/architecture_candidates.json` | Candidatos de arquitectura con entrada, salida, tarea, capas ocultas y datos disponibles. |
| `contracts/architecture_policy.json` | Umbrales de revisión: relación mínima ejemplos/parámetro, balance de clases y tamaños permitidos. |
| `ops/audit_architectures.py` | Auditor ejecutable sin dependencias externas. |
| `output/architecture_report.json` | Resultado estructurado para automatizar revisiones. |
| `output/architecture_decision.md` | Informe legible para clase, revisión técnica o entrega. |

## Qué deberías mirar

1. `layer_shapes`: confirma que cada matriz `W` encaja con la capa anterior.
2. `total_parameters`: estima capacidad y coste.
3. `memory_estimate`: compara FP32, BF16 e INT8 sin confundirlo con memoria total de entrenamiento.
4. `examples_per_parameter`: indica si hay datos suficientes para defender esa capacidad.
5. `output_contract`: comprueba que la activación de salida coincide con la tarea.

## Qué entregaría un alumno

1. El Markdown generado.
2. Una arquitectura nueva para un caso real de su contexto.
3. Una justificación de entrada, salida y activación final.
4. Una decisión técnica: entrenar, simplificar, recoger más datos o cambiar de familia de modelo.
5. Una limitación honesta: qué no mide este auditor todavía.

## Qué te llevas

Te llevas una práctica ejecutable sobre presupuesto y contrato de una red neuronal, con datos editables, contratos y umbrales, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/architecture_candidates.json`, contrastas la decisión contra `contracts/architecture_policy.json` y ejecutas `ops/audit_architectures.py` para generar `output/architecture_decision.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/architecture_decision.md` como línea base.
- Cambia o añade un caso en `data/architecture_candidates.json` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/architecture_policy.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara antes/después en `output/architecture_decision.md` y `output/architecture_report.json` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/audit_architectures.py`, abre `output/architecture_decision.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/architecture_candidates.json`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `Kit F1 C05: presupuesto y contrato de una red neuronal`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/architecture_candidates.json`.
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/architecture_policy.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/audit_architectures.py`.
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_architecture_budget.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/architecture_decision.md`, `output/architecture_report.json`.

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/architecture_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/architecture_report.json`: evidencia estructurada para validar o automatizar.

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
