# Solución de referencia · F12 C12

## Lectura del baseline

El baseline no debe publicarse como release completo. La decisión global es `block_release` porque hay dos bloqueos:

- `policy_rag_with_internal_slides`: mezcla RAG multimodal con fuentes internas y riesgo de secreto. Le faltan ACL de fuente, policy decision, artifact lineage y respuesta completa ante secreto.
- `computer_use_claim_submission`: intenta una acción externa con captura, PII, secreto y contenido no confiable. Sin approval card y egress policy, no debería ejecutar nada.

Hay casos que sí pueden pasar (`catalog_alt_text`, `visual_search_catalog`), pero eso no salva el release completo. Un release no se evalúa solo por sus mejores rutas.

## Lectura de la remediación

La remediación mejora el sistema:

- se añaden evidencias de tablas en Document AI;
- se añade ACL, policy decision y lineage en RAG;
- se baja latencia en voz;
- se añade aprobación, egress y redacción en computer use;
- se mejora el helpdesk multimodal con evidencias de retrieval, voz y privacidad.

La decisión global pasa a `review_release`, no a `ship`, porque `parking_video_event_triage` sigue en revisión. La razón es buena para aprender: aunque el riesgo baja y hay más evidencias, todavía falta `policy_decision` y la calidad temporal queda justo por debajo del umbral de publicación.

## Decisión recomendada

Publicaría solo los casos `pass` y dejaría `parking_video_event_triage` fuera del release hasta cerrar:

1. `policy_decision` explícita para tratamiento de vídeo.
2. Evaluación temporal más fuerte.
3. Prueba de redacción por región en frames.
4. Owner de operación que acepte latencia/coste.

## Lectura del release candidate

El parche `candidate_patch.parking_video_event_triage.v1` convierte el caso de vídeo en candidato publicable porque no solo sube una métrica. Añade evidencia y control operativo:

1. Registra `policy_decision`.
2. Añade `frame_region_redaction_eval`.
3. Sustituye la evaluación temporal básica por `temporal_eval_v2`.
4. Define owner, aprobadores y rollback.
5. Baja failure rate y mantiene latencia/coste dentro del SLO.

Con ese parche, la decisión global pasa a `ship`. Aun así, en una revisión real no lo aprobaría sin leer `output/release_change_request.md`, `output/sli_slo_matrix.csv`, `output/contract_validation_report.md` y `output/version_manifest.json`.

La frase que debería aparecer en una entrega fuerte:

> Aceptaría el release candidate porque ya no queda evidencia faltante, los SLI/SLO pasan, los contract tests separan casos válidos de casos incompletos y hay owner, aprobadores y rollback. Repetiría la regresión si cambia el modelo de vídeo, el muestreo de frames, la redacción, el prompt, el índice, la policy o el criterio de eventos.

## Por qué esta solución es defendible

La decisión usa el facsímil completo:

- C01-C04: contratos y modelos visión-lenguaje.
- C05: Document AI y referencias de página.
- C06: RAG multimodal, ACL y grounding.
- C07: turnos de voz y latencia.
- C08: vídeo y evaluación temporal.
- C09: computer use y aprobación.
- C10: evaluación y slices.
- C11: privacidad, policy, lineage y runbook.

La idea final: una práctica multimodal seria no termina en “el modelo respondió bien”. Termina en una decisión reproducible que otra persona pueda auditar.
