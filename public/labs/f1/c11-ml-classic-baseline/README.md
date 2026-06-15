# Kit F1 C11: baseline clásico antes de usar un LLM

Este kit acompaña el capítulo 11 del facsímil 1. Construye un clasificador tabular mínimo sin dependencias externas y lo compara con una mayoría trivial.

El objetivo es que el alumno practique lo que casi siempre se olvida: separar datos, crear una baseline, calcular matriz de confusión, mirar precision/recall/F1 y decidir si el modelo aporta algo antes de complicar la arquitectura.

## Ejecutar

Desde esta carpeta:

```bash
python3 ops/run_ml_classic_baseline.py --write
cat output/ml_classic_decision.md
```

Como gate:

```bash
python3 ops/run_ml_classic_baseline.py --write --fail-on-invalid
```

## Archivos

| Archivo | Papel |
|---|---|
| `data/support_tickets.csv` | Dataset tabular pequeño de tickets con etiqueta de prioridad. |
| `contracts/ml_classic_policy.json` | Umbrales mínimos de recall, F1 y mejora frente a baseline. |
| `ops/run_ml_classic_baseline.py` | Entrena una regresión logística desde cero y calcula métricas. |
| `output/ml_classic_report.json` | Métricas, matriz de confusión y predicciones. |
| `output/ml_classic_decision.md` | Decisión legible: seguir, recoger datos o cambiar enfoque. |

## Qué deberías mirar

1. Qué hace una baseline de mayoría y por qué puede engañar.
2. Cómo cambia la decisión al mirar falsos negativos.
3. Por qué normalizar features ayuda a un modelo lineal.
4. Qué significa que un modelo sea simple pero útil.
5. Qué pedirías antes de llevar esto a producción: más datos, validación temporal, explicación y monitorización.

## Qué entregaría un alumno

1. El Markdown generado.
2. Cinco tickets propios añadidos al CSV.
3. Una matriz de confusión explicada en lenguaje de negocio.
4. Una decisión: usar baseline, probar otro modelo, recoger más datos o no automatizar.

## Qué te llevas

Te llevas una práctica ejecutable sobre baseline clásico antes de usar un LLM, con datos editables, contratos y umbrales, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/support_tickets.csv`, contrastas la decisión contra `contracts/ml_classic_policy.json` y ejecutas `ops/run_ml_classic_baseline.py` para generar `output/ml_classic_decision.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/ml_classic_decision.md` como línea base.
- Cambia o añade un caso en `data/support_tickets.csv` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/ml_classic_policy.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara antes/después en `output/ml_classic_decision.md` y `output/ml_classic_report.json` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/run_ml_classic_baseline.py`, abre `output/ml_classic_decision.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/support_tickets.csv`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `Kit F1 C11: baseline clásico antes de usar un LLM`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/support_tickets.csv`.
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/ml_classic_policy.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/run_ml_classic_baseline.py`.
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_ml_classic_baseline.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/ml_classic_decision.md`, `output/ml_classic_report.json`.

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/ml_classic_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/ml_classic_report.json`: evidencia estructurada para validar o automatizar.

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
