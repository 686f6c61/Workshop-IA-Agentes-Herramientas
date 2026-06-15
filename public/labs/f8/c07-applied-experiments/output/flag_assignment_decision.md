# Asignacion por feature flag

Estado: **review**.

| Variante | Unidades | Share |
|---|---:|---:|
| `control` | `7` | `0.291667` |
| `treatment` | `17` | `0.708333` |

## Lectura

Este ejemplo simula evaluación determinista por flag. En un sistema real, este output debería corresponder a una tabla de exposición: unidad, variante, versión de flag, contexto y momento de exposición.

Hay diferencias entre la variante del dataset y la variante calculada por la flag. En producción esto bloquearia el analisis hasta explicar la fuente de verdad.
