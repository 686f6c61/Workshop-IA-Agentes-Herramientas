# Decisión final de gobernanza

Decisión: `publicar_con_condiciones`.

## Lectura ejecutiva

Se podría avanzar solo con condiciones fechadas, owners claros y repeticion del gate antes de ampliar alcance.

## Resumen

- Bloqueantes: 0.
- En revisión: 7.
- Revisiones de severidad alta: 6.
- Capas ausentes: ninguna.

## Sistemas

| Sistema | Fase | Pass | Revision | Bloqueo | Severidad maxima |
|---|---|---:|---:|---:|---:|
| Asistente académico con RAG | `production` | 3 | 2 | 0 | 4 |
| Ayuda de priorización para admisiones | `pilot` | 3 | 5 | 0 | 5 |
| Asistente interno de código | `production` | 4 | 0 | 0 | 3 |

## Bloqueantes

- No hay bloqueantes abiertos.

## Condiciones principales

- `academic_support_assistant` · `post_deployment_monitoring`: automatizar reporte mensual · 21 días · owner `owner-ops`.
- `admissions_prioritization_helper` · `dpia_retention_decision`: cerrar decisión formal de retención · 14 días · owner `owner-privacy`.
- `admissions_prioritization_helper` · `tool_and_rag_boundary`: probar escenarios de permisos en piloto · 14 días · owner `owner-platform`.
- `admissions_prioritization_helper` · `fria_precheck`: cerrar precheck con deployer · 21 días · owner `owner-governance`.
- `admissions_prioritization_helper` · `rollback_and_monitoring`: definir rollback y thresholds · 21 días · owner `owner-ops`.
- `admissions_prioritization_helper` · `least_agency_tool_boundary`: separar prepare de execute y limitar scopes por tool · 14 días · owner `owner-platform`.
- `academic_support_assistant` · `memory_ttl_and_source_integrity`: fijar TTL hash de origen y purga de memoria · 21 días · owner `owner-privacy`.

## Decisión profesional

La decisión se basa en evidencias por capa. Si cambia modelo, prompt, índice RAG, tools, finalidad, proveedor o fase, hay que repetir este gate.
