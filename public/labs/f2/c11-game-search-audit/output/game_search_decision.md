# Auditoría de juego

Minimax elige `limitar_tool` con scores `{'limitar_tool': 4, 'seguir_automatico': -8, 'pedir_revision': 3}`.
Alfa-beta elige `limitar_tool` visitando `4` hojas y podando `2`.
UCT elige `limitar_tool` con c=`1.4`.

## Monte Carlo

| Acción | Media | Peor caso | Mejor caso | Incertidumbre |
|---|---:|---:|---:|---:|
| limitar_tool | 4.1667 | 3 | 5 | 0.4082 |
| seguir_automatico | -0.6667 | -8 | 9 | 0.4082 |
| pedir_revision | 4.8333 | 3 | 7 | 0.4082 |

## Decisión

Si el peor caso es inaceptable, la media no basta. Minimax sirve como prueba de tensión; Monte Carlo sirve para estimar comportamiento medio; UCT reparte presupuesto de simulación.
