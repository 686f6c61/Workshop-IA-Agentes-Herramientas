# Reporte de contrato multimodal: f12-c01-modality-contract-v1

Owner: `equipo-aprendizaje-ia`
Casos revisados: 5
Gate valido: `True`

## Decision de ingenieria

- Regla base: usar la modalidad minima que aporte evidencia nueva medible.
- Evitar: no convertir una tarea textual en multimodal solo porque el proveedor acepte imagenes o audio.
- Medir antes de publicar: schema_pass_rate, evidence_coverage, cost_per_valid_answer, latency_p95, manual_review_rate.

## Casos

### support-screenshot-001: Incidencia de soporte con captura de pantalla

- Modalidades disponibles: image, text.
- Modalidad minima declarada: text, image.
- Arquitectura candidata: `vlm_plus_rules`.
- Arquitectura recomendada por el gate: `vlm_or_multimodal_embedding_retrieval`.
- Campos obligatorios: categoria, evidencia_visual, accion_recomendada, confidence.
- Evidencia requerida: texto_del_ticket, region_visual_relevante, mensaje_de_error.
- Metricas: schema_pass_rate, visual_evidence_accuracy, resolution_rate.
- Riesgo acumulado: 6.
- Impuesto multimodal: complejidad=2, latencia=2, privacidad=6, evaluacion=3.
- Revision humana: required_when_confidence_below_0_75_or_personal_data_visible.
- Issues: sin issues bloqueantes.

### invoice-pdf-002: Extraccion de factura en PDF

- Modalidades disponibles: document, text.
- Modalidad minima declarada: document, text.
- Arquitectura candidata: `ocr_layout_plus_llm`.
- Arquitectura recomendada por el gate: `ocr_layout_plus_llm_or_multimodal_rag`.
- Campos obligatorios: proveedor, fecha, total, impuestos, evidencia_por_campo.
- Evidencia requerida: pagina, bbox_or_line_reference, valor_extraido.
- Metricas: field_f1, evidence_coverage, manual_review_rate.
- Riesgo acumulado: 7.
- Impuesto multimodal: complejidad=2, latencia=2, privacidad=7, evaluacion=3.
- Revision humana: required_for_total_mismatch_or_missing_evidence.
- Issues: sin issues bloqueantes.

### catalog-search-003: Busqueda de producto por texto e imagen

- Modalidades disponibles: image, text.
- Modalidad minima declarada: text, image.
- Arquitectura candidata: `multimodal_embedding_retrieval`.
- Arquitectura recomendada por el gate: `vlm_or_multimodal_embedding_retrieval`.
- Campos obligatorios: product_id, score, matching_attributes, reason.
- Evidencia requerida: atributos_visuales, metadatos_de_producto, ranking_score.
- Metricas: recall_at_5, precision_at_5, attribute_match_rate.
- Riesgo acumulado: 4.
- Impuesto multimodal: complejidad=2, latencia=2, privacidad=4, evaluacion=3.
- Revision humana: sampled_review_for_top_5_results.
- Issues: sin issues bloqueantes.

### meeting-audio-004: Resumen de reunion con audio

- Modalidades disponibles: audio, text.
- Modalidad minima declarada: audio, text.
- Arquitectura candidata: `asr_plus_llm_with_review`.
- Arquitectura recomendada por el gate: `asr_plus_llm_with_timestamps`.
- Campos obligatorios: resumen, acuerdos, tareas, dudas.
- Evidencia requerida: timestamp, speaker_if_available, transcript_span.
- Metricas: wer, action_item_precision, timestamp_coverage.
- Riesgo acumulado: 8.
- Impuesto multimodal: complejidad=2, latencia=3, privacidad=8, evaluacion=3.
- Revision humana: required_before_sending_minutes.
- Issues: sin issues bloqueantes.

### grant-workflow-005: Solicitud de beca bloqueada con captura, PDF y politica interna

- Modalidades disponibles: document, image, table, text.
- Modalidad minima declarada: text, image, document, table.
- Arquitectura candidata: `ocr_layout_plus_llm_or_multimodal_rag_with_vlm_triage`.
- Arquitectura recomendada por el gate: `ocr_layout_plus_llm_or_multimodal_rag`.
- Campos obligatorios: causa_probable, evidencia_visual, evidencia_documental, estado_operativo, siguiente_paso, requiere_revision_humana.
- Evidencia requerida: region_visual_relevante, pagina_o_clausula, fila_de_estado, texto_del_ticket.
- Metricas: evidence_coverage, field_accuracy, resolution_rate, manual_review_precision.
- Riesgo acumulado: 12.
- Impuesto multimodal: complejidad=4, latencia=3, privacidad=12, evaluacion=6.
- Revision humana: required_when_policy_conflict_or_missing_evidence_or_personal_data_visible.
- Issues: sin issues bloqueantes.

## Casos que necesitan mas cuidado

Estos casos no estan prohibidos, pero deben llevar minimizacion, evidencias y revision antes de publicarse:

- `support-screenshot-001`
- `invoice-pdf-002`
- `meeting-audio-004`
- `grant-workflow-005`
