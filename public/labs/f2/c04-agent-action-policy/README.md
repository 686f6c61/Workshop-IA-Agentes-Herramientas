# Kit F2 C04: política de acciones para un agente

Este kit acompaña el capítulo 04 del facsímil 2. Simula la primera decisión de un agente de ingeniería que recibe una incidencia: la página de checkout falla al cargar.

El objetivo es separar tres cosas que a menudo se mezclan: acciones disponibles, acciones permitidas y acciones recomendables. Un buen agente no solo rankea; también bloquea lo que no debe hacer todavía.

## Ejecutar

Desde esta carpeta:

```bash
python3 ops/rank_agent_actions.py --write
cat output/agent_action_decision.md
```

Como gate:

```bash
python3 ops/rank_agent_actions.py --write --fail-on-invalid
```

## Archivos

| Archivo | Papel |
|---|---|
| `data/agent_case.json` | Estado inicial, incidencia y acciones candidatas. |
| `contracts/action_policy.json` | Pesos de ranking, presupuestos, bloqueos duros y acción esperada. |
| `ops/rank_agent_actions.py` | Motor de elegibilidad, scoring y reporte sin dependencias externas. |
| `output/agent_action_report.json` | Resultado estructurado para revisión automática. |
| `output/agent_action_decision.md` | Informe legible para revisión humana. |

## Qué deberías mirar

1. Qué acciones quedan bloqueadas antes de rankear.
2. Qué acción gana y por qué.
3. Cómo cambia la decisión si subes el peso del riesgo.
4. Qué pasa si permites editar sin evidencia.
5. Qué evidencia mínima pedirías antes de ejecutar una acción destructiva.

## Qué entregaría un alumno

1. El Markdown generado.
2. Una acción nueva con valores justificados de coste, incertidumbre y riesgo.
3. Una política modificada para un caso real de su entorno.
4. Una explicación de qué bloquearía, qué ejecutaría primero y qué criterio de parada usaría.

## Qué te llevas

Te llevas una práctica ejecutable sobre política de acciones para un agente, con datos editables, contratos y umbrales, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/agent_case.json`, contrastas la decisión contra `contracts/action_policy.json` y ejecutas `ops/rank_agent_actions.py` para generar `output/agent_action_decision.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/agent_action_decision.md` como línea base.
- Cambia o añade un caso en `data/agent_case.json` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/action_policy.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara antes/después en `output/agent_action_decision.md` y `output/agent_action_report.json` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/rank_agent_actions.py`, abre `output/agent_action_decision.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/agent_case.json`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `Kit F2 C04: política de acciones para un agente`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/agent_case.json`.
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/action_policy.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/rank_agent_actions.py`.
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_lab_contract.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/agent_action_decision.md`, `output/agent_action_report.json`.

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/agent_action_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/agent_action_report.json`: evidencia estructurada para validar o automatizar.

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
