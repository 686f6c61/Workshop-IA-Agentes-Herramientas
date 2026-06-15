# Registro de riesgos: Asistente académico con RAG y revisión humana

## Lectura ejecutiva

- Sistema: `academic-assistant-rag-v1`.
- Fase: `canary`.
- Decisión: `publicar_con_condiciones`.
- Escenarios críticos: 0.
- Escenarios altos: 3.

## Fórmula usada

`riesgo = probabilidad x impacto x exposición x hueco_de_detección`

Cada factor usa escala 1-5. El hueco de detección mide lo difícil que sería ver el problema a tiempo.

## Escenarios priorizados

| ID | Área | Banda | Score | Owner | Controles recomendados | Evidencia |
|---|---|---:|---:|---|---|---|
| R-004 | modelo | alto | 192 | owner-eval | model_card, limites_de_uso, fallback | citation_eval, abstention_cases |
| R-002 | datos | alto | 180 | owner-privacy | minimizacion, retencion_limitada, dataset_card | retention_policy, privacy_review |
| R-005 | observabilidad | alto | 180 | owner-observability | span_modelo, metricas_coste, muestreo_revisable | trace_sample, release_manifest |
| R-003 | tools | medio | 160 | owner-platform | permisos_minimos, aprobacion_humana, idempotencia | approval_policy, tool_trace_sample |
| R-001 | rag | medio | 144 | owner-rag | citas_obligatorias, abstencion_sin_evidencia | rag_eval_report, index_manifest |
| R-006 | gobernanza | medio | 144 | owner-governance | decision_escrita, revision_periodica, paquete_evidencias | risk_acceptance_record, review_calendar |
| R-008 | rag | medio | 144 | owner-rag | versionado_indice, abstencion_sin_evidencia, eval_retrieval | source_quality_policy, retrieval_trace |
| R-007 | datos | bajo | 72 | owner-data | minimizacion, seudonimizacion, retencion_limitada | dataset_card, split_manifest |

## Bloqueos y condiciones

- No hay bloqueos absolutos según la política actual.

## Siguiente revisión

Revisar owners, evidencias y controles antes de subir de fase. Si cambia el corpus, el modelo, las tools o la finalidad, volver a ejecutar este kit.
