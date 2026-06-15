# Kit F10 C04: offline RL y evaluación contrafactual

Este kit acompaña el capítulo 04 del facsímil 10. Evalúa una política candidata con datos históricos generados por otra política.

El objetivo no es demostrar que una política nueva sea perfecta. El objetivo es aprender a detectar si los logs tienen propensión, soporte, pesos razonables y estimadores suficientemente consistentes para pasar a modo sombra o piloto limitado.

## Ejecutar

Desde esta carpeta:

```bash
python3 ops/evaluate_offline_policy.py --write
cat output/ope_decision.md
python3 -m json.tool output/ope_report.json
cat output/ope_quality_card.md
```

Salida esperada:

```text
status=pass
events=12
doubly_robust=...
```

Para el escenario que debe bloquear:

```bash
python3 ops/evaluate_offline_policy.py \
  --events data/logged_policy_events_bad.jsonl \
  --output output_bad \
  --write
cat output_bad/ope_decision.md
```

Salida esperada:

```text
status=block
events=6
```

## Archivos

| Archivo | Papel |
|---|---|
| `data/logged_policy_events.jsonl` | Eventos históricos con acción, reward, propensión y probabilidades de política candidata. |
| `data/logged_policy_events_bad.jsonl` | Caso con pesos extremos y soporte insuficiente. |
| `contracts/ope_contract.json` | Gate de OPE: eventos mínimos, ESS, pesos máximos y coherencia entre estimadores. |
| `ops/evaluate_offline_policy.py` | Calcula DM, IPS, WIS, doubly robust y diagnósticos. |
| `sql/ope_warehouse_schema.sql` | Modelo mínimo de tablas para auditar OPE en warehouse. |
| `sql/ope_quality_queries.sql` | Consultas para pesos extremos, soporte, ESS y runs que no deberían avanzar. |
| `output/ope_report.json` | Reporte generado con estimadores, checks y diagnósticos. |
| `output/importance_weights.csv` | Pesos de importancia por evento. |
| `output/slice_diagnostics.csv` | Diagnósticos por slice: DR, ESS, peso máximo y soporte. |
| `output/support_matrix.csv` | Matriz de soporte por slice y acción. |
| `output/estimator_scorecard.csv` | Tabla compacta de estimadores y diagnósticos. |
| `output/ope_decision.md` | Decisión técnica para pasar a sombra, piloto o bloquear. |
| `output/ope_quality_card.md` | Tarjeta de calidad para revisar el run como artefacto de datos. |

## Qué deberías mirar

1. `doubly_robust`: estimación principal para comparar con el umbral.
2. `ips` y `wis`: si se separan mucho, los pesos pueden estar dominando.
3. `ess_ratio`: tamaño efectivo de muestra; no basta contar filas.
4. `max_importance_weight`: si un evento manda demasiado, la conclusión no es estable.
5. `logged_action_support`: cuánta masa de la política candidata aparece realmente en acciones observadas.
6. `importance_weights.csv`: qué eventos explican la estimación.
7. `slice_diagnostics.csv`: si un slice queda mucho peor que la media.
8. `support_matrix.csv`: si la política candidata quiere acciones sin soporte observado.
9. `bootstrap_ci_lower`: si el límite inferior permite avanzar con prudencia.
10. `max_unsupported_target_probability_mass`: si una acción sin soporte tiene demasiada masa candidata.

## Cómo lo adaptas a un proyecto propio

1. Cambia `logged_policy_events.jsonl` por logs de tu sistema.
2. Mantén `behavior_action_probability`; sin ella, OPE se vuelve muy débil.
3. Calcula `target_policy_probability_by_action` con la política candidata sin ejecutarla.
4. Entrena o aproxima `q_model_reward_by_action` con validación separada.
5. Ajusta `ope_contract.json` a tu tolerancia de riesgo.
6. Si el gate bloquea, no subas a piloto: recoge mejor cobertura o limita la política candidata.
7. Carga pesos y runs en tu warehouse con `sql/ope_warehouse_schema.sql`.
8. Automatiza `sql/ope_quality_queries.sql` como control previo a modo sombra.

## Qué entregaría un alumno

1. Reporte JSON generado.
2. CSV de pesos interpretado.
3. Decisión Markdown.
4. Una explicación de por qué IPS, WIS, DM y DR coinciden o discrepan.
5. Un cambio de política candidata y predicción de cómo afectaría a ESS y soporte.
6. Un criterio de paso a modo sombra y un criterio de bloqueo.
7. Una consulta SQL propia para detectar pesos extremos o huecos de soporte.
8. Una `ope_quality_card.md` defendiendo si el dataset sirve o no sirve.

## Qué te llevas

Te llevas una práctica ejecutable sobre offline RL y evaluación contrafactual, con datos editables, contratos y umbrales, consultas SQL, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/logged_policy_events.jsonl` y `data/logged_policy_events_bad.jsonl`, contrastas la decisión contra `contracts/ope_contract.json` y ejecutas `ops/evaluate_offline_policy.py` para generar `output/ope_decision.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/ope_decision.md` como línea base.
- Cambia o añade un caso en `data/logged_policy_events.jsonl` y `data/logged_policy_events_bad.jsonl` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/ope_contract.json` y explica por qué el resultado debería cambiar o bloquearse.
- Lleva `sql/ope_quality_queries.sql` y `sql/ope_warehouse_schema.sql` a una tabla propia o a un notebook y comprueba si responde a una pregunta operativa real.
- Compara el caso que pasa con el caso roto o arriesgado y escribe qué señal lo bloquea.
- Compara antes/después en `output/ope_decision.md` y `output/ope_quality_card.md` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/evaluate_offline_policy.py`, abre `output/ope_decision.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/logged_policy_events.jsonl`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `Kit F10 C04: offline RL y evaluación contrafactual`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/logged_policy_events.jsonl`, `data/logged_policy_events_bad.jsonl`.
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/ope_contract.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `sql/`: consultas o esquemas para llevar el ejercicio a un entorno de datos. Ejemplos dentro del ZIP: `sql/ope_quality_queries.sql`, `sql/ope_warehouse_schema.sql`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/evaluate_offline_policy.py`.
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_lab_contract.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/ope_decision.md`, `output/ope_quality_card.md`, `output/ope_report.json`, `output/estimator_scorecard.csv`, ....
- `output_bad/`: salidas de fallo para aprender qué debe bloquearse. Ejemplos dentro del ZIP: `output_bad/ope_decision.md`, `output_bad/ope_quality_card.md`, `output_bad/ope_report.json`, `output_bad/estimator_scorecard.csv`, ....

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/ope_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/ope_quality_card.md`: lectura humana de la decisión, informe o runbook.
- `output_bad/ope_decision.md`: lectura humana de la decisión, informe o runbook.
- `output_bad/ope_quality_card.md`: lectura humana de la decisión, informe o runbook.
- `output/ope_report.json`: evidencia estructurada para validar o automatizar.
- `output_bad/ope_report.json`: evidencia estructurada para validar o automatizar.
- `output/estimator_scorecard.csv`: tabla que puedes inspeccionar o cargar en un notebook.
- `output/importance_weights.csv`: tabla que puedes inspeccionar o cargar en un notebook.
- `output/slice_diagnostics.csv`: tabla que puedes inspeccionar o cargar en un notebook.
- `output/support_matrix.csv`: tabla que puedes inspeccionar o cargar en un notebook.
- `output_bad/estimator_scorecard.csv`: tabla que puedes inspeccionar o cargar en un notebook.
- `output_bad/importance_weights.csv`: tabla que puedes inspeccionar o cargar en un notebook.

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
