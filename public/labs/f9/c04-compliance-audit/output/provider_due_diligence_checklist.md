# Due diligence técnica de terceros

Este informe revisa proveedores que pueden ver datos, cambiar comportamiento, afectar disponibilidad o modificar una decisión operativa.

| Sistema | Proveedor | Capa | Región | Datos enviados | Estado | Hueco principal |
|---|---|---|---|---|---|---|
| Asistente académico con RAG | Hosted LLM API | `model_api` | `eu-west` | `question_text_redacted;retrieved_chunks` | `partial` | falta confirmar retención exacta en contrato final |
| Asistente académico con RAG | Managed Vector DB | `vector_database` | `eu-west` | `embeddings;chunk_metadata` | `accepted` | sin hueco principal |
| Asistente académico con RAG | LLM Observability | `observability` | `eu-west` | `trace_metadata_no_raw_text` | `accepted` | sin hueco principal |
| Ayuda de priorización para admisiones | Hosted LLM API | `model_api` | `eu-west` | `case_features_redacted;ranking_context` | `partial` | plan de salida; falta plan de salida y prueba de export |
| Ayuda de priorización para admisiones | Managed Vector DB | `vector_database` | `eu-west` | `embeddings;academic_metadata` | `partial` | plan de salida; falta tombstone y restore test |
| Asistente interno de código | Local Inference Server | `local_model_runtime` | `on_prem` | `repository_metadata_no_secrets` | `accepted` | sin hueco principal |

## Checklist que debería cerrar el equipo

- Confirmar región efectiva del servicio y si hay cambios por fallback.
- Confirmar si el proveedor conserva prompts, salidas, documentos, embeddings o solo metadatos.
- Revisar DPA, subprocesadores, periodo de retención, soporte y contacto operativo.
- Probar plan de salida: export, borrado, reindexado y sustitución de proveedor.
- Registrar cómo se notifican cambios de modelo, API, runtime o contrato.
- Conectar cada proveedor con `technical_file`, `data_flow`, `recordkeeping_schema` y `change_control_record`.
