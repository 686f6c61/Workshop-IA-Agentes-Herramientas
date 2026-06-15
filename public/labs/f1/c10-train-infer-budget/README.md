# Kit F1 C10: presupuesto de entrenamiento e inferencia

Este kit acompaña el capítulo 10 del facsímil 1. Calcula, de forma aproximada, memoria de pesos, memoria de KV cache, coste relativo de entrenamiento y viabilidad de inferencia local.

El objetivo es separar tres decisiones que suelen mezclarse: entrenar desde cero, ajustar un modelo existente y servir inferencia. Cada una exige hardware, presupuesto y riesgos distintos.

## Ejecutar

Desde esta carpeta:

```bash
python3 ops/plan_train_infer.py --write
cat output/train_infer_decision.md
```

Como gate:

```bash
python3 ops/plan_train_infer.py --write --fail-on-invalid
```

## Archivos

| Archivo | Papel |
|---|---|
| `data/model_scenarios.json` | Escenarios de inferencia local, API, LoRA y entrenamiento desde cero. |
| `contracts/deployment_policy.json` | Bytes por precisión, margen de VRAM, costes y límites de seguridad. |
| `ops/plan_train_infer.py` | Calcula memoria, KV cache, headroom y recomendación de despliegue. |
| `output/train_infer_report.json` | Resultados estructurados por escenario. |
| `output/train_infer_decision.md` | Informe legible para decidir qué camino seguir. |

## Qué deberías mirar

1. Por qué cuantizar reduce memoria de pesos, pero no elimina el coste de contexto.
2. Por qué entrenar con Adam necesita mucha más memoria que inferir.
3. Por qué una GPU que carga pesos puede quedarse corta al subir batch o contexto.
4. Cuándo conviene API, cuándo local y cuándo ni siquiera toca modelo.
5. Qué dato falta antes de decidir: dataset, latencia objetivo, privacidad, coste o evaluación.

## Qué entregaría un alumno

1. El Markdown generado.
2. Un escenario propio con GPU, contexto y tamaño de modelo.
3. Una tabla comparando FP16, INT8 e INT4.
4. Una decisión escrita: API, local, RAG, fine-tuning o no construir todavía.

## Qué te llevas

Te llevas una práctica ejecutable sobre presupuesto de entrenamiento e inferencia, con datos editables, contratos y umbrales, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/model_scenarios.json`, contrastas la decisión contra `contracts/deployment_policy.json` y ejecutas `ops/plan_train_infer.py` para generar `output/train_infer_decision.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/train_infer_decision.md` como línea base.
- Cambia o añade un caso en `data/model_scenarios.json` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/deployment_policy.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara antes/después en `output/train_infer_decision.md` y `output/train_infer_report.json` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/plan_train_infer.py`, abre `output/train_infer_decision.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/model_scenarios.json`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `Kit F1 C10: presupuesto de entrenamiento e inferencia`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/model_scenarios.json`.
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/deployment_policy.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/plan_train_infer.py`.
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_train_infer_budget.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/train_infer_decision.md`, `output/train_infer_report.json`.

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/train_infer_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/train_infer_report.json`: evidencia estructurada para validar o automatizar.

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
