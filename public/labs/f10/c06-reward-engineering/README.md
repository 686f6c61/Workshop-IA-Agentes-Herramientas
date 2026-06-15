# Kit F10 C06: reward engineering y verificadores

Este kit acompaña el capítulo 06 del facsímil 10. Audita una reward card antes de usarla para entrenar, seleccionar o publicar una política.

El objetivo es comprobar si la recompensa premia lo que declaramos: exactitud, evidencia, formato, abstención y coste razonable. También bloquea especificaciones que dependen demasiado de proxies, bonus de longitud o pocos casos de prueba.

## Ejecutar

```bash
python3 ops/audit_reward_card.py --write
python3 ops/reward_weight_sweep.py
python3 ops/calibrate_thresholds.py --write
python3 ops/validate_trace.py --write
python3 ops/fail_ci_if_blocked.py --report output/reward_card_audit_report.json
cat output/reward_card_decision.md
head -n 8 output/sensitivity_report.csv
cat output/threshold_recommendation.md
cat output/trace_validation_report.json
cat output/grader_confusion_matrix.csv
cat output/reward_card.md
```

Salida esperada:

```text
status=pass
cases=9
```

Escenario que debe bloquear:

```bash
python3 ops/audit_reward_card.py \
  --spec data/reward_spec_bad.json \
  --output output_bad \
  --write
cat output_bad/reward_card_decision.md
python3 ops/reward_weight_sweep.py \
  --spec data/reward_spec_bad.json \
  --output output_bad/sensitivity_report.csv
python3 ops/validate_trace.py \
  --trace data/reward_run_trace_bad.json \
  --output output_bad/trace_validation_report.json \
  --write
python3 ops/fail_ci_if_blocked.py \
  --report output_bad/reward_card_audit_report.json
```

El último comando debe devolver código de salida `1`, porque esa reward card está bloqueada.

Salida esperada:

```text
status=block
cases=4
```

## Archivos

| Archivo | Papel |
|---|---|
| `contracts/reward_card_contract.json` | Gate mínimo de reward card. |
| `contracts/reward_run_trace_contract.json` | Campos mínimos que debería guardar una run en producción. |
| `data/reward_spec.json` | Reward card sana con pesos, categorías, verificadores y casos. |
| `data/reward_spec_bad.json` | Reward card rota: proxy excesivo y bonus de longitud. |
| `data/reward_run_trace.json` | Traza sana para validar operación. |
| `data/reward_run_trace_bad.json` | Traza rota: campos ausentes, gate fallido y reward que no cuadra. |
| `ops/audit_reward_card.py` | Auditor reproducible sin dependencias externas. |
| `ops/reward_weight_sweep.py` | Barrido de sensibilidad de pesos. |
| `ops/calibrate_thresholds.py` | Calibración de umbral por slice. |
| `ops/validate_trace.py` | Validador de trazas de reward. |
| `ops/fail_ci_if_blocked.py` | Check para usar la auditoría en CI. |
| `templates/reward_card_pr_template.md` | Plantilla de PR para cambios de reward card. |
| `output/reward_card_audit_report.json` | Reporte generado. |
| `output/component_scorecard.csv` | Tabla de términos y pesos. |
| `output/case_scorecard.csv` | Resultado por caso. |
| `output/sensitivity_report.csv` | Cambios de ganadores al variar cada peso. |
| `output/threshold_calibration.csv` | Tabla de umbrales, falsos pases y falsos bloqueos. |
| `output/threshold_recommendation.md` | Recomendación de umbral por slice. |
| `output/grader_confusion_matrix.csv` | Precisión, recall y accuracy de los verificadores evaluados. |
| `output/trace_validation_report.json` | Resultado de validar una traza de producción. |
| `output/reward_card_decision.md` | Decisión técnica. |
| `output/reward_card.md` | Tarjeta de recompensa generada. |

## Qué debería mirar el alumno

1. Si están presentes `correctness`, `evidence`, `format` y `abstention`.
2. Si los proxies no pesan demasiado.
3. Si no hay bonus positivo por longitud.
4. Si hay casos ocultos suficientes.
5. Si el ganador por recompensa coincide con el ganador esperado.
6. Si los costes restan, pero no dominan exactitud y evidencia.
7. Si hay restricciones duras con verificadores reales.
8. Si la matriz del verificador muestra falsos positivos o falsos negativos.
9. Si pequeños cambios de pesos cambian muchos ganadores.
10. Si los cambios apuntan a casos explicables, como `sensibilidad_evidencia`.
11. Si las trazas de producción guardan versiones de política, reward card, dataset y graders.
12. Si el umbral recomendado por slice tiene falsos pases tolerables.
13. Si un PR de reward card trae evidencia suficiente para revisarse.

Si `sensitivity_report.csv` marca `sensibilidad_evidencia`, no lo trates como fallo automático de la reward base. Es una alerta para revisar el criterio: al bajar evidencia, la respuesta más completa y barata puede ganar a la respuesta mejor soportada.

## Qué te llevas

Te llevas una práctica ejecutable sobre reward engineering y verificadores, con datos editables, contratos y umbrales, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/reward_run_trace.json` y `data/reward_run_trace_bad.json`, contrastas la decisión contra `contracts/reward_card_contract.json` y `contracts/reward_run_trace_contract.json` y ejecutas `ops/audit_reward_card.py` para generar `output/reward_card.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/reward_card.md` como línea base.
- Cambia o añade un caso en `data/reward_run_trace.json` y `data/reward_run_trace_bad.json` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/reward_card_contract.json` y `contracts/reward_run_trace_contract.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara el caso que pasa con el caso roto o arriesgado y escribe qué señal lo bloquea.
- Compara antes/después en `output/reward_card.md` y `output/reward_card_decision.md` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/audit_reward_card.py`, abre `output/reward_card.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/reward_run_trace.json`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `Kit F10 C06: reward engineering y verificadores`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/reward_run_trace.json`, `data/reward_run_trace_bad.json`, `data/reward_spec.json`, `data/reward_spec_bad.json`.
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/reward_card_contract.json`, `contracts/reward_run_trace_contract.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`, `templates/reward_card_pr_template.md`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/audit_reward_card.py`, `ops/calibrate_thresholds.py`, `ops/fail_ci_if_blocked.py`, `ops/reward_weight_sweep.py`, ....
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_lab_contract.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/reward_card.md`, `output/reward_card_decision.md`, `output/threshold_recommendation.md`, `output/reward_card_audit_report.json`, ....
- `output_bad/`: salidas de fallo para aprender qué debe bloquearse. Ejemplos dentro del ZIP: `output_bad/reward_card.md`, `output_bad/reward_card_decision.md`, `output_bad/reward_card_audit_report.json`, `output_bad/trace_validation_report.json`, ....

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/reward_card.md`: lectura humana de la decisión, informe o runbook.
- `output/reward_card_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/threshold_recommendation.md`: lectura humana de la decisión, informe o runbook.
- `output_bad/reward_card.md`: lectura humana de la decisión, informe o runbook.
- `output_bad/reward_card_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/reward_card_audit_report.json`: evidencia estructurada para validar o automatizar.
- `output/trace_validation_report.json`: evidencia estructurada para validar o automatizar.
- `output_bad/reward_card_audit_report.json`: evidencia estructurada para validar o automatizar.
- `output_bad/trace_validation_report.json`: evidencia estructurada para validar o automatizar.
- `output/case_scorecard.csv`: tabla que puedes inspeccionar o cargar en un notebook.
- `output/component_scorecard.csv`: tabla que puedes inspeccionar o cargar en un notebook.
- `output/grader_confusion_matrix.csv`: tabla que puedes inspeccionar o cargar en un notebook.

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
