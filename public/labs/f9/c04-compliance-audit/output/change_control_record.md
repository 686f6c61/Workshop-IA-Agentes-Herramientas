# Registro de control de cambios

Cada cambio siguiente puede alterar clasificación, evidencias o gate. Debe registrarse antes de publicar.

| Cambio | Por qué importa | Evidencia que debe reabrirse |
|---|---|---|
| Nuevo modelo o proveedor | Cambia comportamiento, región, contrato, logs y límites. | technical file, evals, privacidad, manifest. |
| Nuevo prompt de sistema | Cambia instrucciones, formato, límites y decisiones de tool. | prompt diff, regresiones, appsec gate. |
| Nuevo índice RAG | Cambia conocimiento recuperado, ACL y vigencia documental. | linaje, retrieval checks, trace sample. |
| Nueva tool con efecto real | Cambia permisos, aprobación, trazas y operación. | tool contract, RACI, approval gate. |
| Cambio de finalidad | Puede cambiar categoría AI Act y DPIA. | clasificación, alcance AIMS, risk register. |
| Paso de piloto a producción | Cambia exposición, SLO, soporte y seguimiento. | audit gate, monitoring plan, operator manual. |

## Aplicación a los sistemas del kit

- `academic_support_assistant`: reabrir gate si cambian `provider-model@2026-06-07`, `academic-prompt@0.4.2`, `normativa-academica@2026.1` o `ticket-tools@0.3.0`.
- `admissions_prioritization_helper`: reabrir gate si cambian `provider-model@2026-06-07`, `admissions-prompt@0.2.0`, `admissions-index@2026.1` o `admissions-tools@0.1.0`.
- `internal_coding_helper`: reabrir gate si cambian `provider-code-model@2026-06-07`, `coding-prompt@1.1.0`, `engineering-docs@2026.2` o `repo-tools@0.5.1`.
