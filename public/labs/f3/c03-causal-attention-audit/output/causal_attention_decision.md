# Auditoría QKV y máscara causal

| Token | Pesos visibles |
|---|---|
| El | `[1.0, 0.0, 0.0, 0.0]` |
| banco | `[0.500831, 0.499169, 0.0, 0.0]` |
| aprobó | `[0.319183, 0.314678, 0.366139, 0.0]` |
| préstamo | `[0.218168, 0.213967, 0.284193, 0.283671]` |

Máscara causal correcta: `True`.
Cada fila suma 1 y las posiciones futuras quedan con peso 0.
