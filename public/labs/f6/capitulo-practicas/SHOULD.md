# SHOULD.md verificable

Este documento separa obligaciones, expectativas y comportamientos opcionales para que el equipo no confunda una buena intención con un contrato operativo.

## MUST

- Toda run debe tener `run_id`, `trace_id`, `release_id` e `idempotency_key`.
- Toda salida externa debe validar contrato antes de publicarse.
- Todo cambio debe tener rollback conocido.
- Toda incidencia debe producir caso de regresión si descubre un fallo nuevo.

## SHOULD

- La respuesta debería citar evidencia cuando use RAG.
- El router debería elegir la ruta más barata que cumpla contrato.
- La observabilidad debería evitar guardar payloads sensibles completos.
- El gate debería explicar qué métrica bloquea una release.

## MAY

- El sistema puede degradar a modo solo lectura.
- El sistema puede pedir revisión humana si falta evidencia.
- El sistema puede aplazar una acción si el presupuesto de error está consumido.

## Cómo se valida

```bash
python3 ops/run_f6_practices.py --chapter c01 --write --fail-on-invalid
cat output/c01_decision.md
python3 -m json.tool output/c01_report.json
```

La validación no busca retórica: busca evidencia de que cada MUST tiene una comprobación o una salida auditable.
