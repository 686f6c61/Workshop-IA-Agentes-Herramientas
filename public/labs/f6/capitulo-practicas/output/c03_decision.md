# Decisión C03: Estimación de capacidad

Estado: `valid`.

## Evidencias

- OK: servicio calculado. Tiempo estimado por request: 9.08s.
- OK: capacidad suficiente. Capacidad estimada: 7.05 rps.
- OK: margen visible. Hay margen antes de saturar.
- OK: tokens separados. Se distinguen prefill y decode.

## Decisión

La capacidad inicial es defendible, pero exige medir p95 real después del despliegue.
