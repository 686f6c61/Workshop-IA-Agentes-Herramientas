# Decisión: ¿encaja aquí IA generativa?

La regla del capítulo 01 es sencilla: un LLM genera lenguaje; no sustituye cálculo exacto, fuentes, permisos ni responsabilidad.

| Caso | Recomendación | Componentes | Controles mínimos |
|---|---|---|---|
| Calcular ventas del último trimestre | `hybrid_system` | `sql_or_deterministic_code`, `tool_or_api`, `human_review` | `tests_with_known_answers`, `data_lineage`, `query_review`, `permission_boundary`, `dry_run`, `audit_log`, `named_reviewer`, `acceptance_criteria`, `decision_record` |
| Responder dudas sobre una política de becas | `hybrid_system` | `search_or_rag`, `llm_generation`, `tool_or_api` | `source_citations`, `freshness_date`, `retrieval_evaluation`, `structured_prompt`, `output_schema`, `sampling_policy`, `permission_boundary`, `dry_run`, `audit_log` |
| Redactar un correo de seguimiento | `llm_generation` | `llm_generation` | `structured_prompt`, `output_schema`, `sampling_policy` |
| Proponer y ejecutar un reembolso | `hybrid_system` | `sql_or_deterministic_code`, `search_or_rag`, `llm_generation`, `tool_or_api`, `human_review` | `tests_with_known_answers`, `data_lineage`, `query_review`, `source_citations`, `freshness_date`, `retrieval_evaluation`, `structured_prompt`, `output_schema`, `sampling_policy`, `permission_boundary`, `dry_run`, `audit_log`, `named_reviewer`, `acceptance_criteria`, `decision_record` |
| Resumir una incidencia de producción | `hybrid_system` | `search_or_rag`, `llm_generation`, `tool_or_api`, `human_review` | `source_citations`, `freshness_date`, `retrieval_evaluation`, `structured_prompt`, `output_schema`, `sampling_policy`, `permission_boundary`, `dry_run`, `audit_log`, `named_reviewer`, `acceptance_criteria`, `decision_record` |

## Lectura técnica

### Calcular ventas del último trimestre

Por qué: hay que calcular o consultar un dato exacto; hace falta leer estado real o actuar sobre un sistema; el impacto o la acción externa exige una persona responsable.
Decisión: no publiques automatización directa; exige revisión humana trazable.

### Responder dudas sobre una política de becas

Por qué: la respuesta debe apoyarse en fuentes recuperables; hay que redactar, resumir o transformar lenguaje; hace falta leer estado real o actuar sobre un sistema.
Decisión: se puede automatizar con los controles indicados y pruebas pequeñas.

### Redactar un correo de seguimiento

Por qué: hay que redactar, resumir o transformar lenguaje.
Decisión: se puede automatizar con los controles indicados y pruebas pequeñas.

### Proponer y ejecutar un reembolso

Por qué: hay que calcular o consultar un dato exacto; la respuesta debe apoyarse en fuentes recuperables; hay que redactar, resumir o transformar lenguaje; hace falta leer estado real o actuar sobre un sistema; el impacto o la acción externa exige una persona responsable.
Decisión: no publiques automatización directa; exige revisión humana trazable.

### Resumir una incidencia de producción

Por qué: la respuesta debe apoyarse en fuentes recuperables; hay que redactar, resumir o transformar lenguaje; hace falta leer estado real o actuar sobre un sistema; el impacto o la acción externa exige una persona responsable.
Decisión: no publiques automatización directa; exige revisión humana trazable.

