# Gate de salida: Asistente académico con RAG y revisión humana

Decisión: `publicar_con_condiciones`

## Condiciones obligatorias

- `R-002` (alto): owner `owner-privacy`, controles `minimizacion, retencion_limitada, dataset_card`, evidencia `retention_policy, privacy_review`.
- `R-004` (alto): owner `owner-eval`, controles `model_card, limites_de_uso, fallback`, evidencia `citation_eval, abstention_cases`.
- `R-005` (alto): owner `owner-observability`, controles `span_modelo, metricas_coste, muestreo_revisable`, evidencia `trace_sample, release_manifest`.

## Criterio de aceptación

Una versión puede avanzar si no quedan escenarios críticos abiertos, todo escenario alto tiene owner y cada condición tiene evidencia revisable.

## Cómo explicarlo

No estamos buscando certeza absoluta. Estamos dejando claro qué puede salir mal, quién lo mira, qué control lo reduce y qué prueba demuestra que no estamos improvisando.
