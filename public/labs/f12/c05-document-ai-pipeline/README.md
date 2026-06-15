# F12 C05 · Pipeline Document AI

Este laboratorio acompaña el capítulo 05 del facsímil 12. No llama a Google, Azure, AWS ni a ningún VLM externo. Simula el contrato de ingeniería que necesitas antes de integrar un servicio de Document AI: páginas, regiones, OCR, layout, campos, tablas, chunks citables, validación numérica, revisión humana y bloqueo de instrucciones no confiables.

## Casos incluidos

| Caso | Qué fuerza a practicar | Resultado sano |
|---|---|---|
| `grant_policy_005` | Extraer reglas y fecha de una política con evidencia por página. | Revisar antes de decidir expediente. |
| `invoice_line_items_002` | Extraer factura con line items, subtotal, IVA y total. | Pasar si campos, tabla y suma cuadran. |
| `low_quality_scan_003` | Detectar escaneo ilegible. | Revisar o pedir nuevo documento. |
| `merged_table_004` | No perder cabecera agrupada en tabla. | Revisar estructura antes de usar en RAG o cálculo. |
| `visual_instruction_doc_006` | Tratar texto del documento como dato no confiable. | Bloquear acción sensible. |

## Ejecutar

```bash
make run
make test
```

El script genera:

| Archivo | Qué contiene |
|---|---|
| `output/document_ai_report.md` | Informe humano con rutas, métricas, decisiones y límites. |
| `output/document_ai_report.json` | Informe estructurado para CI o revisión. |
| `output/extractions/*.json` | Extracciones por documento con campos, tablas, chunks y evidencias. |
| `output/table_cells.csv` | Celdas extraídas para inspeccionar estructura de tablas. |
| `output/document_pipeline.svg` | Figura del pipeline con firma del proyecto. |

## Qué deberías mirar

1. `decision`: si el documento pasa, requiere revisión o se bloquea.
2. `fields`: cada campo conserva `page`, `region_id`, `bbox`, confianza y error de caracteres.
3. `tables`: cada tabla conserva región, celdas, spans y validación numérica.
4. `chunks`: cada chunk mantiene página y región para ser citable en un RAG.
5. `review_hits`: cuándo el sistema debe pedir revisión humana.
6. `block_hits`: cuándo no se debe producir una respuesta operativa.
7. `metric`: qué métrica usarías para evaluar ese tipo de documento.

## Cambios útiles

- Cambia el total de `invoice_line_items_002` y comprueba que aparece una alerta numérica.
- Baja la confianza de una celda y explica si el documento debe pasar o revisarse.
- Quita el `bbox` de un campo obligatorio y observa cómo falla el gate.
- Añade una segunda página a `grant_policy_005` y decide qué chunk debería citarse.
- Añade una tabla con cabecera partida y comprueba si la estructura sigue siendo defendible.
- Cambia `untrusted_document_instruction` para ver por qué bloquear es el resultado correcto.

## Qué te llevas

Document AI no es “extraer texto del PDF”. Es convertir documentos en datos auditables. La unidad mínima no es una frase suelta: es campo, página, región, tabla, confianza, límite y decisión. Si una extracción no puede explicar de dónde sale, todavía no es una evidencia.

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `F12 C05 · Pipeline Document AI`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; este kit usa la biblioteca estándar de Python.
- `data/document_cases.json`: casos editables.
- `data/pages/*.svg`: páginas sintéticas para practicar extracción documental.
- `data/docs/*`: fuentes no visuales del caso guía.
- `contracts/document_ai_policy.json`: política de validación.
- `schemas/document_extraction_schema.json`: esquema de salida.
- `ops/run_document_ai_pipeline.py`: código ejecutable.
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

- `output/document_ai_report.md`: informe humano.
- `output/extractions/invoice_line_items_002.json`: extracción de factura defendible.
- `output/extractions/visual_instruction_doc_006.json`: bloqueo por instrucción no confiable.
- `output/table_cells.csv`: celdas para revisar estructura de tabla.
- `output/document_pipeline.svg`: figura del pipeline.

### Qué entregar

Una entrega útil debe incluir resultado de `make test`, una modificación razonada en `data/document_cases.json` o `contracts/document_ai_policy.json`, y una decisión técnica sobre si usar OCR/layout, extractor de facturas, parser de tablas, VLM, RAG multimodal o revisión humana.

La entrega buena defiende una decisión operativa: pasar, revisar, bloquear o pedir mejor documento. No basta con decir “el modelo extrajo texto”.

### Criterio de validación

El kit está completo cuando se puede descargar, extraer, ejecutar con `make run`, validar con `make test` y explicar sin depender de ninguna carpeta externa.
<!-- zip-quality-audit:end -->
