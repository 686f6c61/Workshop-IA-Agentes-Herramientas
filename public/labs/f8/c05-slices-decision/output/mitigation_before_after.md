# Comparación de mitigación por banda de revisión

Esta comparación no busca ganar una metrica tocando test. Muestra una hipótesis de mitigación: ampliar la banda de revisión para evitar que casos prioritarios inciertos pasen a flujo normal.

## Resultado global

| Politica | Estado | Normal si score < | Captura segura | Perdida operativa | Tasa de revisión | Coste por caso | Flags block | Flags review |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| base | block | 0.38 | 0.7778 | 0.2222 | 0.3611 | 1.4056 | 5 | 7 |
| banda_revision | review | 0.32 | 1.0 | 0.0 | 0.5278 | 0.7167 | 0 | 5 |

## Lectura de ingeniería

- La política base queda en `block`: captura segura `0.7778` y perdida operativa `0.2222`.
- La política candidata queda en `review`: captura segura `1.0` y perdida operativa `0.0`.
- El coste es que la tasa de revisión sube de `0.3611` a `0.5278`.
- Si el equipo no tiene capacidad humana para esa revisión, la mitigación no está lista aunque mejore la captura.

## Slices críticos

| Politica | Slice | n | Positivos | Auto-recall | Perdida | Captura segura | Revision | Coste por caso |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| base | `language=en` | 9 | 4 | 0.25 | 0.25 | 0.75 | 0.5556 | 1.5556 |
| base | `access_need=si` | 12 | 6 | 0.0 | 0.6667 | 0.3333 | 0.5 | 3.2667 |
| base | `product=practicas|access_need=si` | 4 | 2 | 0.0 | 1.0 | 0.0 | 0.5 | 4.6 |
| banda_revision | `language=en` | 9 | 4 | 0.25 | 0.0 | 1.0 | 0.6667 | 0.8 |
| banda_revision | `access_need=si` | 12 | 6 | 0.0 | 0.0 | 1.0 | 0.9167 | 1.1 |
| banda_revision | `product=practicas|access_need=si` | 4 | 2 | 0.0 | 0.0 | 1.0 | 1.0 | 1.2 |

## Decisión

Esta candidata no se publica automáticamente. Pasa de `block` a `review`, que es justo el aprendizaje: mitigar puede reducir un fallo grave, pero debe revisarse contra capacidad, coste, experiencia de usuario y datos adicionales.
