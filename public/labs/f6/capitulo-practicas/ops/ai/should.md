# SHOULD: comportamiento verificable

## MUST

- Toda run debe tener `run_id`, `trace_id`, `release_id` y `idempotency_key`.
- Toda salida externa debe validar contrato antes de publicarse.
- Todo cambio debe tener rollback conocido.
- Toda incidencia debe producir caso de regresión si descubre un fallo nuevo.

## SHOULD

- La respuesta debería citar evidencia cuando use RAG.
- El router debería elegir la ruta más barata que cumpla contrato.
- La observabilidad debería evitar guardar payloads sensibles completos.

## MAY

- El sistema puede degradar a modo solo lectura.
- El sistema puede pedir revisión humana si falta evidencia.
