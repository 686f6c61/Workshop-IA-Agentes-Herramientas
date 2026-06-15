# Kit F1 C09: inspeccionar tokens y embeddings sin API

Este kit acompaña el capítulo 09 del facsímil 1. Simula tokenización, IDs y embeddings con un programa local, sin depender de claves de API ni de modelos externos.

No pretende sustituir al tokenizador real de OpenAI, Anthropic, Google o cualquier proveedor. Sirve para que el alumno vea la mecánica: un texto se parte en tokens, esos tokens se convierten en IDs, los IDs alimentan vectores y esos vectores se comparan con similitud coseno.

## Ejecutar

Desde esta carpeta:

```bash
python3 ops/inspect_tokens_embeddings.py --write
cat output/token_embedding_decision.md
```

Como gate:

```bash
python3 ops/inspect_tokens_embeddings.py --write --fail-on-invalid
```

## Archivos

| Archivo | Papel |
|---|---|
| `data/text_cases.json` | Pares y grupos de texto para comparar tokenización y similitud. |
| `contracts/token_embedding_policy.json` | Dimensión del embedding de juguete, umbrales de similitud y coste de ejemplo. |
| `ops/inspect_tokens_embeddings.py` | Tokenizador simple, IDs deterministas, embedding hash y similitud coseno. |
| `output/token_embedding_report.json` | Tokens, IDs, vectores resumidos y similitudes. |
| `output/token_embedding_decision.md` | Informe legible con conclusiones y límites del experimento. |

## Qué deberías mirar

1. Qué palabra y token no son lo mismo.
2. Qué dos textos con significado cercano pueden tener tokens distintos.
3. Qué es un embedding: una lista de dimensiónes numéricas.
4. Qué la similitud coseno compara direcciones, no igualdad literal.
5. Qué para producción siempre se mide con el tokenizador y el embedding reales del modelo elegido.

## Qué entregaría un alumno

1. El Markdown generado.
2. Dos pares nuevos añadidos a `data/text_cases.json`.
3. Una explicación de un caso donde el parecido semántico no coincide con el parecido literal.
4. Una decisión: qué modelo/tokenizador real mediría antes de estimar coste, memoria o RAG.

## Qué te llevas

Te llevas una práctica ejecutable sobre inspeccionar tokens y embeddings sin API, con datos editables, contratos y umbrales, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/text_cases.json`, contrastas la decisión contra `contracts/token_embedding_policy.json` y ejecutas `ops/inspect_tokens_embeddings.py` para generar `output/token_embedding_decision.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/token_embedding_decision.md` como línea base.
- Cambia o añade un caso en `data/text_cases.json` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/token_embedding_policy.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara antes/después en `output/token_embedding_decision.md` y `output/token_embedding_report.json` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/inspect_tokens_embeddings.py`, abre `output/token_embedding_decision.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/text_cases.json`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `Kit F1 C09: inspeccionar tokens y embeddings sin API`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/text_cases.json`.
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/token_embedding_policy.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/inspect_tokens_embeddings.py`.
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_token_embedding_inspector.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/token_embedding_decision.md`, `output/token_embedding_report.json`.

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/token_embedding_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/token_embedding_report.json`: evidencia estructurada para validar o automatizar.

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
