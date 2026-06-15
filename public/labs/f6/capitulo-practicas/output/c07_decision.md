# Decisión C07: Rollout progresivo

Estado: `valid`.

## Evidencias

- OK: shadow sin efecto. Se observa antes de impactar.
- OK: canary pequeño. Exposición limitada.
- OK: ramp con gate. Subir tráfico exige evidencia.
- OK: rollback definido. Hay ruta de vuelta.

## Decisión

El cambio progresa por evidencia: shadow, canary, ramp y rollback tienen gates separados.
