# Kit F10 C03: bandits y validación de políticas

Este kit acompaña el capítulo 03 del facsímil 10. Simula políticas bandit para routing de modelos y genera una decisión técnica de piloto.

El objetivo no es encontrar una política perfecta. El objetivo es aprender a comparar exploración, recompensa, regret, trazas y gates antes de mover tráfico real.
El resultado final debe permitir una conversación de ingeniería: qué política se propone, qué evidencia hay, dónde no se explora, cómo se haría shadow y bajo qué condiciones se vuelve a la política estable.

## Ejecutar

Desde esta carpeta:

```bash
python3 ops/simulate_policy_gate.py --write
cat output/policy_decision.md
python3 -m json.tool output/bandit_validation_report.json
python3 -m json.tool output/shadow_replay_report.json
```

Para el escenario que debe quedar en revisión:

```bash
python3 ops/simulate_policy_gate.py \
  --scenario data/routing_scenario_risky.json \
  --output output_risky \
  --write
cat output_risky/policy_decision.md
```

## Archivos

| Archivo | Papel |
|---|---|
| `data/routing_scenario.json` | Rondas reproducibles de routing con recompensas por acción. |
| `data/routing_scenario_risky.json` | Escenario con más criticidad para forzar revisión. |
| `contracts/bandit_policy_contract.json` | Gates de regret, exploración, coste, slices y trazas. |
| `ops/simulate_policy_gate.py` | Simulador sin dependencias externas. |
| `runbooks/pilot_runbook.md` | Runbook de piloto con flag, fallback, métricas y condiciones de parada. |
| `output/bandit_validation_report.json` | Comparación de políticas, gates y recomendación. |
| `output/shadow_replay_report.json` | Checklist de shadow y preparación para piloto. |
| `output/bandit_trace.jsonl` | Traza por ronda con acción, probabilidad, recompensa y regret. |
| `output/policy_scorecard.csv` | Tabla compacta por política. |
| `output/policy_decision.md` | Decisión técnica de piloto. |

## Qué deberías mirar

1. `selected_policy`: política recomendada por el gate.
2. `cumulative_reward`: recompensa total, no solo media.
3. `regret`: coste de aprendizaje.
4. `exploration_share`: cuánto tráfico se usó para probar.
5. `sensitive_exploration_count`: si se exploró donde el contrato lo limitaba.
6. `bandit_trace.jsonl`: si cada ronda deja contexto, acción, probabilidad y motivo.
7. `shadow_replay_report.json`: si el piloto tiene checks de preparación antes de decidir online.
8. `runbooks/pilot_runbook.md`: si la decisión tiene rollout, fallback y parada.

## Cómo lo adaptas a un proyecto propio

1. Cambia `routing_scenario.json` por rondas de tu sistema.
2. Mantén `reward_by_action` separado por acción para simular comparaciones.
3. Ajusta `bandit_policy_contract.json` con tus umbrales reales.
4. No publiques una política si el gate queda en `review` o `block`.
5. Guarda la traza como evidencia para evaluación offline.
6. Antes del piloto, ejecuta la política en shadow y compara recomendaciones contra la ruta estable.
7. Lleva el runbook a una revisión técnica: si no puedes explicar rollback y condiciones de parada, no hay piloto.

## Qué te llevas

Te llevas una práctica ejecutable sobre bandits y validación de políticas, con datos editables, contratos y umbrales, runbooks, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/routing_scenario.json` y `data/routing_scenario_risky.json`, contrastas la decisión contra `contracts/bandit_policy_contract.json` y ejecutas `ops/simulate_policy_gate.py` para generar `output/policy_decision.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Qué entregaría un alumno

1. Reporte JSON generado.
2. Scorecard CSV interpretada.
3. Decisión Markdown.
4. Una explicación de por qué una política gana o queda limitada.
5. Un cambio de contrato y una predicción de cómo afectaría al gate.
6. Una propuesta de logging para poder evaluar la política offline después.
7. Un `pilot_runbook.md` adaptado a su caso, con métrica, owner, rollout y rollback.
8. Un informe de shadow que diga si la política candidata merece pasar a piloto o debe seguir en simulación.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/policy_decision.md` como línea base.
- Cambia o añade un caso en `data/routing_scenario.json` y `data/routing_scenario_risky.json` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/bandit_policy_contract.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara el caso que pasa con el caso roto o arriesgado y escribe qué señal lo bloquea.
- Compara antes/después en `output/policy_decision.md` y `output/bandit_validation_report.json` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/simulate_policy_gate.py`, abre `output/policy_decision.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/routing_scenario.json`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `Kit F10 C03: bandits y validación de políticas`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/routing_scenario.json`, `data/routing_scenario_risky.json`.
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/bandit_policy_contract.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `runbooks/`: procedimientos de operación o respuesta. Ejemplos dentro del ZIP: `runbooks/pilot_runbook.md`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/simulate_policy_gate.py`.
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_lab_contract.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/policy_decision.md`, `output/bandit_validation_report.json`, `output/shadow_replay_report.json`, `output/bandit_trace.jsonl`, ....
- `output_risky/`: salidas de escenario arriesgado o alternativo. Ejemplos dentro del ZIP: `output_risky/policy_decision.md`, `output_risky/bandit_validation_report.json`, `output_risky/shadow_replay_report.json`, `output_risky/bandit_trace.jsonl`, ....

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/policy_decision.md`: lectura humana de la decisión, informe o runbook.
- `output_risky/policy_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/bandit_validation_report.json`: evidencia estructurada para validar o automatizar.
- `output/shadow_replay_report.json`: evidencia estructurada para validar o automatizar.
- `output_risky/bandit_validation_report.json`: evidencia estructurada para validar o automatizar.
- `output_risky/shadow_replay_report.json`: evidencia estructurada para validar o automatizar.
- `output/bandit_trace.jsonl`: eventos o registros línea a línea.
- `output_risky/bandit_trace.jsonl`: eventos o registros línea a línea.
- `output/policy_scorecard.csv`: tabla que puedes inspeccionar o cargar en un notebook.
- `output_risky/policy_scorecard.csv`: tabla que puedes inspeccionar o cargar en un notebook.

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
