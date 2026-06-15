# Kit F10 C01: MDP, Bellman y política mínima

Este kit acompaña el capítulo 01 del facsímil 10. Convierte la definición de un MDP en una práctica reproducible: dado un pequeño sistema de soporte, calcula valores, compara acciones y genera una decisión técnica.

El objetivo no es entrenar nada. El objetivo es que puedas mirar un problema secuencial y responder con evidencia: qué estados existen, qué acciones están permitidas, qué recompensa se está optimizando, qué futuro pesa el descuento y qué política sale de Bellman.

## Ejecutar

Desde esta carpeta:

```bash
python3 ops/evaluate_bellman.py --write
cat output/bellman_decision.md
python3 -m json.tool output/policy_iteration_report.json
cat output/value_table.csv
cat output/q_values.csv
```

Como gate:

```bash
python3 ops/evaluate_bellman.py --write --fail-on-gate
```

## Archivos

| Archivo | Papel |
|---|---|
| `data/support_mdp.json` | MDP de soporte con estados, acciones, transiciones y recompensas. |
| `contracts/bellman_contract.json` | Contrato mínimo: gamma, tolerancia, iteraciones y campos requeridos. |
| `ops/evaluate_bellman.py` | Iteración de valor y extracción de política sin dependencias externas. |
| `output/policy_iteration_report.json` | Reporte generado con valores, política, Q-values, delta y gate. |
| `output/value_table.csv` | Tabla compacta de valor por estado y mejor acción. |
| `output/q_values.csv` | Comparación de acciones por estado. |
| `output/bellman_decision.md` | Decisión legible para revisar en clase o en un equipo. |

## Qué deberías mirar

1. Si el MDP declara \(S,A,P,R,\gamma\) de forma explícita.
2. Si las probabilidades de cada acción suman 1.
3. Si la política elige una acción por valor esperado y no por intuición.
4. Si el descuento hace visible el futuro: pedir evidencia puede perder tiempo ahora y ganar después.
5. Si los terminales tienen valor cero porque ya no hay decisión futura.
6. Si cada \(Q(s,a)\) explica por qué una acción gana o pierde.
7. Si el reporte deja suficiente traza para cambiar recompensas y repetir el cálculo.

## Cómo lo adaptas a un proyecto propio

1. Cambia `data/support_mdp.json` por tus estados y acciones.
2. Mantén transiciones explícitas: recompensa, siguiente estado y probabilidad.
3. Ajusta `gamma` en `contracts/bellman_contract.json` según el horizonte real.
4. No aceptes una política si hay acciones sin transición o probabilidades mal normalizadas.
5. Compara siempre \(V(s)\) y \(Q(s,a)\): el valor del estado no explica por sí solo qué acción tomar.
6. Lleva `bellman_decision.md` a una revisión técnica: si nadie entiende qué se optimiza, la política no está lista.

## Qué entregaría un alumno

1. `bellman_decision.md` generado.
2. `value_table.csv` interpretado.
3. `q_values.csv` con una explicación de por qué gana una acción.
4. Un cambio propio en una recompensa o transición y una comparación antes/después.
5. Una frase clara sobre qué parte del problema sí es RL y cuál sería mejor resolver con reglas, RAG o revisión humana.

## Qué te llevas

Te llevas una práctica ejecutable sobre MDP, Bellman y política mínima, con datos editables, contratos y umbrales, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/support_mdp.json`, contrastas la decisión contra `contracts/bellman_contract.json` y ejecutas `ops/evaluate_bellman.py` para generar `output/bellman_decision.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/bellman_decision.md` como línea base.
- Cambia o añade un caso en `data/support_mdp.json` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/bellman_contract.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara antes/después en `output/bellman_decision.md` y `output/policy_iteration_report.json` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/evaluate_bellman.py`, abre `output/bellman_decision.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/support_mdp.json`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `Kit F10 C01: MDP, Bellman y política mínima`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/support_mdp.json`.
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/bellman_contract.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/evaluate_bellman.py`.
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_lab_contract.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/bellman_decision.md`, `output/policy_iteration_report.json`, `output/q_values.csv`, `output/value_table.csv`.

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/bellman_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/policy_iteration_report.json`: evidencia estructurada para validar o automatizar.
- `output/q_values.csv`: tabla que puedes inspeccionar o cargar en un notebook.
- `output/value_table.csv`: tabla que puedes inspeccionar o cargar en un notebook.

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
