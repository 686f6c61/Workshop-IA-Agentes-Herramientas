# F10 · Laboratorio de refuerzo

Este kit cierra el facsímil 10 con dos retos ejecutables:

1. Simular una política bandit para routing de solicitudes.
2. Auditar una recompensa de post-training verificable.

El objetivo no es obtener un número verde y seguir. El objetivo es practicar una decisión de ingeniería: qué política avanza, con qué evidencia, bajo qué límites, con qué evaluación offline, con qué reward card, con qué serving gate y con qué condición de parada.

## Qué vas a construir

| Pieza | Archivo | Para qué sirve |
|---|---|---|
| Comparación de políticas | `output/bandit_policy_report.json` | Ver recompensa acumulada, regret y reparto de acciones. |
| Traza de decisiones | `output/bandit_trace.jsonl` | Revisar ronda, política, acción, recompensa y razón de selección. |
| Decisión de piloto | `output/bandit_policy_decision.md` | Explicar qué política avanza y con qué límites. |
| Auditoría de recompensa | `output/reward_audit_report.json` | Comprobar si la reward spec elige candidatos correctos. |
| Reward card | `output/reward_card.md` | Documentar objetivo, términos, límites y repetición del gate. |
| Gate de CI | `output/ci_reward_gate.json` | Bloquear especificaciones incompletas. |
| Decisión OPE | `ope_decision.md` | Explicar si una política candidata puede pasar a sombra con datos históricos. |
| Quality card OPE | `ope_quality_card.md` | Revisar soporte, ESS, pesos e intervalo de confianza. |
| Decisión de serving | `serving_decision.md` | Decidir si una política versionada avanza en rollout. |
| Runbook de serving | `serving_runbook.md` | Definir rollback, reserva, drift y condiciones operativas. |
| Informe de entrega | `output/student_submission_report.md` | Revisar si la carpeta entregada contiene lo necesario. |

## Ejecutar

Desde esta carpeta:

```bash
make run
make test
```

`make run` ejecuta los dos retos propios del laboratorio y copia desde `evidence/` las cuatro evidencias OPE/serving necesarias para cerrar una revisión completa. Así el kit funciona descargado de forma independiente.

Como gate:

```bash
python3 ops/simulate_bandit_policy.py --write --fail-on-gate
python3 ops/audit_reward_spec.py --write --fail-on-gate
```

Generar solución de referencia:

```bash
python3 ops/simulate_bandit_policy.py --output-dir solutions/reference --write
python3 ops/audit_reward_spec.py --output-dir solutions/reference --write
cp evidence/ope_decision.md solutions/reference/ope_decision.md
cp evidence/ope_quality_card.md solutions/reference/ope_quality_card.md
cp evidence/serving_decision.md solutions/reference/serving_decision.md
cp evidence/serving_runbook.md solutions/reference/serving_runbook.md
python3 ops/check_student_submission.py --submission-dir solutions/reference --write --fail-on-missing
```

## Cómo leer el reto 1

No mires solo `selected_policy`.

Abre:

```bash
python3 -m json.tool output/bandit_policy_report.json
head -n 5 output/bandit_trace.jsonl
cat output/bandit_policy_decision.md
```

Preguntas que debes contestar:

| Pregunta | Dónde mirarla |
|---|---|
| ¿La política supera el gate? | `gate_ok`. |
| ¿Cuánto coste tuvo aprender? | `regret`. |
| ¿Se concentró demasiado tráfico en una ruta cara? | `action_share`. |
| ¿La decisión es reproducible? | `bandit_trace.jsonl`. |
| ¿Hay límites de piloto? | `bandit_policy_decision.md`. |

Una buena respuesta no dice “gana X”. Dice: “X pasa a piloto limitado porque cumple estos umbrales, con estos límites y esta política de reserva”.

## Cómo leer el reto 2

Abre:

```bash
python3 -m json.tool output/reward_audit_report.json
python3 -m json.tool output/ci_reward_gate.json
cat output/reward_card.md
```

Preguntas que debes contestar:

| Pregunta | Dónde mirarla |
|---|---|
| ¿Todos los casos pasan? | `pass_rate`. |
| ¿Falta algún término obligatorio? | `missing_terms`. |
| ¿Se premia longitud de forma directa? | `length_bonus_present`. |
| ¿Qué candidato gana en cada caso? | `cases[].winner`. |
| ¿Qué comportamiento induce la recompensa? | `reward_card.md`. |

El caso sin fuente suficiente es el más importante. Si la recompensa premia una respuesta fluida cuando debería reconocer falta de evidencia, la reward spec no está lista.

## Cómo leer la extensión offline RL / OPE

El capítulo 04 del facsímil enseña una idea incómoda: evaluar una política con datos históricos no es gratis. Si la política candidata elige acciones que casi nunca aparecen en los logs, la estimación puede parecer precisa y estar apoyada en aire.

En el facsímil, OPE se construye en el capítulo 04. En este kit de cierre ya tienes una evidencia OPE cerrada en `evidence/` para no depender de rutas externas. Si trabajas en el repositorio completo y quieres regenerarla desde cero, usa el kit `labs/f10/c04-offline-ope/`.

Lee:

```bash
cat output/ope_decision.md
cat output/ope_quality_card.md
```

Preguntas que debes contestar:

| Pregunta | Dónde mirarla |
|---|---|
| ¿La política candidata tiene soporte en los datos históricos? | `logged_action_support` y `max_unsupported_target_probability_mass`. |
| ¿Los pesos de importancia son razonables? | `max_importance_weight` y `ess_ratio`. |
| ¿Los estimadores discrepan demasiado? | Diferencia entre IPS, WIS, direct method y doubly robust. |
| ¿El intervalo inferior permite avanzar? | `bootstrap_ci_lower`. |
| ¿Qué slices tienen poca muestra? | `slice_diagnostics.csv` y `support_matrix.csv`. |

Una buena respuesta no dice “OPE pasa”. Dice: “OPE permite sombra o piloto muy limitado porque hay soporte suficiente, ESS razonable, estimadores no se separan demasiado y el intervalo inferior no cae bajo el umbral”. Si cualquiera de esas piezas falla, la decisión correcta es recoger más datos, limitar la política o mantener la estable.

## Conectar con serving

Después de estos dos retos, incorpora la evidencia de serving incluida en `evidence/`. En el repositorio completo, esa evidencia se relaciona con el kit del capítulo 07; descargado, este laboratorio ya trae lo necesario para practicar la decisión final.

Lee:

```bash
cat output/serving_decision.md
cat output/serving_runbook.md
```

La comparación entre caso que pasa y caso bloqueado enseña una idea clave: una política no termina al ganar en simulación. Termina cuando puedes decir si avanza, se limita o se revisa.

Para incorporar esta parte a tu entrega final, copia a `rl-lab-release/`:

```text
ope_decision.md
ope_quality_card.md
serving_decision.md
serving_runbook.md
```

Estos cuatro archivos hacen que el laboratorio deje de ser solo aprendizaje de política y reward design. Lo convierten en una revisión de publicación: datos históricos, calidad de estimación, drift, rollout, fallback y rollback.

## Entradas

| Archivo | Uso |
|---|---|
| `contracts/refuerzo_lab_contract.json` | Gates de política bandit y reward spec. |
| `data/bandit_rewards.json` | Recompensas reproducibles para rutas de respuesta. |
| `data/reward_cases.json` | Casos de auditoría para correctness, citation, abstention, cost y format. |
| `evidence/ope_decision.md` | Evidencia OPE ya incorporada para que el laboratorio descargado sea autocontenido. |
| `evidence/ope_quality_card.md` | Tarjeta de calidad OPE con soporte, ESS e intervalo. |
| `evidence/serving_decision.md` | Evidencia de serving y rollout versionado. |
| `evidence/serving_runbook.md` | Runbook de serving con rollback y política de reserva. |

## Entrega esperada

```text
rl-lab-release/
  bandit_policy_report.json
  bandit_policy_decision.md
  bandit_trace.jsonl
  reward_audit_report.json
  reward_card.md
  ci_reward_gate.json
  ope_decision.md
  ope_quality_card.md
  serving_decision.md
  serving_runbook.md
  student_submission_report.md
```

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/audit_reward_spec.py`, abre `output/bandit_policy_decision.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/bandit_rewards.json`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

## Qué te llevas

Te llevas una práctica ejecutable sobre F10 · Laboratorio de refuerzo, con datos editables, contratos y umbrales, evidencias fuente, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/bandit_rewards.json` y `data/reward_cases.json`, contrastas la decisión contra `contracts/refuerzo_lab_contract.json` y ejecutas `ops/audit_reward_spec.py` para generar `output/bandit_policy_decision.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/bandit_policy_decision.md` como línea base.
- Cambia o añade un caso en `data/bandit_rewards.json` y `data/reward_cases.json` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/refuerzo_lab_contract.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara antes/después en `output/bandit_policy_decision.md` y `output/ope_decision.md` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `F10 · Laboratorio de refuerzo`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/bandit_rewards.json`, `data/reward_cases.json`.
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/refuerzo_lab_contract.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `evidence/`: evidencias preconstruidas que el kit usa como entrada o referencia. Ejemplos dentro del ZIP: `evidence/ope_decision.md`, `evidence/ope_quality_card.md`, `evidence/serving_decision.md`, `evidence/serving_runbook.md`, ....
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/audit_reward_spec.py`, `ops/check_student_submission.py`, `ops/simulate_bandit_policy.py`.
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_lab_contract.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/bandit_policy_decision.md`, `output/ope_decision.md`, `output/ope_quality_card.md`, `output/reward_card.md`, ....
- `solutions/`: soluciones de referencia o carpeta para la entrega del alumno. Ejemplos dentro del ZIP: `solutions/reference/bandit_policy_decision.md`, `solutions/reference/ope_decision.md`, `solutions/reference/ope_quality_card.md`, `solutions/reference/reward_card.md`, ....

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/bandit_policy_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/ope_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/ope_quality_card.md`: lectura humana de la decisión, informe o runbook.
- `output/reward_card.md`: lectura humana de la decisión, informe o runbook.
- `output/serving_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/serving_runbook.md`: lectura humana de la decisión, informe o runbook.
- `output/student_submission_report.md`: lectura humana de la decisión, informe o runbook.
- `solutions/reference/bandit_policy_decision.md`: lectura humana de la decisión, informe o runbook.
- `solutions/reference/ope_decision.md`: lectura humana de la decisión, informe o runbook.
- `solutions/reference/ope_quality_card.md`: lectura humana de la decisión, informe o runbook.
- `solutions/reference/reward_card.md`: lectura humana de la decisión, informe o runbook.
- `solutions/reference/serving_decision.md`: lectura humana de la decisión, informe o runbook.

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
6. Usa `solutions/` como contraste de calidad, no como sustituto de tu razonamiento.
7. Guarda los outputs finales y una nota breve con la decisión técnica que tomarías en un proyecto real.

### Criterio de validación

El kit está completo cuando se puede descargar, extraer, ejecutar con `make run`, validar con `make test` y explicar sin depender de ninguna carpeta externa. Si una práctica menciona código, datos, contrato, CSV, SQL, política o plantilla, ese contenido debe venir dentro del ZIP.
<!-- zip-quality-audit:end -->
