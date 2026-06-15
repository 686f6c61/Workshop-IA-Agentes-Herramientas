# Índice de evidencias: Asistente académico con RAG y revisión humana

Este índice no demuestra cumplimiento legal por sí solo. Sirve para que ingeniería, privacidad, producto y operación sepan qué mirar antes de cambiar de fase.

## Decisión

- Fase revisada: `canary`.
- Decisión: `publicar_con_condiciones`.
- Escenarios altos: 3.

## Marcos y artefactos

| Marco o función | Artefactos que debe enseñar el equipo |
|---|---|
| `nist_ai_rmf_govern` | `owner`, `decision_escrita`, `paquete_evidencias` |
| `nist_ai_rmf_map` | `inventario_sistema`, `contexto_uso`, `limites_sistema` |
| `nist_ai_rmf_measure` | `risk_register`, `eval_regresion`, `trace_sample` |
| `nist_ai_rmf_manage` | `control_matrix`, `release_gate`, `revision_periodica` |
| `iso_42001` | `politica_ia`, `raci_operativo`, `mejora_continua` |
| `ai_act` | `clasificacion_uso`, `documentacion_tecnica`, `monitorizacion_post_release` |
| `gdpr` | `privacy_review`, `retencion_limitada`, `minimizacion` |
| `owasp_llm` | `permisos_minimos`, `validacion_salida`, `control_contexto_tools` |

## Evidencias por escenario alto

| ID | Owner | Evidencias mínimas |
|---|---|---|
| `R-004` | `owner-eval` | `citation_eval`, `abstention_cases` |
| `R-002` | `owner-privacy` | `retention_policy`, `privacy_review` |
| `R-005` | `owner-observability` | `trace_sample`, `release_manifest` |

## Huecos que no aceptaría sin explicación

- Un escenario alto sin owner.
- Un control declarado sin evidencia ejecutable o revisable.
- Una tool con efecto externo sin traza de aprobación.
- Un RAG sin manifest de índice y sin casos de abstención.
- Logs o memoria sin política de retención.
