# Kit F8 C04: features, representaciones y embeddings

Este kit acompaña el capítulo 04 del facsímil 8. Construye un pipeline pequeño pero completo: parte de casos académicos, respeta un split ya congelado, ajusta transformaciones solo con train, genera una matriz de features y produce una búsqueda vectorial local.

La idea no es competir con un modelo de embeddings comercial. La idea es aprender el contrato de ingeniería que luego usaras con cualquier encoder real: dimensiones, versión, vocabulario, normalizacion, similitud, metadata y evaluación por split.

## Ejecutar

Desde está carpeta:

```bash
python3 ops/build_feature_vectors.py --write
cat output/feature_decision.md
python3 ops/search_feature_vectors.py --write
cat output/search_decision.md
```

## Archivos

| Archivo | Papel |
|---|---|
| `data/feature_cases.csv` | Casos de soporte académico con texto, producto, canal y etiqueta. |
| `data/split_assignments.csv` | Split congelado heredado del capítulo 03. |
| `data/search_queries.csv` | Consultas de ejemplo para probar recuperación vectorial. |
| `contracts/feature_contract.json` | Contrato de columnas, transformaciones, dimensiones y reglas de leakage. |
| `ops/build_feature_vectors.py` | Ajusta transformaciones solo con train y genera matrices. |
| `ops/search_feature_vectors.py` | Calcula similitud coseno entre consultas y casos indexables. |
| `output/feature_manifest.json` | Manifest de features: hashes, vocabulario, dimensiones y versión. |
| `output/feature_matrix.csv` | Matriz tabular + TF-IDF local por caso. |
| `output/dense_embedding_matrix.csv` | Embedding denso local de 16 dimensiones por caso. |
| `output/feature_quality_report.json` | Checks de fit scope, columnas prohibidas, dimensiones y desconocidos. |
| `output/search_results.csv` | Vecinos más cercanos por consulta. |
| `output/search_report.json` | Reporte de búsqueda: top-k, terminos fuera de vocabulario y cobertura. |
| `output/feature_decision.md` | Decisión técnica sobre la representación generada. |
| `output/search_decision.md` | Lectura operativa de los resultados de búsqueda. |

## Qué deberías mirar

1. `feature_manifest.json`: confirma que el vocabulario y las categorias se han ajustado con train.
2. `feature_matrix.csv`: muestra que cada fila acaba como numeros versionados.
3. `dense_embedding_matrix.csv`: ensena una representación densa local para probar dimensiones y similitud.
4. `feature_quality_report.json`: comprueba columnas prohibidas, desconocidos y dimensiones.
5. `search_results.csv`: permite ver por que una consulta recupera unos casos y no otros.
6. `search_report.json`: detecta terminos de consulta que no existen en el vocabulario de train.

## Qué entregaría un alumno

1. Manifest de features generado.
2. Matriz de features y embeddings densos.
3. Decisión técnica sobre si la representación es publicable.
4. Tres consultas propias en `search_queries.csv`.
5. Lectura de un fallo de recuperación y propuesta de mejora.
6. Una modificacion del contrato para su propio dataset.

## Qué te llevas

Te llevas una práctica ejecutable sobre features, representaciones y embeddings, con datos editables, contratos y umbrales, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/feature_cases.csv` y `data/search_queries.csv`, contrastas la decisión contra `contracts/feature_contract.json` y ejecutas `ops/build_feature_vectors.py` para generar `output/feature_decision.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/feature_decision.md` como línea base.
- Cambia o añade un caso en `data/feature_cases.csv` y `data/search_queries.csv` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/feature_contract.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara antes/después en `output/feature_decision.md` y `output/search_decision.md` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/build_feature_vectors.py`, abre `output/feature_decision.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/feature_cases.csv`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `Kit F8 C04: features, representaciones y embeddings`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/feature_cases.csv`, `data/search_queries.csv`, `data/split_assignments.csv`.
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/feature_contract.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/build_feature_vectors.py`, `ops/search_feature_vectors.py`.
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_lab_contract.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/feature_decision.md`, `output/search_decision.md`, `output/feature_manifest.json`, `output/feature_quality_report.json`, ....

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/feature_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/search_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/feature_manifest.json`: evidencia estructurada para validar o automatizar.
- `output/feature_quality_report.json`: evidencia estructurada para validar o automatizar.
- `output/search_report.json`: evidencia estructurada para validar o automatizar.
- `output/dense_embedding_matrix.csv`: tabla que puedes inspeccionar o cargar en un notebook.
- `output/feature_matrix.csv`: tabla que puedes inspeccionar o cargar en un notebook.
- `output/search_results.csv`: tabla que puedes inspeccionar o cargar en un notebook.

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
