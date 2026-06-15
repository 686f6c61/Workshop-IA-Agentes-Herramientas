# Revision Zero Trust de agentes

Esta revisión convierte el principio de menor capacidad de actuación en preguntas verificables. Un agente no debería recibir identidad, credenciales, memoria o tools por comodidad: cada capacidad tiene que tener alcance, evidencia y una prueba.

- Controles revisados: 4.
- Controles abiertos: 3.

## Matriz resumida

| Sistema | Requisito | Estado | Identidad | Credencial | Tools | Memoria | Prueba de ingeniería |
|---|---|---|---|---|---|---|---|
| `admissions_prioritization_helper` | `agent_identity_and_short_lived_credentials` | `review` | agent_id único por sistema y entorno | token corto con scopes de lectura y preparación | sin tools de escritura directa | sin memoria compartida entre sesiones | revisar TTL, rotación, owner y traza de uso de credencial |
| `admissions_prioritization_helper` | `least_agency_tool_boundary` | `review` | identidad de agente separada de usuario y servicio | solo scopes necesarios para prepare, no execute | allowlist de tools y validación de parámetros | memoria de tarea con fuente trazable | probar que una tool no autorizada no aparece ni se ejecuta |
| `academic_support_assistant` | `memory_ttl_and_source_integrity` | `review` | usuario, sesion y agente separados | sin permisos extra por usar memoria | RAG con ACL antes de similitud | TTL, hash de origen, purga y atribucion de fuente | crear muestra before/after de purga y verificar hashes |
| `internal_coding_helper` | `repo_scoped_agent_identity` | `pass` | agent_id por repo, rama y entorno | scopes por repositorio | tools limitadas a repo permitido | sin memoria cruzada entre repositorios | intentar leer repo no permitido y comprobar bloqueo |

## Lectura profesional

- `admissions_prioritization_helper` mantiene abierto `agent_identity_and_short_lived_credentials`. Owner `owner-platform` debe aportar `evidence/agent_identity_policy.yaml` y ejecutar: asignar agent_id y credenciales de corta duración.
- `admissions_prioritization_helper` mantiene abierto `least_agency_tool_boundary`. Owner `owner-platform` debe aportar `evidence/tool_boundary_contract.yaml` y ejecutar: separar prepare de execute y limitar scopes por tool.
- `academic_support_assistant` mantiene abierto `memory_ttl_and_source_integrity`. Owner `owner-privacy` debe aportar `evidence/memory_retention_policy.md` y ejecutar: fijar TTL hash de origen y purga de memoria.

## Criterio de cierre

Un control de agente se cierra cuando la capacidad queda reducida en runtime y existe evidencia reproducible. No basta con documentar la intencion: debe verse en policy-as-code, contrato de tool, TTL de credencial, traza y salida del gate.
