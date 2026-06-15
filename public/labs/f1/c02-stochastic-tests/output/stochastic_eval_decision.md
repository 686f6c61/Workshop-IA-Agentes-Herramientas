# Decisión: cómo testear una salida probabilística

Un assert exacto mide si la frase coincide letra por letra. Una evaluación de propiedades mide si la salida conserva el contrato que importa.

Ejecuciones por caso: `120`.

| Caso | Temperatura | Exact pass | Property pass | Salidas únicas | Gate |
|---|---:|---:|---:|---:|---|
| rust_definition | 0 | 1.00 | 1.00 | 1 | pasa |
| rust_definition | 0.4 | 0.85 | 1.00 | 3 | pasa |
| rust_definition | 0.9 | 0.55 | 0.95 | 4 | pasa |
| rust_definition | 1.4 | 0.40 | 0.93 | 4 | pasa |
| json_priority | 0 | 1.00 | 1.00 | 1 | pasa |
| json_priority | 0.4 | 0.77 | 0.99 | 3 | pasa |
| json_priority | 0.9 | 0.64 | 0.95 | 3 | pasa |
| json_priority | 1.4 | 0.39 | 0.76 | 4 | revisar |

## Lectura técnica

Si `exact_pass_rate` cae pero `property_pass_rate` se mantiene alto, el problema no es necesariamente el modelo: es el test.
Si `property_pass_rate` cae al subir la temperatura, la tarea necesita muestreo más conservador, salida estructurada o una evaluación más fuerte.
Si hay demasiadas salidas únicas en una tarea factual, el producto puede parecer inestable aunque muchas respuestas sean aceptables.
