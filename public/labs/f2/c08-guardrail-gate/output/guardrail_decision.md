# Decisión: guardrail gate

| Pedido | Decisión | Importe | Rol | Riesgo | Motivos |
|---|---|---:|---|---:|---|
| A100 | ALLOW | 80 | support | 2 | todos los controles pasan |
| A101 | HITL | 850 | support | 20 | permission: importe 850 supera límite automático de rol support: 100; risk: riesgo 20 supera umbral 8 |
| A102 | DENY | 40 | support | 6 | business_policy: estado no permitido: disputed |
| A103 | DENY | -10 | support |  | schema: amount_eur fuera de rango; permission: schema inválido; business_policy: schema inválido; risk: schema inválido; invariant: schema inválido |
| A104 | DENY | 50 | support | 2 | invariant: pedido ya reembolsado |

## Lectura técnica

- `ALLOW` significa que schema, permisos, política, riesgo e invariante pasan.
- `HITL` significa que la acción puede ser legítima, pero no debe ejecutarse automáticamente.
- `DENY` se usa para schema inválido, estado incompatible o invariante roto.
- El sistema falla cerrado: si no puede evaluar un control crítico, no ejecuta la tool.
