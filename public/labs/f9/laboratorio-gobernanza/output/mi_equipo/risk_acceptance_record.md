# Registro de aceptación de riesgo residual

Este registro solo aplica a condiciones que no bloquean. Un bloqueo no se acepta: se cierra o se mantiene la decisión `revisar_antes`.

| Sistema | Requisito | Severidad | Owner que debe aceptar | Condición |
|---|---|---:|---|---|
| `academic_support_assistant` | `post_deployment_monitoring` | 3 | `owner-ops` | automatizar reporte mensual |
| `admissions_prioritization_helper` | `dpia_retention_decision` | 5 | `owner-privacy` | cerrar decisión formal de retención |
| `admissions_prioritization_helper` | `tool_and_rag_boundary` | 4 | `owner-platform` | probar escenarios de permisos en piloto |
| `admissions_prioritization_helper` | `fria_precheck` | 4 | `owner-governance` | cerrar precheck con deployer |
| `admissions_prioritization_helper` | `rollback_and_monitoring` | 4 | `owner-ops` | definir rollback y thresholds |
| `admissions_prioritization_helper` | `least_agency_tool_boundary` | 5 | `owner-platform` | separar prepare de execute y limitar scopes por tool |
| `academic_support_assistant` | `memory_ttl_and_source_integrity` | 4 | `owner-privacy` | fijar TTL hash de origen y purga de memoria |
