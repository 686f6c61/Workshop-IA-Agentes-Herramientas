# Decisión: pérdida y optimizador

Todas las runs usan el mismo dataset sintético y la misma partición train/validación. La comparación mira pérdida, F1, accuracy y brecha de generalización.

| Run | Pérdida | Optimizador | lr | weight decay | F1 valid | Accuracy valid | Gap F1 | Avisos | Decisión |
|---|---|---|---:|---:|---:|---:|---:|---|---|
| `bce_sgd_lr_1` | bce | sgd | 1.0 | 0.0 | 0.913793 | 0.885714 | 0.00301 | ok | candidato principal |
| `bce_sgd_lr_01` | bce | sgd | 0.1 | 0.0 | 0.909871 | 0.88 | 0.005438 | ok | candidato principal |
| `bce_adamw` | bce | adamw | 0.05 | 0.01 | 0.909871 | 0.88 | 0.007471 | ok | candidato principal |
| `mse_sgd_lr_01` | mse | sgd | 0.1 | 0.0 | 0.909871 | 0.88 | 0.006931 | MSE no es la pérdida natural para clasificación binaria | candidato a revisar |
| `bce_adamw_no_decay` | bce | adamw | 0.05 | 0.0 | 0.909871 | 0.88 | 0.007471 | ok | candidato principal |

## Curvas resumidas

### bce_sgd_lr_1

| Época | Train loss | Valid loss | Valid F1 |
|---:|---:|---:|---:|
| 1 | 0.693147 | 0.565904 | 0.909871 |
| 5 | 0.406009 | 0.385864 | 0.909871 |
| 20 | 0.267657 | 0.277054 | 0.909871 |
| 60 | 0.220908 | 0.240095 | 0.913793 |
| 120 | 0.208059 | 0.231674 | 0.913793 |

### bce_sgd_lr_01

| Época | Train loss | Valid loss | Valid F1 |
|---:|---:|---:|---:|
| 1 | 0.693147 | 0.678829 | 0.909871 |
| 5 | 0.639307 | 0.628209 | 0.909871 |
| 20 | 0.508465 | 0.504724 | 0.909871 |
| 60 | 0.372471 | 0.375946 | 0.909871 |
| 120 | 0.304446 | 0.312606 | 0.909871 |

### bce_adamw

| Época | Train loss | Valid loss | Valid F1 |
|---:|---:|---:|---:|
| 1 | 0.693147 | 0.660623 | 0.914729 |
| 5 | 0.588527 | 0.552334 | 0.914729 |
| 20 | 0.383624 | 0.3689 | 0.900826 |
| 60 | 0.25753 | 0.26845 | 0.905983 |
| 120 | 0.223079 | 0.241376 | 0.909871 |

### mse_sgd_lr_01

| Época | Train loss | Valid loss | Valid F1 |
|---:|---:|---:|---:|
| 1 | 0.125 | 0.124097 | 0.909871 |
| 5 | 0.121412 | 0.120596 | 0.909871 |
| 20 | 0.109566 | 0.109049 | 0.909871 |
| 60 | 0.088177 | 0.088217 | 0.909871 |
| 120 | 0.071602 | 0.072139 | 0.909871 |

### bce_adamw_no_decay

| Época | Train loss | Valid loss | Valid F1 |
|---:|---:|---:|---:|
| 1 | 0.693147 | 0.660611 | 0.914729 |
| 5 | 0.588422 | 0.552197 | 0.914729 |
| 20 | 0.382787 | 0.368153 | 0.900826 |
| 60 | 0.255811 | 0.26706 | 0.905983 |
| 120 | 0.221041 | 0.239928 | 0.909871 |

## Lectura técnica

- BCE es la pérdida natural para clasificación binaria porque optimiza probabilidad logarítmica de la clase correcta.
- MSE puede aprender algo, pero su gradiente no está tan alineado con clasificación probabilística.
- No compares el valor absoluto de BCE y MSE como si fueran la misma escala; compara validación y comportamiento.
- AdamW añade estado interno y weight decay desacoplado; por eso puede ser más estable que SGD con menos ajuste manual.
- Una run no se elige solo por train loss: validación y F1 mandan.
