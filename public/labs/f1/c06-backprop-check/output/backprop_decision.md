# Decisión: comprobación de retropropagación

El informe compara gradientes analíticos contra diferencias finitas y revisa cómo cambia la pérdida con distintos learning rates.

| Caso | Loss inicial | Grad norm | Check | Learning rate recomendado | Loss con signo contrario | Avisos |
|---|---:|---:|---|---:|---:|---|
| `chapter_example` | 0.055049677269 | 0.164500907769 | pasa | 1.0 | 0.057805931372 | algún learning rate mueve el peso más que su escala actual |
| `saturated_sigmoid` | 0.499999999986 | 1.12e-10 | pasa | ninguno | 0.499999999986 | gradiente casi nulo |
| `small_signal` | 0.145754041282 | 0.134286073333 | pasa | 5.0 | 0.147561893247 | ok |

## Gradientes

### chapter_example

| Parámetro | Analítico | Numérico | Error absoluto |
|---|---:|---:|---:|
| `dE_dw` | -0.147134084853 | -0.147134084858 | 5e-12 |
| `dE_db` | -0.073567042426 | -0.073567042427 | 1e-12 |

### saturated_sigmoid

| Parámetro | Analítico | Numérico | Error absoluto |
|---|---:|---:|---:|
| `dE_dw` | 1.11e-10 | 1.11e-10 | 0.0 |
| `dE_db` | 1.4e-11 | 1.1e-11 | 3e-12 |

### small_signal

| Parámetro | Analítico | Numérico | Error absoluto |
|---|---:|---:|---:|
| `dE_dw` | -0.006705926491 | -0.006705926492 | 1e-12 |
| `dE_db` | -0.13411852982 | -0.134118529817 | 3e-12 |

## Barrido de learning rate

### chapter_example

| lr | Loss después | Cambio de loss | Mejora | Ratio actualización w |
|---:|---:|---:|---|---:|
| 0.001 | 0.05502262172 | -2.7055549e-05 | sí | 0.000367835212 |
| 0.01 | 0.054779571534 | -0.000270105735 | sí | 0.003678352121 |
| 0.1 | 0.052393401988 | -0.002656275281 | sí | 0.036783521213 |
| 1.0 | 0.032720653251 | -0.022329024018 | sí | 0.367835212132 |
| 5.0 | 0.002675974864 | -0.052373702405 | sí | 1.83917606066 |

### saturated_sigmoid

| lr | Loss después | Cambio de loss | Mejora | Ratio actualización w |
|---:|---:|---:|---|---:|
| 0.001 | 0.499999999986 | 0.0 | no | 0.0 |
| 0.01 | 0.499999999986 | 0.0 | no | 0.0 |
| 0.1 | 0.499999999986 | 0.0 | no | 4e-12 |
| 1.0 | 0.499999999986 | 0.0 | no | 3.7e-11 |
| 5.0 | 0.499999999986 | 0.0 | no | 1.85e-10 |

### small_signal

| lr | Loss después | Cambio de loss | Mejora | Ratio actualización w |
|---:|---:|---:|---|---:|
| 0.001 | 0.145736008994 | -1.8032288e-05 | sí | 8.382408e-06 |
| 0.01 | 0.145573759918 | -0.000180281364 | sí | 8.3824081e-05 |
| 0.1 | 0.143955408614 | -0.001798632668 | sí | 0.000838240811 |
| 1.0 | 0.128213489831 | -0.017540551451 | sí | 0.008382408114 |
| 5.0 | 0.070185709392 | -0.07556833189 | sí | 0.041912040569 |

## Lectura técnica

- Si el gradient check falla, primero se revisa la derivada, el signo y la función de pérdida.
- Si el gradiente es casi cero, puede haber saturación o una cadena de activaciones que atenúa la señal.
- Si el learning rate mejora con pasos pequeños pero empeora con pasos grandes, el problema no es la derivada: es la escala de actualización.
- La actualización con signo contrario debe empeorar o no mejorar. Si mejora, has definido la pérdida o el signo de forma sospechosa.
