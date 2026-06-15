# AI-BOM operativo

Este AI-BOM no es un inventario decorativo. Sirve para saber qué piezas vivas pueden cambiar el comportamiento de cada sistema de IA: modelo, prompt, RAG, tools, terceros, memoria, políticas y evidencias.

- Fecha de corte: `2026-06-07`.
- Politica: `f9c04-compliance-policy@0.1.0`.

## Asistente académico con RAG

| Pieza | Valor vivo | Por que importa |
|---|---|---|
| `system_id` | `academic_support_assistant` | Une evidencias, logs, owners y decisión. |
| Modelo | `provider-model@2026-06-07` | Cambiarlo exige repetir evals, privacidad y gate si afecta salida. |
| Prompt | `academic-prompt@0.4.2` | Cambia instrucciones, formato, criterios y límites. |
| RAG | `normativa-academica@2026.1` | Cambia documentos recuperados, ACL, citas y vigencia. |
| Tools | `ticket-tools@0.3.0` | Cambia acciones posibles, scopes, aprobaciones y trazas. |
| Terceros | Hosted LLM API; Managed Vector DB; LLM Observability | Pueden afectar datos, disponibilidad, contrato, region y salida. |
| Datos personales | `true` | Conecta con minimizacion, DPIA/EIPD, retención y derechos. |
| Decisión de gate | `publicar_con_condiciones` | Explica si puede avanzar, queda condicionado o debe revisarse antes. |

### Checklist Zero Trust para agentes

| Control | Pregunta de revisión | Evidencia esperada |
|---|---|---|
| Identidad | ¿El agente tiene identidad técnica propia por sistema y entorno? | `agent_id`, owner, entorno y traza. |
| Credenciales | ¿La credencial caduca y tiene scopes limitados? | TTL, scopes, rotacion y registro de uso. |
| Tools | ¿Solo ve tools necesarias para está finalidad? | allowlist, contrato de parámetros y approval si hay efecto real. |
| Memoria | ¿La memoria tiene TTL, origen, hash y aislamiento? | política de memoria, purga y prueba de no cruce. |
| Configuración | ¿La política activa está versionada y hasheada? | manifest, hash, PR o cambio aprobado. |
| Reversibilidad | ¿Se puede revocar credencial, apagar tool o volver a versión anterior? | rollback probado y runbook. |

## Ayuda de priorización para admisiones

| Pieza | Valor vivo | Por que importa |
|---|---|---|
| `system_id` | `admissions_prioritization_helper` | Une evidencias, logs, owners y decisión. |
| Modelo | `provider-model@2026-06-07` | Cambiarlo exige repetir evals, privacidad y gate si afecta salida. |
| Prompt | `admissions-prompt@0.2.0` | Cambia instrucciones, formato, criterios y límites. |
| RAG | `admissions-index@2026.1` | Cambia documentos recuperados, ACL, citas y vigencia. |
| Tools | `admissions-tools@0.1.0` | Cambia acciones posibles, scopes, aprobaciones y trazas. |
| Terceros | Hosted LLM API; Managed Vector DB | Pueden afectar datos, disponibilidad, contrato, region y salida. |
| Datos personales | `true` | Conecta con minimizacion, DPIA/EIPD, retención y derechos. |
| Decisión de gate | `revisar_antes` | Explica si puede avanzar, queda condicionado o debe revisarse antes. |

### Checklist Zero Trust para agentes

| Control | Pregunta de revisión | Evidencia esperada |
|---|---|---|
| Identidad | ¿El agente tiene identidad técnica propia por sistema y entorno? | `agent_id`, owner, entorno y traza. |
| Credenciales | ¿La credencial caduca y tiene scopes limitados? | TTL, scopes, rotacion y registro de uso. |
| Tools | ¿Solo ve tools necesarias para está finalidad? | allowlist, contrato de parámetros y approval si hay efecto real. |
| Memoria | ¿La memoria tiene TTL, origen, hash y aislamiento? | política de memoria, purga y prueba de no cruce. |
| Configuración | ¿La política activa está versionada y hasheada? | manifest, hash, PR o cambio aprobado. |
| Reversibilidad | ¿Se puede revocar credencial, apagar tool o volver a versión anterior? | rollback probado y runbook. |

## Asistente interno de código

| Pieza | Valor vivo | Por que importa |
|---|---|---|
| `system_id` | `internal_coding_helper` | Une evidencias, logs, owners y decisión. |
| Modelo | `provider-code-model@2026-06-07` | Cambiarlo exige repetir evals, privacidad y gate si afecta salida. |
| Prompt | `coding-prompt@1.1.0` | Cambia instrucciones, formato, criterios y límites. |
| RAG | `engineering-docs@2026.2` | Cambia documentos recuperados, ACL, citas y vigencia. |
| Tools | `repo-tools@0.5.1` | Cambia acciones posibles, scopes, aprobaciones y trazas. |
| Terceros | Local Inference Server | Pueden afectar datos, disponibilidad, contrato, region y salida. |
| Datos personales | `false` | Conecta con minimizacion, DPIA/EIPD, retención y derechos. |
| Decisión de gate | `publicar_con_seguimiento` | Explica si puede avanzar, queda condicionado o debe revisarse antes. |

### Checklist Zero Trust para agentes

| Control | Pregunta de revisión | Evidencia esperada |
|---|---|---|
| Identidad | ¿El agente tiene identidad técnica propia por sistema y entorno? | `agent_id`, owner, entorno y traza. |
| Credenciales | ¿La credencial caduca y tiene scopes limitados? | TTL, scopes, rotacion y registro de uso. |
| Tools | ¿Solo ve tools necesarias para está finalidad? | allowlist, contrato de parámetros y approval si hay efecto real. |
| Memoria | ¿La memoria tiene TTL, origen, hash y aislamiento? | política de memoria, purga y prueba de no cruce. |
| Configuración | ¿La política activa está versionada y hasheada? | manifest, hash, PR o cambio aprobado. |
| Reversibilidad | ¿Se puede revocar credencial, apagar tool o volver a versión anterior? | rollback probado y runbook. |
