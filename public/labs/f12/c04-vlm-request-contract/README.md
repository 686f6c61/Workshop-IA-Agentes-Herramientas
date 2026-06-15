# F12 C04 · Contrato de petición VLM

Este laboratorio acompaña el capítulo 04 del facsímil 12. No llama a un proveedor de visión-lenguaje. Antes de usar uno, construye lo que un equipo serio debería tener: contrato de entrada, presupuesto visual, esquema de salida, evidencias obligatorias, reglas de rechazo y disparadores de revisión humana.

## Casos incluidos

El caso `grant_workflow_005` continúa el hilo de la solicitud de beca bloqueada. La imagen muestra el botón desactivado y la alerta; el PDF sintético explica la política; la tabla CSV aporta estado operativo. La práctica consiste en no dejar que el VLM decida solo: describe la evidencia visual y exige validación no visual.

El ZIP trae más casos para que no entrenes solo el camino feliz:

| Caso | Qué fuerza a practicar | Resultado sano |
|---|---|---|
| `grant_workflow_005` | Separar evidencia visual, política y estado operativo. | Explicar el bloqueo sin prometer aprobación. |
| `invoice_total_002` | No convertir una imagen de factura en extracción contable definitiva. | Derivar a OCR/layout y declarar límites. |
| `product_policy_003` | Usar VLM como prechequeo, no como autoridad legal. | Preclasificar y pedir revisión sensible. |
| `visual_injection_004` | Tratar texto dentro de imagen como dato no confiable. | Bloquear acción irreversible y pedir revisión. |
| `low_quality_005` | No inventar cuando la captura no permite leer evidencia. | Pedir mejor imagen o fuente textual. |

## Ejecutar

```bash
make run
make test
```

El script genera:

| Archivo | Qué contiene |
|---|---|
| `output/vlm_request_report.md` | Informe humano con rutas, presupuesto visual, warnings e issues. |
| `output/vlm_request_report.json` | Informe estructurado para CI o revisión. |
| `output/request_contracts/*.json` | Peticiones VLM acotadas por caso. |
| `output/vlm_architecture_contract.svg` | Figura del contrato con firma del proyecto. |

El reporte no solo dice si pasa. También separa `pass`, `review` y `block`. En esta práctica, un bloqueo correcto cuenta como una capacidad: si la imagen contiene una instrucción no confiable o pide una acción irreversible, el sistema debe parar.

## Qué deberías mirar

1. `route`: si el VLM hace triage visual, extracción documental, recuperación, validación con herramienta o revisión humana.
2. `visual_token_budget`: cuánto cuesta la imagen antes de generar nada.
3. `required_output_fields`: si la salida exige evidencia y límites.
4. `refusal_rules`: cuándo debe negarse, pedir mejor imagen o escalar.
5. `human_review_triggers`: qué no debe decidirse automáticamente.
6. `block_triggers`: qué debe bloquearse sin respuesta operativa.
7. `task_metric`: qué métrica usarías para evaluar ese tipo de caso.
8. `grounding_contract`: cuántas regiones mínimas se citan y qué evidencia se exige.

## Cambios útiles

- Añade una imagen más grande y observa si sube el presupuesto visual.
- Quita una región de evidencia y comprueba que el test conceptual deja de ser defendible.
- Duplica `grant_workflow_005` y prueba una variante con conflicto entre política y tabla de estados.
- Añade un caso de gráfico o pizarra y decide si hace falta OCR, VLM, tabla o revisión humana.
- Convierte `low_visual_quality` en disparador bloqueante dentro de `contracts/vlm_request_policy.json`.
- Añade una caja `bbox` normalizada a una región y explica cómo la medirías con IoU.
- Añade un caso donde la captura sea correcta pero el CSV contradiga la imagen.

## Qué te llevas

Un VLM no debería recibir “mira esta imagen y contesta”. Debe recibir una tarea, una lista de evidencias esperadas, un esquema de salida, reglas de rechazo, métricas y una política de revisión. Este kit deja esa estructura lista para llevarla a una integración real.

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `F12 C04 · Contrato de petición VLM`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; este kit usa la biblioteca estándar de Python.
- `data/vlm_cases.json`: casos editables.
- `data/images/*.svg`: imágenes sintéticas de ejemplo.
- `data/docs/*`: fuentes no visuales del caso guía.
- `contracts/vlm_request_policy.json`: política de validación.
- `schemas/vlm_output_schema.json`: esquema de salida.
- `ops/audit_vlm_requests.py`: código ejecutable.
- `templates/entrega.md`: plantilla editable.
- `tests/test_lab_contract.py`: tests de reproducibilidad.
- `output/`: salidas generadas o esperadas.

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` construye las evidencias del ejercicio. `make test` comprueba que el kit sigue siendo ejecutable después de descargarlo, extraerlo y tocarlo.

### Qué mirar antes de entregar

- `output/vlm_request_report.md`: informe humano.
- `output/request_contracts/grant_workflow_005.json`: contrato del caso guía.
- `output/request_contracts/visual_injection_004.json`: contrato donde bloquear es el resultado correcto.
- `output/request_contracts/low_quality_005.json`: contrato donde la abstención evita inventar evidencia.
- `output/vlm_architecture_contract.svg`: figura del contrato.

### Qué entregar

Una entrega útil debe incluir resultado de `make test`, una modificación razonada en `data/vlm_cases.json` o `contracts/vlm_request_policy.json`, y una decisión técnica sobre si usar VLM, OCR, herramienta, recuperación o revisión humana.

La entrega buena debería defender al menos una decisión incómoda: bloquear una acción, pedir mejor imagen, derivar a OCR/layout o consultar una fuente operativa aunque el VLM parezca capaz de responder.

### Criterio de validación

El kit está completo cuando se puede descargar, extraer, ejecutar con `make run`, validar con `make test` y explicar sin depender de ninguna carpeta externa.
<!-- zip-quality-audit:end -->
