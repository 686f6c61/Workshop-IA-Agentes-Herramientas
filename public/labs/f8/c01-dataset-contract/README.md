# Kit F8 C01: contrato de dataset y linaje

Este kit acompaña el capítulo 01 del facsímil 8. Construye una revisión reproducible de un dataset pequeño antes de usarlo en entrenamiento, evaluación o RAG.

El objetivo no es entrenar un modelo. El objetivo es que el alumno vea que un dataset de IA es un artefacto de ingeniería: tiene contrato, schema, splits, linaje, licencia, sensibilidad, checks y decision.

## Ejecutar

Desde está carpeta:

```bash
python3 ops/data/audit_dataset_contract.py --write
python3 ops/data/compare_drift.py --write
cat output/data_release_decision.md
cat output/drift_decision.md
```

## Archivos

| Archivo | Papel |
|---|---|
| `data/support_cases.csv` | Dataset tabular sintético de soporte académico. |
| `data/rag_documents.jsonl` | Documentos/chunks para pensar RAG y linaje documental. |
| `data/preference_pairs.jsonl` | Pares de preferencia para post-entrenamiento o evaluación comparativa. |
| `data/production_sample.csv` | Muestra de producción para comparar drift con el dataset base. |
| `contracts/data_contract.json` | Contrato de columnas, splits, licencias y criterios de release. |
| `contracts/odcs_like_contract.yaml` | Contrato estilo ODCS simplificado para leer estructura profesional. |
| `ops/data/audit_dataset_contract.py` | Script sin dependencias externas. |
| `ops/data/compare_drift.py` | Script de comparación de distribuciones sin dependencias externas. |
| `output/data_quality_report.json` | Checks, conteos, distribuciones y resultado del gate. |
| `output/lineage_manifest.json` | Hashes, owner, finalidad y resumen versionable. |
| `output/data_release_gate.json` | Gate separado para CI o revisión de release. |
| `output/leakage_report.json` | Resultado especifico de fuga textual entre splits. |
| `output/drift_report.json` | Comparación de distribuciones entre referencia y muestra actual. |
| `output/drift_decision.md` | Decisión resumida de drift. |
| `output/dataset_card.md` | Ficha breve del dataset. |
| `output/data_release_decision.md` | Decisión técnica para usar o revisar el dataset. |

## Qué deberías mirar

1. `checks`: que condiciones pasan o fallan.
2. `split_counts`: si hay suficientes filas por split.
3. `label_distribution`: si las clases existen en cantidad mínima.
4. `license_mismatches`: si alguna fila se usa fuera de su permiso.
5. `duplicate_text_across_splits`: si hay fuga entre train y test.
6. `lineage_manifest.json`: hashes para saber exactamente que se audito.
7. `drift_report.json`: que columnas cambiaron en una muestra nueva.
8. `rag_documents.jsonl`: que metadatos necesita un chunk recuperable.
9. `preference_pairs.jsonl`: como se estructura un par elegido/rechazado.

## Qué entregaría un alumno

1. Reporte JSON generado.
2. Manifest de linaje.
3. Dataset card.
4. Decisión Markdown.
5. Una propuesta de mejora del contrato para un caso propio.
6. Un diagnostico de drift y una decisión: usar, revisar o rehacer muestra.

## Qué te llevas

Te llevas una práctica ejecutable sobre contrato de dataset y linaje, con datos editables, contratos y umbrales, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/production_sample.csv` y `data/support_cases.csv`, contrastas la decisión contra `contracts/data_contract.json` y `contracts/odcs_like_contract.yaml` y ejecutas `ops/data/audit_dataset_contract.py` para generar `output/data_release_decision.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/data_release_decision.md` como línea base.
- Cambia o añade un caso en `data/production_sample.csv` y `data/support_cases.csv` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/data_contract.json` y `contracts/odcs_like_contract.yaml` y explica por qué el resultado debería cambiar o bloquearse.
- Compara antes/después en `output/data_release_decision.md` y `output/dataset_card.md` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/data/audit_dataset_contract.py`, abre `output/data_release_decision.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/production_sample.csv`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `Kit F8 C01: contrato de dataset y linaje`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/preference_pairs.jsonl`, `data/rag_documents.jsonl`, `data/production_sample.csv`, `data/support_cases.csv`.
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/data_contract.json`, `contracts/odcs_like_contract.yaml`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/data/audit_dataset_contract.py`, `ops/data/compare_drift.py`.
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_lab_contract.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/data_release_decision.md`, `output/dataset_card.md`, `output/drift_decision.md`, `output/data_quality_report.json`, ....

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/data_release_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/dataset_card.md`: lectura humana de la decisión, informe o runbook.
- `output/drift_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/data_quality_report.json`: evidencia estructurada para validar o automatizar.
- `output/data_release_gate.json`: evidencia estructurada para validar o automatizar.
- `output/drift_report.json`: evidencia estructurada para validar o automatizar.
- `output/leakage_report.json`: evidencia estructurada para validar o automatizar.
- `output/lineage_manifest.json`: evidencia estructurada para validar o automatizar.

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
