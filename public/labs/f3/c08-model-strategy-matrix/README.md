# Kit F3 C08: matriz de estrategia de modelo

Este kit acompaña el capítulo 08 del facsímil 3. Convierte criterios del facsímil en una matriz ponderada para elegir estrategia de modelo.

## Ejecutar

```bash
python3 ops/score_model_strategy.py --write
cat output/model_strategy_decision.md
```

Como gate:

```bash
python3 ops/score_model_strategy.py --write --fail-on-invalid
```

## Archivos

| Archivo | Papel |
|---|---|
| `data/model_strategy_case.json` | Opciones, criterios y pesos. |
| `contracts/model_strategy_policy.json` | Mínimos de privacidad/contexto y opción esperada. |
| `ops/score_model_strategy.py` | Scoring ponderado y razones de decisión. |
| `output/model_strategy_report.json` | Puntuaciones estructuradas. |
| `output/model_strategy_decision.md` | Memo de decisión. |

## Qué deberías mirar

1. `hard_filters`: opciones descartadas antes de ponderar.
2. `criteria_weights`: qué pesa más en la decisión: privacidad, coste, calidad, latencia o mantenibilidad.
3. `option_scores`: puntuación total y explicación por criterio.
4. `sensitivity`: si un cambio razonable de pesos cambia la recomendación.
5. `decision_memo`: por qué la estrategia elegida encaja con el problema y qué riesgo queda abierto.

## Cómo lo adaptas a tu caso

Añade una opción realista a `data/model_strategy_case.json`: API externa, modelo local, RAG, fine-tuning o híbrido. Después cambia pesos en el contrato. La práctica es buena cuando el alumno puede explicar por qué no basta con “el modelo con más benchmark”.

## Qué entregaría un alumno

El Markdown generado, una opción nueva, pesos ajustados a su caso y una decisión defendible.

## Qué te llevas

Te llevas una práctica ejecutable sobre matriz de estrategia de modelo, con datos editables, contratos y umbrales, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/model_strategy_case.json`, contrastas la decisión contra `contracts/model_strategy_policy.json` y ejecutas `ops/score_model_strategy.py` para generar `output/model_strategy_decision.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/model_strategy_decision.md` como línea base.
- Cambia o añade un caso en `data/model_strategy_case.json` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/model_strategy_policy.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara antes/después en `output/model_strategy_decision.md` y `output/model_strategy_report.json` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/score_model_strategy.py`, abre `output/model_strategy_decision.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/model_strategy_case.json`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `Kit F3 C08: matriz de estrategia de modelo`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/model_strategy_case.json`.
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/model_strategy_policy.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/score_model_strategy.py`.
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_lab_contract.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/model_strategy_decision.md`, `output/model_strategy_report.json`.

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/model_strategy_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/model_strategy_report.json`: evidencia estructurada para validar o automatizar.

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
