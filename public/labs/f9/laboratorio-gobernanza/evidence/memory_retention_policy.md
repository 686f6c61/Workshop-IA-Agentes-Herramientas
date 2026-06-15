# Politica de memoria y retención

## Alcance

Esta política cubre memoria de sesion, memoria persistente y contexto recuperado para los sistemas del laboratorio de gobernanza.

## Reglas por sistema

| Sistema | Tipo de memoria | TTL | Aislamiento | Evidencia de cierre |
|---|---|---:|---|---|
| `academic_support_assistant` | memoria de sesion y resumen operativo | 8 horas | usuario + sesion + agente | prueba de purga, hash de origen y muestra de traza sin texto completo |
| `admissions_prioritization_helper` | memoria de tarea durante piloto | 4 horas | caso + revisor + agente | prueba de no cruce entre expedientes y purga al cerrar revisión |
| `internal_coding_helper` | memoria por repositorio | 24 horas | repositorio + rama + agente | prueba de no lectura entre repositorios |

## Campos mínimos en una traza

```json
{
  "memory_store_id": "session:academic_support:2026-06-07:hash",
  "memory_type": "session_summary",
  "source_hash": "sha256:...",
  "ttl_until": "2026-06-07T20:00:00Z",
  "agent_id": "academic_support_assistant.agent.rag",
  "personal_data_stored": false,
  "purge_event_id": "purge_001"
}
```

## Criterio de cierre

El control no se cierra por decir que la memoria es temporal. Se cierra cuando existe una prueba que muestra creacion, uso, TTL, purga y ausencia de cruce entre usuarios, expedientes o repositorios.
