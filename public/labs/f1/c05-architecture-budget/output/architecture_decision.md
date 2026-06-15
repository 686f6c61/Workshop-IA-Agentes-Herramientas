# Decisión: presupuesto de arquitectura neuronal

Una arquitectura se puede revisar antes de entrenar: contrato de salida, formas, parámetros, memoria mínima y relación entre datos y capacidad.

| Candidato | Arquitectura | Parámetros | Ejemplos/parámetro | Memoria BF16 MB | Estado | Decisión |
|---|---|---:|---:|---:|---|---|
| `tickets_mlp_small` | 48 -> 32 -> 3 | 1667 | 2.9994 | 0.0032 | ok | candidato razonable para primer entrenamiento |
| `tickets_mlp_medium` | 48 -> 128 -> 64 -> 3 | 14723 | 0.339605 | 0.0281 | relación ejemplos/parámetro baja; exige validación fuerte | entrenar solo como experimento controlado y comparar con una base más simple |
| `tickets_mlp_excessive_for_data` | 48 -> 1024 -> 1024 -> 3 | 1102851 | 0.001088 | 2.1035 | demasiados parámetros para el laboratorio introductorio; muy pocos ejemplos por parámetro | entrenar solo como experimento controlado y comparar con una base más simple |
| `binary_output_wrong` | 24 -> 16 -> 2 | 434 | 1.843318 | 0.0008 | binary_classification espera output_dim=1; binary_classification espera activación sigmoid | corregir contrato antes de entrenar |
| `regression_price_baseline` | 18 -> 32 -> 16 -> 1 | 1153 | 2.601908 | 0.0022 | ok | candidato razonable para primer entrenamiento |

## Formas por capa

### tickets_mlp_small

| Capa | W | b | Parámetros |
|---:|---|---|---:|
| 1 | 32 x 48 | 32 | 1568 |
| 2 | 3 x 32 | 3 | 99 |

### tickets_mlp_medium

| Capa | W | b | Parámetros |
|---:|---|---|---:|
| 1 | 128 x 48 | 128 | 6272 |
| 2 | 64 x 128 | 64 | 8256 |
| 3 | 3 x 64 | 3 | 195 |

### tickets_mlp_excessive_for_data

| Capa | W | b | Parámetros |
|---:|---|---|---:|
| 1 | 1024 x 48 | 1024 | 50176 |
| 2 | 1024 x 1024 | 1024 | 1049600 |
| 3 | 3 x 1024 | 3 | 3075 |

### binary_output_wrong

| Capa | W | b | Parámetros |
|---:|---|---|---:|
| 1 | 16 x 24 | 16 | 400 |
| 2 | 2 x 16 | 2 | 34 |

### regression_price_baseline

| Capa | W | b | Parámetros |
|---:|---|---|---:|
| 1 | 32 x 18 | 32 | 608 |
| 2 | 16 x 32 | 16 | 528 |
| 3 | 1 x 16 | 1 | 17 |

## Lectura técnica

- Un candidato `invalid` no debe entrenarse: primero se arregla el contrato de salida.
- Un candidato con `warning` puede ser útil, pero exige comparación con una base sencilla y validación fuera de entrenamiento.
- La memoria de pesos no es la memoria total de entrenamiento: faltan activaciones, gradientes y estados del optimizador.
- El conteo de parámetros no mide calidad. Sirve para discutir capacidad, coste y riesgo.
