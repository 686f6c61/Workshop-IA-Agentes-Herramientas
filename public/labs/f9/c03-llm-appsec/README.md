# F9 C03 · Seguridad de aplicaciones LLM con RAG y tools

Este kit genera un paquete de evidencias para revisar una aplicación LLM antes de publicarla. Simula un asistente académico con RAG y tools, y comprueba si cada escenario respeta permisos, contratos, aprobación, egress y trazabilidad.

## Ejecutar

```bash
python3 ops/run_appsec_gate.py --write
```

Cómo gate de CI:

```bash
python3 ops/run_appsec_gate.py --write --fail-on-blocker
```

El informe distingue dos señales: una decisión `block` o `needs_approval`, que puede ser correcta si el escenario lo exige, y una discrepancia entre `decision` y `expected_decision`, que siempre pide revisión del contrato o del test.

## Archivos de entrada

| Archivo | Uso |
|---|---|
| `contracts/appsec_policy.json` | Política de roles, scopes, tools, aprobación, dominios y reglas de RAG. |
| `data/documents.jsonl` | Documentos simulados del RAG con ACL, finalidad, vigencia y etiqueta de confianza. |
| `data/scenarios.jsonl` | Casos de prueba con rol, documentos recuperados y propuesta de tool. |
| `data/market_tools.csv` | Herramientas de mercado ordenadas por capa y evidencia esperada. |

## Salidas

| Archivo | Qué demuestra |
|---|---|
| `output/appsec_gate_report.md` | Decisión legible por escenario: permitir, bloquear o pedir aprobación. |
| `output/appsec_gate.json` | Resultado máquina para CI. |
| `output/tool_contract_matrix.csv` | Matriz de capabilities, efectos, scopes, aprobación y egress. |
| `output/rag_retrieval_checks.md` | Revisión de documentos recuperados por ACL, finalidad y confianza. |
| `output/trace_sample.jsonl` | Trazas mínimas con decisiones de política sin guardar texto completo. |
| `output/market_tooling_review.md` | Matriz de selección de herramientas por capa, límites y evidencias. |
| `output/day_to_day_playbook.md` | Checklist diario para PRs, RAG, tools, trazas y gate de salida. |

## Cómo adaptarlo

1. Cambia `data/scenarios.jsonl` por conversaciones y tools de tu producto.
2. Cambia `data/documents.jsonl` por metadatos reales de tu RAG.
3. Ajusta `contracts/appsec_policy.json`: roles, scopes, tools, dominios y aprobación.
4. Mantén la idea: el modelo propone y la aplicación decide.

## Qué te llevas

Te llevas una práctica ejecutable sobre F9 C03 · Seguridad de aplicaciones LLM con RAG y tools, con datos editables, contratos y umbrales, plantillas de entrega, código ejecutable y tests reproducibles. Trabajas con `data/market_tools.csv` y `data/documents.jsonl`, contrastas la decisión contra `contracts/appsec_policy.json` y ejecutas `ops/run_appsec_gate.py` para generar `output/appsec_gate_report.md`. La idea no es mirar una solución cerrada: es cambiar una entrada, volver a ejecutar, comparar la salida y poder defender qué harías en una revisión técnica, una asignatura o un piloto real.

## Variantes para hacerlo tuyo

- Ejecuta `make run` sin tocar nada y usa `output/appsec_gate_report.md` como línea base.
- Cambia o añade un caso en `data/market_tools.csv` y `data/documents.jsonl` para representar un problema de tu trabajo, clase o producto.
- Endurece una regla, umbral o campo obligatorio en `contracts/appsec_policy.json` y explica por qué el resultado debería cambiar o bloquearse.
- Compara antes/después en `output/appsec_gate_report.md` y `output/day_to_day_playbook.md` y escribe una decisión de una página: seguir, bloquear, medir más o cambiar el diseño.
- Completa `templates/entrega.md` con contexto, cambio, evidencia, decisión y límite; no la dejes como checklist vacía.

## Rúbrica rápida

| Nivel | Qué demuestra |
|---|---|
| Mínimo | Ejecuta `make run` y `make test`, localiza `ops/run_appsec_gate.py`, abre `output/appsec_gate_report.md` y explica qué decisión o señal produce. |
| Bueno | Cambia `data/market_tools.csv`, compara antes/después y justifica la diferencia con una evidencia concreta del output. |
| Excelente | Convierte el kit en un mini caso profesional: añade un caso propio, ajusta una regla o test, documenta el límite principal y deja una recomendación accionable para un equipo. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `F9 C03 · Seguridad de aplicaciones LLM con RAG y tools`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; muchos kits solo usan la biblioteca estándar de Python.
- `data/`: datos de entrada o casos de prueba realistas. Ejemplos dentro del ZIP: `data/documents.jsonl`, `data/scenarios.jsonl`, `data/market_tools.csv`.
- `contracts/`: contratos de datos, salida, política o validación. Ejemplos dentro del ZIP: `contracts/appsec_policy.json`.
- `templates/`: plantillas editables para la entrega. Ejemplos dentro del ZIP: `templates/entrega.md`.
- `ops/`: código ejecutable del laboratorio. Ejemplos dentro del ZIP: `ops/run_appsec_gate.py`.
- `tests/`: tests que comprueban que el ejercicio sigue siendo reproducible. Ejemplos dentro del ZIP: `tests/test_lab_contract.py`.
- `output/`: salidas generadas o esperadas que debes revisar. Ejemplos dentro del ZIP: `output/appsec_gate_report.md`, `output/day_to_day_playbook.md`, `output/market_tooling_review.md`, `output/rag_retrieval_checks.md`, ....

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/appsec_gate_report.md`: lectura humana de la decisión, informe o runbook.
- `output/day_to_day_playbook.md`: lectura humana de la decisión, informe o runbook.
- `output/market_tooling_review.md`: lectura humana de la decisión, informe o runbook.
- `output/rag_retrieval_checks.md`: lectura humana de la decisión, informe o runbook.
- `output/appsec_gate.json`: evidencia estructurada para validar o automatizar.
- `output/trace_sample.jsonl`: eventos o registros línea a línea.
- `output/tool_contract_matrix.csv`: tabla que puedes inspeccionar o cargar en un notebook.

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
