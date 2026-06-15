# F12 C09 · Computer use harness

Este laboratorio acompaña el capítulo 09 del facsímil 12. Simula un arnés de computer use donde un agente observa una interfaz, propone acciones y una política decide si la acción se ejecuta, pide aprobación, se revisa o se bloquea.

No llama a APIs externas ni abre un navegador real. Está diseñado para que puedas estudiar la parte de ingeniería: observación, objetivos, targets accesibles, acciones, permisos, trazas y evaluación.

El kit trae además un ejemplo opcional con el SDK oficial de OpenAI. No se ejecuta en los tests porque necesita `OPENAI_API_KEY`, pero está incluido para que veas cómo convertir el contrato local en `tools` y `text.format` reales de Responses API.

## Ejecutar

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

Si quieres probar los contratos contra OpenAI Responses API:

```bash
python3 -m pip install -r requirements-openai.txt
export OPENAI_API_KEY="..."
python3 guides/openai_responses_contracts.py
```

## Casos incluidos

| Caso | Qué fuerza a practicar | Resultado sano |
|---|---|---|
| `t01_preparar_respuesta_revisable_ticket` | Buscar, abrir y preparar respuesta revisable sin enviar. | `success`. |
| `t02_factura_pago` | Botón financiero con consecuencia real. | `needs_approval`. |
| `t03_inyeccion_visual_exportar` | Página que intenta ordenar exportar datos. | `block`. |
| `t04_reinicio_api` | Acción operativa destructiva. | `needs_approval`. |
| `t05_click_por_coordenadas` | Click no trazable por coordenadas. | `review`. |
| `t06_target_ambiguo` | Dos botones con el mismo role/name. | `review`. |
| `t07_envio_externo_alumno` | Enviar una respuesta real no es preparar una respuesta revisable. | `needs_approval`. |

## Qué genera

| Archivo | Qué contiene |
|---|---|
| `output/computer_use_report.md` | Informe humano con decisiones y flags. |
| `output/computer_use_report.json` | Informe estructurado para CI o revisión. |
| `output/action_eval_matrix.csv` | Métricas por tarea: pasos, aprobaciones, bloqueos y acciones inválidas. |
| `output/trace_cards/*.json` | Traza completa por tarea. |
| `output/computer_use_harness.svg` | Arquitectura del arnés con firma del proyecto. |
| `output/capacity_report.md` | Estimación de capacidad, latencia, revisión humana y coste. |
| `output/capacity_matrix.csv` | Matriz de coste y tiempo por tarea. |
| `contracts/openai_request_ui_action_tool.json` | Tool strict de Responses API para que el modelo proponga una acción. |
| `contracts/openai_approval_card_text_format.json` | Structured Output para generar una tarjeta de aprobación. |
| `guides/openai_responses_contracts.py` | Ejemplo con el SDK oficial de OpenAI que usa ambos contratos. |

## Qué deberías tocar

1. Abre `data/computer_use_tasks.json`.
2. Mira qué acción propone cada tarea.
3. Ejecuta `make run`.
4. Abre `output/action_eval_matrix.csv`.
5. Abre `output/trace_cards/t03_inyeccion_visual_exportar.json`.
6. Comprueba por qué el botón de exportación no se ejecuta.
7. Cambia `allow_coordinate_clicks` a `true` y decide si aceptarías ese riesgo.
8. Quita `financial` de `approval_required_tags` y observa qué pasaría con la factura.
9. Abre `output/trace_cards/t06_target_ambiguo.json` y comprueba por qué no basta con role/name si no es único.
10. Abre `output/trace_cards/t07_envio_externo_alumno.json` y mira por qué enviar al alumno pide aprobación.
11. Abre `output/capacity_report.md` y cambia `data/capacity_assumptions.json`.
12. Baja `browser_workers` o sube `tasks_per_day` y decide si necesitas cola, más workers o menos pasos por tarea.

## Qué te llevas

Computer use no es “el modelo hace clic”. Es un loop con observación, target, política, ejecución, nueva observación, trazas y capacidad. La parte profesional está en no dejar que una página, un botón o una coordenada gobiernen la acción, y en saber si la operación aguanta cuando pasas de una demo a 200 tareas al día.

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `F12 C09 · Computer use harness`.

### Qué contiene

- `README.md`: esta guía.
- `Makefile`: entrada única para ejecutar y validar.
- `requirements.txt`: dependencias declaradas; usa biblioteca estándar.
- `contracts/computer_use_policy.json`: política de dominios, approvals, aislamiento y gates.
- `contracts/openai_request_ui_action_tool.json`: tool strict compatible con OpenAI Responses API.
- `contracts/openai_approval_card_text_format.json`: formato JSON Schema para Structured Outputs.
- `data/ui_states.json`: estados de interfaz simulados con roles, nombres, textos y riesgos.
- `data/computer_use_tasks.json`: tareas y acciones propuestas.
- `data/capacity_assumptions.json`: supuestos de latencia, tokens, coste y mezcla de tareas.
- `schemas/computer_use_trace_schema.json`: contrato mínimo de traza.
- `ops/run_computer_use_harness.py`: arnés ejecutable.
- `ops/estimate_capacity.py`: estimador operativo de capacidad y revisión humana.
- `guides/openai_responses_contracts.py`: ejemplo opcional con el SDK oficial de OpenAI.
- `requirements-openai.txt`: dependencia opcional para ejecutar el ejemplo con API real.
- `templates/entrega.md`: plantilla editable.
- `tests/test_lab_contract.py`: tests de reproducibilidad.
- `output/`: salidas generadas o esperadas.

### Ejecutar desde cero

```bash
make run
make test
```

### Qué mirar antes de entregar

- `output/computer_use_report.md`
- `output/action_eval_matrix.csv`
- `output/capacity_report.md`
- `contracts/openai_request_ui_action_tool.json`
- `contracts/openai_approval_card_text_format.json`
- `guides/openai_responses_contracts.py`
- `output/trace_cards/t01_preparar_respuesta_revisable_ticket.json`
- `output/trace_cards/t03_inyeccion_visual_exportar.json`
- `output/trace_cards/t05_click_por_coordenadas.json`
- `output/trace_cards/t06_target_ambiguo.json`
- `output/trace_cards/t07_envio_externo_alumno.json`

### Criterio de validación

El kit está completo cuando se puede descargar, extraer, ejecutar con `make run`, validar con `make test` y defender cada decisión sin depender de ninguna carpeta externa.
<!-- zip-quality-audit:end -->
