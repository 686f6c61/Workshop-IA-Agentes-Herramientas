# Kit F10 C02: eventos RL, trayectorias y replay buffer

Este kit acompaña el capítulo 02 del facsímil 10. Construye una revisión reproducible de eventos de interacción antes de convertirlos en trayectorias o en un replay buffer.

El objetivo no es entrenar una política. El objetivo es validar si los datos son defendibles: contrato, tiempos, propensión, recompensa, linaje, cobertura, retorno y snapshot.

## Ejecutar

Desde esta carpeta:

```bash
python3 ops/validate_rl_events.py --write
cat output/rl_event_decision.md
python3 -m json.tool output/rl_event_report.json
```

Para ver cómo falla un dataset que no debería alimentar entrenamiento ni evaluación:

```bash
python3 ops/validate_rl_events.py \
  --events data/events_bad.jsonl \
  --output output_bad \
  --write
cat output_bad/rl_event_decision.md
python3 -m json.tool output_bad/rl_event_report.json
```

También puedes pasar rutas explícitas:

```bash
python3 ops/validate_rl_events.py \
  --events data/events.jsonl \
  --contract contracts/rl_event_contract.json \
  --output output \
  --write
```

## Archivos

| Archivo | Papel |
|---|---|
| `data/events.jsonl` | Eventos de interacción de un asistente de soporte. |
| `data/events_bad.jsonl` | Eventos rotos para observar cómo bloquea el gate. |
| `contracts/rl_event_contract.json` | Contrato de evento RL: campos, tipos, catálogos, tiempos, umbrales y gamma. |
| `ops/validate_rl_events.py` | Script sin dependencias externas para validar eventos y crear snapshot. |
| `sql/warehouse_schema.sql` | Esquema físico mínimo para llevar estos eventos a warehouse. |
| `sql/query_examples.sql` | Consultas de auditoría: cobertura, propensión, recompensa tardía y episodios abiertos. |
| `output/rl_event_report.json` | Reporte con checks, errores, retornos, cobertura y hash. |
| `output/trajectory_snapshot.json` | Snapshot gold de trayectorias ordenadas. |
| `output/rl_event_decision.md` | Decisión técnica: aceptar, revisar o bloquear. |
| `output_bad/*` | Outputs esperados al ejecutar el dataset roto. |

## Qué deberías mirar

1. `status`: si el snapshot queda en `pass`, `review` o `block`.
2. `checks`: qué reglas pasan y cuáles fallan.
3. `episode_returns`: retorno descontado por episodio.
4. `coverage.state_action`: cobertura por pareja estado-acción.
5. `low_coverage_pairs`: huecos que no conviene esconder en la media.
6. `snapshot_hash`: identificador estable del corte de datos.
7. `lineage`: contrato, política, reward y entorno presentes en los eventos.
8. `output_bad/rl_event_report.json`: errores concretos que deberían bloquear el snapshot.
9. `sql/query_examples.sql`: consultas que llevarías a un notebook, dbt model o job de auditoría.

## Cómo lo escalarías con herramientas reales

| Capa | Herramientas posibles | Adaptación de este kit |
|---|---|---|
| Validación | Great Expectations, Pandera, Deequ | Convertir `rl_event_contract.json` en expectativas o schema ejecutable. |
| Linaje | OpenLineage, Marquez, DataHub | Emitir un evento de linaje cada vez que se genere `trajectory_snapshot.json`. |
| Versionado | DVC, lakeFS, Delta Lake | Versionar `events.jsonl`, snapshots y reportes. |
| Orquestación | Airflow, Dagster, Prefect | Ejecutar el validador antes de publicar un snapshot. |
| Tracking | MLflow, Weights & Biases | Registrar hash, métricas de cobertura y decisión de gate en cada run. |
| RL | Vowpal Wabbit, Ray RLlib, TorchRL, CleanRL | Entrenar o simular solo cuando `status=pass`. |

## Cómo lo adaptas a un proyecto propio

1. Cambia `data/events.jsonl` por eventos de tu sistema.
2. Ajusta `contracts/rl_event_contract.json` con tus acciones, versiones y umbrales.
3. Añade campos de estado que expliquen decisiones reales, pero minimiza datos personales.
4. Ejecuta el script antes de entrenar, evaluar offline o comparar políticas.
5. Guarda los outputs como evidencia de la run.
6. Convierte `sql/query_examples.sql` en vistas o tests de tu warehouse.
7. Mantén un dataset roto pequeño para comprobar que el gate falla cuando debe fallar.

## Qué entregaría un alumno

1. Un JSONL con tres episodios como mínimo.
2. Un contrato adaptado a su caso.
3. El reporte JSON generado.
4. El snapshot de trayectorias.
5. Una decisión Markdown explicando si usaría, revisaría o bloquearía los datos.
6. Una mejora concreta para aumentar cobertura de una pareja estado-acción.
7. Una explicación de por qué `action_probability` y `reward_time` no son campos decorativos.
8. Una consulta SQL propia que detecte un fallo de datos de interacción en su dominio.

## Qué te llevas

Te llevas una práctica ejecutable sobre eventos RL, trayectorias y replay buffer, con datos editables, contratos y umbrales, consultas SQL, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/events.jsonl` y `data/events_bad.jsonl`, contrastas la decisión contra `contracts/rl_event_contract.json` y ejecutas `ops/validate_rl_events.py` para generar `output/rl_event_decision.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/rl_event_decision.md` como línea base.
- Cambia o añade un caso en `data/events.jsonl` y `data/events_bad.jsonl` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/rl_event_contract.json` y explica por qué el resultado debería cambiar o bloquearse.
- Lleva `sql/query_examples.sql` y `sql/warehouse_schema.sql` a una tabla propia o a un notebook y comprueba si responde a una pregunta operativa real.
- Compara el caso que pasa con el caso roto o arriesgado y escribe qué señal lo bloquea.
- Compara antes/después en `output/rl_event_decision.md` y `output/rl_event_report.json` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/validate_rl_events.py`, abre `output/rl_event_decision.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/events.jsonl`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `Kit F10 C02: eventos RL, trayectorias y replay buffer`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/events.jsonl`, `data/events_bad.jsonl`.
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/rl_event_contract.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `sql/`: consultas o esquemas para llevar el ejercicio a un entorno de datos. Ejemplos dentro del ZIP: `sql/query_examples.sql`, `sql/warehouse_schema.sql`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/validate_rl_events.py`.
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_lab_contract.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/rl_event_decision.md`, `output/rl_event_report.json`, `output/trajectory_snapshot.json`, `output/coverage_state_action.csv`.
- `output_bad/`: salidas de fallo para aprender qué debe bloquearse. Ejemplos dentro del ZIP: `output_bad/rl_event_decision.md`, `output_bad/rl_event_report.json`, `output_bad/trajectory_snapshot.json`, `output_bad/coverage_state_action.csv`.

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/rl_event_decision.md`: lectura humana de la decisión, informe o runbook.
- `output_bad/rl_event_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/rl_event_report.json`: evidencia estructurada para validar o automatizar.
- `output/trajectory_snapshot.json`: evidencia estructurada para validar o automatizar.
- `output_bad/rl_event_report.json`: evidencia estructurada para validar o automatizar.
- `output_bad/trajectory_snapshot.json`: evidencia estructurada para validar o automatizar.
- `output/coverage_state_action.csv`: tabla que puedes inspeccionar o cargar en un notebook.
- `output_bad/coverage_state_action.csv`: tabla que puedes inspeccionar o cargar en un notebook.

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
6. Lleva las consultas de `sql/` a tu warehouse o notebook y comprueba que responden a una pregunta operativa real.
7. Guarda los outputs finales y una nota breve con la decisión técnica que tomarías en un proyecto real.

### Criterio de validación

El kit está completo cuando se puede descargar, extraer, ejecutar con `make run`, validar con `make test` y explicar sin depender de ninguna carpeta externa. Si una práctica menciona código, datos, contrato, CSV, SQL, política o plantilla, ese contenido debe venir dentro del ZIP.
<!-- zip-quality-audit:end -->
