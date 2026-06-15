# Kit F3 C07: presupuesto de inferencia y serving

Este kit acompaña el capítulo 07 del facsímil 3. Calcula memoria de pesos, KV cache y latencia aproximada con varios usuarios.

## Ejecutar

```bash
python3 ops/estimate_serving_budget.py --write
cat output/serving_budget_decision.md
```

Como gate:

```bash
python3 ops/estimate_serving_budget.py --write --fail-on-invalid
```

## Archivos

| Archivo | Papel |
|---|---|
| `data/serving_scenario.json` | Parámetros, bits, capas, batch, contexto, heads y throughput. |
| `contracts/serving_policy.json` | Umbrales de memoria y degradación de latencia. |
| `ops/estimate_serving_budget.py` | Calculadora de pesos, KV cache y latencia. |
| `output/serving_budget_report.json` | Resultados estructurados. |
| `output/serving_budget_decision.md` | Informe legible. |

## Qué deberías mirar

1. `weights_memory_gb`: memoria de pesos según precisión.
2. `kv_cache_gb`: memoria que crece con contexto, capas, batch y cabezas KV.
3. `total_memory_gb`: suma mínima antes de contar margen real de runtime.
4. `decode_seconds_per_user`: por qué generar tokens es secuencial y afecta la experiencia.
5. `serving_recommendation`: si conviene reducir contexto, batch, salida, modelo o cambiar arquitectura de atención.

## Cómo lo adaptas a tu caso

Cambia batch, contexto, número de capas y heads en `data/serving_scenario.json`. El alumno debe defender una decisión concreta: qué serviría, con qué límite de concurrencia, qué degradaría y qué mediría antes de prometer latencia.

## Qué entregaría un alumno

El Markdown generado, una variante de batch/contexto y una decisión sobre MHA/GQA/MQA, cuantización y concurrencia.

## Qué te llevas

Te llevas una práctica ejecutable sobre presupuesto de inferencia y serving, con datos editables, contratos y umbrales, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/serving_scenario.json`, contrastas la decisión contra `contracts/serving_policy.json` y ejecutas `ops/estimate_serving_budget.py` para generar `output/serving_budget_decision.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/serving_budget_decision.md` como línea base.
- Cambia o añade un caso en `data/serving_scenario.json` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/serving_policy.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara antes/después en `output/serving_budget_decision.md` y `output/serving_budget_report.json` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/estimate_serving_budget.py`, abre `output/serving_budget_decision.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/serving_scenario.json`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `Kit F3 C07: presupuesto de inferencia y serving`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/serving_scenario.json`.
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/serving_policy.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/estimate_serving_budget.py`.
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_lab_contract.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/serving_budget_decision.md`, `output/serving_budget_report.json`.

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/serving_budget_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/serving_budget_report.json`: evidencia estructurada para validar o automatizar.

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
