# Decisión: neurona artificial con contrato

Una neurona solo calcula si el contrato de entrada se cumple: misma dimensión para entradas y pesos, sesgo numérico y activación permitida.

| Caso | Válido | Dimensión | Activación | z | salida | Estado |
|---|---|---:|---|---:|---:|---|
| baseline_relu | sí | 3 | `relu` | 0.64 | 0.64 | pasa |
| negative_relu | sí | 3 | `relu` | -1.3 | 0.0 | pasa |
| binary_sigmoid | sí | 2 | `sigmoid` | 1.0 | 0.7310585786 | pasa |
| linear_score | sí | 4 | `linear` | 0.35 | 0.35 | pasa |
| invalid_dimension | no | - | - | - | - | fallo esperado: inputs y weights deben tener la misma dimensión |

## Sensibilidad

- `baseline_relu`: el mayor cambio de salida viene de `bias` con variación 0.1.
- `negative_relu`: el mayor cambio de salida viene de `w1` con variación 0.0.
- `binary_sigmoid`: el mayor cambio de salida viene de `w1` con variación 0.0374662049.
- `linear_score`: el mayor cambio de salida viene de `bias` con variación 0.1.
