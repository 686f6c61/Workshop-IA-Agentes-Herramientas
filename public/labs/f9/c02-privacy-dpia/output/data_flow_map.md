# Mapa de flujos de datos personales

Este mapa no sustituye una revisión legal. Sirve para que el equipo técnico vea qué dato entra, dónde se guarda, para qué finalidad se usa y qué evidencia debería existir.

| Flujo | Origen -> destino | Finalidad | Memoria | Retención | Banda | Owner |
|---|---|---|---|---:|---|---|
| `F-001` Prompt de consulta de alumnado | `web_chat` -> `llm_provider` | `responder_consulta` | `contexto_efimero` | 0 días | bajo | `platform_ai` |
| `F-002` Recuperación RAG de normativa | `vector_store` -> `llm_provider` | `recuperar_contexto` | `corpus_rag` | 365 días | medio | `rag_owner` |
| `F-003` Trazas operativas con texto bruto | `app_runtime` -> `observability_tool` | `depurar_servicio` | `traza_operativa` | 90 días | alto | `ops_owner` |
| `F-004` Memoria de preferencias | `app_runtime` -> `profile_store` | `recordar_preferencias` | `memoria_usuario` | 30 días | mínimo | `product_owner` |
| `F-005` Dataset de evaluación con tickets revisados | `support_tool` -> `eval_repository` | `evaluar_calidad` | `dataset_evaluacion` | 180 días | mínimo | `eval_owner` |
| `F-006` Intento de usar tickets para fine tuning | `support_tool` -> `training_pipeline` | `evaluar_calidad` | `entrenamiento` | 365 días | alto | `ml_owner` |
