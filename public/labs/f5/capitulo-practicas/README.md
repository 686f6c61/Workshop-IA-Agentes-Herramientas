# Kit F5: prácticas por capítulo

Este kit acompaña los `Manos a la obra` del facsímil 5. Convierte agentes, tools, memoria, harness, SDKs, permisos, routing y evaluación en artefactos ejecutables.

No llama a proveedores externos. La intención es que puedas ejecutar la práctica, leer el JSON, revisar la decisión Markdown y adaptar el patrón a tu proyecto.

Cada práctica entrena una pieza concreta del diseño de agentes. No hay que memorizar el script: hay que entender qué contrato produce y qué cambiarías si el agente fuera real.

Los escenarios y artefactos editables están en `data/practice_cases.json`. Los umbrales, expectativas y la utilidad profesional de cada práctica están en `contracts/practice_policy.json`. Empieza cambiando esos archivos, no el runner: así practicas como en un proyecto real, donde los contratos y políticas viven fuera del código de ejecución.

## Ejecutar todo

```bash
python3 ops/run_f5_practices.py --all --write --fail-on-invalid
```

## Ejecutar un capítulo

```bash
python3 ops/run_f5_practices.py --chapter c03 --write --fail-on-invalid
```

Ejemplo de trabajo:

```bash
python3 ops/run_f5_practices.py --chapter c08 --write --fail-on-invalid
cat output/c08_decision.md
python3 -m json.tool output/c08_report.json
```

## Salidas

Cada capítulo genera:

```text
output/cXX_report.json
output/cXX_decision.md
```

La ejecución completa genera además:

```text
output/all_summary.json
```

## Qué debe demostrar

| Capítulo | Entrega práctica |
|---|---|
| C01 | Manifest operativo de un agente antes de implementarlo. |
| C02 | Bucle estado-acción-observación con presupuesto y parada. |
| C03 | Contrato de tool con schema, permisos, errores y observación. |
| C04 | Handoff reproducible con memoria, compaction y artefactos. |
| C05 | Decision record para elegir arquitectura agentic. |
| C06 | Harness mínimo con límites, sensores y trazas. |
| C07 | Contrato portable antes de casarse con un SDK. |
| C08 | Motor de permisos con cola de aprobación. |
| C09 | Router interoperable entre tool local, MCP, A2A, workflow y revisión humana. |
| C10 | Gate de evaluación de trayectorias, coste, latencia y permisos. |

## Cómo trabajarlo como alumno

1. Ejecuta el capítulo que acabas de leer.
2. Abre el Markdown de decisión y subraya qué parte sería reutilizable en un proyecto real.
3. Abre el JSON y comprueba qué métrica, permiso, presupuesto o traza sostiene la decisión.
4. Cambia un caso de entrada en `data/practice_cases.json`.
5. Cambia un límite o criterio en `contracts/practice_policy.json`.
6. Vuelve a ejecutar y explica por qué la decisión cambió o por qué se mantiene.

## Qué te llevas

Te llevas una práctica ejecutable sobre prácticas por capítulo, con datos editables, contratos y umbrales, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/practice_cases.json`, contrastas la decisión contra `contracts/practice_policy.json` y ejecutas `ops/run_f5_practices.py` para generar `output/c01_decision.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Entrega mínima

Para cerrar una práctica, entrega:

- `output/cXX_decision.md`;
- `output/cXX_report.json`;
- una variante del caso original;
- una explicación breve sobre estado, tool, permiso, coste, traza o gate afectado.

Una práctica buena no dice “el agente funciona”. Dice qué efecto produjo, qué permiso necesitó, qué trazas dejó, cuánto costó y qué gate lo dejaría pasar o bloquearía.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/c01_decision.md` como línea base.
- Cambia o añade un caso en `data/practice_cases.json` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/practice_policy.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara antes/después en `output/c01_decision.md` y `output/c02_decision.md` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/run_f5_practices.py`, abre `output/c01_decision.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/practice_cases.json`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `Kit F5: prácticas por capítulo`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/practice_cases.json`.
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/practice_policy.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/run_f5_practices.py`.
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_lab_contract.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/c01_decision.md`, `output/c02_decision.md`, `output/c03_decision.md`, `output/c04_decision.md`, ....

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/c01_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/c02_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/c03_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/c04_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/c05_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/c06_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/c07_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/c08_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/c09_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/c10_decision.md`: lectura humana de la decisión, informe o runbook.
- `output/all_summary.json`: evidencia estructurada para validar o automatizar.
- `output/c01_report.json`: evidencia estructurada para validar o automatizar.

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
