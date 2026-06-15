# Kit F1 C07: pérdida, optimizador y validación

Este kit acompaña el capítulo 07 del facsímil 1. Entrena una regresión logística pequeña sin dependencias externas para comparar pérdidas, optimizadores, weight decay y brecha entre entrenamiento y validación.

La práctica no busca producir un modelo de producción. Busca que puedas leer una run: qué se optimizó, qué métrica mejoró y qué configuración merece seguir.

## Ejecutar

Desde esta carpeta:

```bash
python3 ops/run_training_grid.py --write
cat output/training_decision.md
```

Como gate:

```bash
python3 ops/run_training_grid.py --write --fail-on-invalid
```

## Archivos

| Archivo | Papel |
|---|---|
| `contracts/training_grid.json` | Configuración de dataset, épocas y runs a comparar. |
| `ops/run_training_grid.py` | Entrenador reproducible sin dependencias externas. |
| `output/training_report.json` | Métricas estructuradas por run. |
| `output/training_decision.md` | Informe legible con recomendación. |

## Qué deberías mirar

1. Pérdida de entrenamiento y validación.
2. Accuracy y F1 en validación.
3. Brecha entre train y validación.
4. Efecto de BCE frente a MSE en clasificación.
5. Efecto de SGD frente a AdamW y de weight decay.

## Qué entregaría un alumno

1. El Markdown generado.
2. Una run nueva en `contracts/training_grid.json`.
3. Una justificación de pérdida y métrica.
4. Una decisión: qué run repetiría, cuál descartaría y qué miraría después.

## Qué te llevas

Te llevas una práctica ejecutable sobre pérdida, optimizador y validación, con contratos y umbrales, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con entradas del propio ejercicio, contrastas la decisión contra `contracts/training_grid.json` y ejecutas `ops/run_training_grid.py` para generar `output/training_decision.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/training_decision.md` como línea base.
- Endurece una regla, umbral o campo obligatorio en `contracts/training_grid.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara antes/después en `output/training_decision.md` y `output/training_report.json` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/run_training_grid.py`, abre `output/training_decision.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `contracts/training_grid.json`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `Kit F1 C07: pérdida, optimizador y validación`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/training_grid.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/run_training_grid.py`.
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_training_grid.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/training_decision.md`, `output/training_report.json`.

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/training_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/training_report.json`: evidencia estructurada para validar o automatizar.

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
3. Ajusta `contracts/` cuando cambien tipos, campos obligatorios, umbrales o catálogos permitidos.
4. Usa `templates/` como base documental; no entregues una plantilla sin completar.
5. Guarda los outputs finales y una nota breve con la decisión técnica que tomarías en un proyecto real.

### Criterio de validación

El kit está completo cuando se puede descargar, extraer, ejecutar con `make run`, validar con `make test` y explicar sin depender de ninguna carpeta externa. Si una práctica menciona código, datos, contrato, CSV, SQL, política o plantilla, ese contenido debe venir dentro del ZIP.
<!-- zip-quality-audit:end -->
