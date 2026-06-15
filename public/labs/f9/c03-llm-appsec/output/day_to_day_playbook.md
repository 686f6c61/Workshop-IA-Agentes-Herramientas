# Playbook diario para aplicaciones LLM con RAG y tools

Este playbook convierte los ejemplos del capítulo en trabajo de PR, CI, revisión de arquitectura y operación.

## PR que añade o cambia una tool

| Check | Evidencia esperada |
|---|---|
| Capability nombrada | Acción real que la tool permite realizar. |
| Effect declarado | `read`, `state_change`, `external_send`, `external_fetch` o equivalente. |
| Schema estricto | Campos requeridos, tipos, enums, límites y extras rechazados. |
| Scope requerido | Permisos que debe tener el rol antes de ejecutar. |
| Approval | Condición clara para `needs_approval`. |
| Egress | Dominios, métodos o destinos permitidos. |
| Idempotencia | Clave o mecanismo para evitar duplicados. |
| Traza | Campos que quedarán en logs operativos. |
| Test | Escenario en `data/scenarios.jsonl` que falla si se rompe el contrato. |

## Alta o cambio de documento RAG

| Check | Evidencia esperada |
|---|---|
| `doc_id` estable | Identificador usado en trazas y citas. |
| Owner | Equipo responsable de vigencia y retirada. |
| ACL | Roles o grupos que pueden recuperar el documento. |
| Finalidad | Usos permitidos del documento. |
| Vigencia | `valid_from`, `valid_to`, `status` y reemplazos. |
| Sensibilidad | Clasificación de datos y necesidad de redacción. |
| Test de retrieval | Escenario que demuestra que rol no autorizado no recupera el chunk. |

## Revisión de una respuesta problemática

| Pregunta | Campo que buscaría |
|---|---|
| ¿Qué política estaba activa? | `policy_version` |
| ¿Qué plantilla construyó el contexto? | `prompt_version` |
| ¿Qué documentos entraron? | `retrieved_docs` |
| ¿Qué documentos se bloquearon? | `blocked_docs` o decisión equivalente |
| ¿Qué tool propuso el modelo? | `tool_call` |
| ¿Qué decidió la aplicación? | `tool_decision` y `policy_decision` |
| ¿Hubo aprobación? | `approval_id` |
| ¿Qué validación falló? | `output_validation` |

## Gate mínimo antes de publicar

1. Ejecutar `python3 ops/run_appsec_gate.py --write`.
2. Revisar `output/appsec_gate_report.md`.
3. Corregir bloqueos no esperados.
4. Revisar `output/tool_contract_matrix.csv` con arquitectura.
5. Revisar `output/rag_retrieval_checks.md` con owner del corpus.
6. Revisar `output/market_tooling_review.md` antes de incorporar producto externo.
7. Guardar `output/trace_sample.jsonl` como contrato mínimo de observabilidad.

## Qué no dejaría como decisión del modelo

- Permisos de usuario.
- ACL de documentos.
- Destinos externos permitidos.
- Ejecución de acciones sensibles.
- Retención de trazas.
- Aprobación de cambios de estado.
- Selección de datos personales que pueden conservarse.
