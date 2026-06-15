# Decisiones de policy-as-code

Este informe simula las mismas reglas que aparecen como ejemplos en `policies/egress_policy.rego` y `policies/egress_policy.cedar`.
No sustituye a OPA ni Cedar en producción: sirve para entender el input que debe recibir una policy real y qué evidencia conviene guardar.

| Decisión | Acción | Destino | Riesgo | Resultado | Razones |
|---|---|---|---:|---|---|
| `allow_redacted_support_trace` | `SendArtifact` | `internal_support_tool` | 0.32 | `allow` | none |
| `review_eval_fixture_with_missing_redaction` | `StoreEvalFixture` | `internal_eval_store` | 0.51 | `review` | missing_controls, risk_above_review_threshold |
| `deny_public_webhook` | `SendArtifact` | `public_webhook` | 0.76 | `deny` | blocked_destination, external_action_requires_approval, missing_controls, risk_above_review_threshold |
| `deny_secret_visible` | `CreateSecurityTicket` | `security_ticket` | 0.72 | `deny` | unredacted_secret, risk_above_review_threshold |

## Lectura

- La aplicación no pregunta al modelo si puede enviar una captura: evalúa una política externa.
- `deny` bloquea destino, secreto o acción externa sin aprobación.
- `review` mantiene el flujo humano cuando el riesgo o los controles faltantes superan el umbral.
- `allow` solo aparece con destino aprobado, riesgo bajo y controles completos.
