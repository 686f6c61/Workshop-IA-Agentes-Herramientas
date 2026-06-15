# Decisión C02: Contrato de runtime

Estado: `valid`.

## Evidencias

- OK: estados explícitos. La run no vive como string libre.
- OK: idempotencia. Los retries no duplican efectos.
- OK: DLQ. Hay lugar para mensajes no procesables.
- OK: edad máxima de cola. La cola no es memoria eterna.

## Decisión

El runtime se puede implementar y probar: estados, cola, retries, idempotencia y error quedan explícitos.
