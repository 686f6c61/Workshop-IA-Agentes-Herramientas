# Decisión simbólica

Decisión: `conceder_acceso_temporal`.

| Comprobación | Resultado |
|---|---|
| `rol_requerido` | sí |
| `aprobacion_del_equipo` | sí |
| `acceso_temporal_permitido` | sí |

## Plan trazable

- `resolver_entidades(ticket:t1)`
- `consultar_grafo(persona:ana, recurso:facturas)`
- `validar_rol(rol:finanzas)`
- `validar_aprobacion(persona:luis)`
- `conceder_acceso_temporal(persona:ana, recurso:facturas)`
- `registrar_traza(ticket:t1)`

## Lectura técnica

El modelo podría ayudar a leer el ticket, pero la acción se decide con hechos y precondiciones. Esa separación permite explicar y depurar el resultado.
