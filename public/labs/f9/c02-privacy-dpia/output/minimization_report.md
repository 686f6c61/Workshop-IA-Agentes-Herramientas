# Informe de minimización

Minimizar no significa borrar al azar. Significa conservar solo los campos necesarios para la finalidad declarada, transformar lo que pueda exponerse menos y justificar lo que deba permanecer.

| Flujo | Campos permitidos | Revisar o transformar | Ratio |
|---|---|---|---:|
| `F-001` | question_text, course_code, language, consent_flag | sin cambios principales | 1.0 |
| `F-002` | document_id, chunk_id, chunk_text, source_url, access_group | version:justificar_o_eliminar | 0.833 |
| `F-003` | trace_id, timestamp, model_id, latency_ms, token_count | question_text:redactar_o_sustituir_por_hash, email:redactar_o_sustituir_por_hash, phone:redactar_o_sustituir_por_hash | 0.625 |
| `F-004` | user_id_hash, language, accessibility_preference, consent_flag, expires_at | sin cambios principales | 1.0 |
| `F-005` | case_id, expected_answer, model_answer, rubric, source_document, reviewer_id | sin cambios principales | 1.0 |
| `F-006` | case_id | question_text:redactar_o_sustituir_por_hash, answer_text:redactar_o_sustituir_por_hash, email:redactar_o_sustituir_por_hash, student_status:justificar_o_eliminar | 0.2 |

## Criterio de aceptación

- Cualquier campo fuera de la allowlist debe eliminarse, redactarse, agregarse o justificarse.
- Si un campo aparece solo para depuración, debe tener TTL, owner y muestra de traza revisada.
- La memoria de usuario necesita consentimiento, fecha de expiración y ruta de borrado.
