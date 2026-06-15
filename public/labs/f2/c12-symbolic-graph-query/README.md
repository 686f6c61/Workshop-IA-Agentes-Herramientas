# Kit F2 C12: micrografo simbólico con inferencia

Este kit acompaña el capítulo 12 del facsímil 2. Construye un micrografo de tripletas, ejecuta consultas sencillas e infiere tipos por subclases.

No es una implementación completa de RDF, RDFS, OWL ni SPARQL. Es una maqueta reproducible para entender qué significa guardar conocimiento como hechos explícitos y consultar relaciones trazables.

## Ejecutar

Desde esta carpeta:

```bash
python3 ops/query_symbolic_graph.py --write
cat output/symbolic_graph_decision.md
```

Como gate:

```bash
python3 ops/query_symbolic_graph.py --write --fail-on-invalid
```

## Archivos

| Archivo | Papel |
|---|---|
| `data/triples.json` | Tripletas base de factura, cliente, plan y servicios. |
| `contracts/graph_policy.json` | Consultas esperadas e inferencias obligatorias. |
| `ops/query_symbolic_graph.py` | Motor mínimo de consulta e inferencia por subclase. |
| `output/symbolic_graph_report.json` | Tripletas base, inferidas y respuestas. |
| `output/symbolic_graph_decision.md` | Lectura técnica del micrografo. |

## Qué deberías mirar

1. Qué tripleta justifica que una factura pertenece a un cliente.
2. Qué regla permite inferir un tipo más general.
3. Qué se parece a una consulta SPARQL.
4. Qué no debería meterse en un vector store si necesitas verdad trazable.
5. Qué relación añadirías para permisos o aprobaciones.

## Qué entregaría un alumno

1. El Markdown generado.
2. Tres tripletas nuevas.
3. Una consulta nueva con su respuesta.
4. Una explicación de cuándo usaría grafo, vector store o ambos.

## Qué te llevas

Te llevas una práctica ejecutable sobre micrografo simbólico con inferencia, con datos editables, contratos y umbrales, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/triples.json`, contrastas la decisión contra `contracts/graph_policy.json` y ejecutas `ops/query_symbolic_graph.py` para generar `output/symbolic_graph_decision.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/symbolic_graph_decision.md` como línea base.
- Cambia o añade un caso en `data/triples.json` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/graph_policy.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara antes/después en `output/symbolic_graph_decision.md` y `output/symbolic_graph_report.json` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/query_symbolic_graph.py`, abre `output/symbolic_graph_decision.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/triples.json`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `Kit F2 C12: micrografo simbólico con inferencia`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/triples.json`.
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/graph_policy.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/query_symbolic_graph.py`.
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_lab_contract.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/symbolic_graph_decision.md`, `output/symbolic_graph_report.json`.

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/symbolic_graph_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/symbolic_graph_report.json`: evidencia estructurada para validar o automatizar.

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
