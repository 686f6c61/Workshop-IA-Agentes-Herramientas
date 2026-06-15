# Kit F3 C05: sondas de arquitecturas modernas

Este kit acompaña el capítulo 05 del facsímil 3. Simula tres piezas: routing MoE, self-consistency y alineación imagen-texto con coseno.

## Ejecutar

```bash
python3 ops/probe_modern_architectures.py --write
cat output/modern_architecture_decision.md
```

Como gate:

```bash
python3 ops/probe_modern_architectures.py --write --fail-on-invalid
```

## Archivos

| Archivo | Papel |
|---|---|
| `data/modern_architecture_case.json` | Scores de expertos, respuestas y vectores multimodales. |
| `contracts/modern_architecture_policy.json` | Top-k, umbrales y experto esperado. |
| `ops/probe_modern_architectures.py` | Routing, self-consistency y similitud coseno. |
| `output/modern_architecture_report.json` | Resultados estructurados. |
| `output/modern_architecture_decision.md` | Informe legible. |

## Qué deberías mirar

1. `moe_routing`: qué expertos se activan y qué queda fuera.
2. `self_consistency`: si varias respuestas convergen o si la mayoría es frágil.
3. `multimodal_alignment`: si texto e imagen caen cerca en el espacio vectorial de juguete.
4. `review_flags`: cuándo una señal moderna no basta y pide revisión humana.
5. Qué parte del resultado es mecanismo estable y qué parte es maqueta pedagógica.

## Cómo lo adaptas a tu caso

Añade un caso de routing donde el experto ganador no sea el de siempre. Después cambia las respuestas de self-consistency para provocar empate o baja confianza. La práctica debe enseñar que las arquitecturas modernas no eliminan evaluación: añaden señales nuevas que también hay que auditar.

## Qué entregaría un alumno

El Markdown generado, un ticket nuevo con routing distinto y una decisión sobre qué señal usaría para activar revisión humana.

## Qué te llevas

Te llevas una práctica ejecutable sobre sondas de arquitecturas modernas, con datos editables, contratos y umbrales, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/modern_architecture_case.json`, contrastas la decisión contra `contracts/modern_architecture_policy.json` y ejecutas `ops/probe_modern_architectures.py` para generar `output/modern_architecture_decision.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/modern_architecture_decision.md` como línea base.
- Cambia o añade un caso en `data/modern_architecture_case.json` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/modern_architecture_policy.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara antes/después en `output/modern_architecture_decision.md` y `output/modern_architecture_report.json` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/probe_modern_architectures.py`, abre `output/modern_architecture_decision.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/modern_architecture_case.json`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `Kit F3 C05: sondas de arquitecturas modernas`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/modern_architecture_case.json`.
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/modern_architecture_policy.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/probe_modern_architectures.py`.
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_lab_contract.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/modern_architecture_decision.md`, `output/modern_architecture_report.json`.

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/modern_architecture_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/modern_architecture_report.json`: evidencia estructurada para validar o automatizar.

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
