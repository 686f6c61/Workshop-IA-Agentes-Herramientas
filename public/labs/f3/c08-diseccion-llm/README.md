# Kit F3 C08: diseccion de una llamada a un LLM

Este kit acompaña la sección “Diseccionando un LLM” del capítulo 08 del facsímil 3. No intenta construir un modelo real. Sirve para entrenar una mirada de ingeniería: seguir una petición desde texto, tokens y embeddings hasta logits, sampling, KV cache y decisión de runtime.

El caso reproduce una tarea frecuente: una aplicación de soporte interno pide una salida JSON verificable a partir de instrucciones, documentos y contrato de respuesta. El script usa números pequeños y deterministas para que puedas tocar parámetros sin depender de claves de API.

## Ejecutar

```bash
make run
cat output/dissection_report.md
```

Como gate:

```bash
make test
```

## Archivos

| Archivo | Papel |
|---|---|
| `data/request_case.json` | Prompt, documentos, contrato JSON, parámetros de generación y forma del modelo. |
| `data/toy_vocab.json` | Logits candidatos para simular el primer token de salida. |
| `contracts/dissection_policy.json` | Umbrales de tokens, entropía, TTFT, KV cache y token esperado. |
| `ops/dissect_llm_request.py` | Simulador de tokenización, embeddings, softmax, top-k, top-p, min-p y runtime. |
| `output/dissection_report.json` | Evidencia estructurada. |
| `output/dissection_report.md` | Informe humano de la disección. |

## Qué deberías mirar

1. `prompt_token_count`: cuánto cuesta el caso antes de generar nada.
2. `tensor_shapes`: qué forma tendrían tokens, embeddings, Q, K/V cache y logits.
3. `sampling.final_probabilities`: cómo quedan los candidatos tras temperatura, top-k, top-p y min-p.
4. `runtime.kv_cache_gb`: memoria temporal provocada por contexto, batch y cabezas KV.
5. `architecture_signals`: RoPE, RMSNorm, SwiGLU, GQA, riesgo de posición intermedia y speculative decoding.
6. `engineering_decision`: qué medirías antes de mover esto a producción.

## Cómo lo adaptas a tu caso

Cambia `data/request_case.json` con una tarea tuya: tickets, políticas internas, análisis de logs, clasificación de leads o resumen de incidencias. Después prueba tres cambios:

- sube `temperature` y observa si aumenta la entropía;
- sube `num_ctx` o `batch_size` y mira la KV cache;
- cambia `kv_heads` y compáralo con `attention_heads` para ver por qué GQA ahorra KV cache;
- cambia `generation.speculative_decoding.expected_acceptance_rate` y observa cuándo la estimación deja de compensar;
- reduce `max_output_tokens` y observa el tiempo de decode.

La práctica es buena cuando puedes explicar qué parámetro tocaste, qué métrica cambió y qué decisión tomarías.

## Qué entregaría un alumno

El Markdown generado, una variante propia del caso y una explicación breve: qué cambió, qué se midió y qué capa del sistema tocaría antes de publicar.

## Qué te llevas

Te llevas una práctica ejecutable sobre diseccion de una llamada a un LLM, con datos editables, contratos y umbrales, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/request_case.json` y `data/toy_vocab.json`, contrastas la decisión contra `contracts/dissection_policy.json` y ejecutas `ops/dissect_llm_request.py` para generar `output/dissection_report.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/dissection_report.md` como línea base.
- Cambia o añade un caso en `data/request_case.json` y `data/toy_vocab.json` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/dissection_policy.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara antes/después en `output/dissection_report.md` y `output/dissection_report.json` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/dissect_llm_request.py`, abre `output/dissection_report.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/request_case.json`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `Kit F3 C08: diseccion de una llamada a un LLM`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/request_case.json`, `data/toy_vocab.json`.
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/dissection_policy.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/dissect_llm_request.py`.
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_lab_contract.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/dissection_report.md`, `output/dissection_report.json`.

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/dissection_report.md`: lectura humana de la decisión, informe o runbook.
- `output/dissection_report.json`: evidencia estructurada para validar o automatizar.

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
