# Decisión operativa DataOps

Estado global: **block**.

## Lectura

Este gate no decide si el modelo es inteligente. Decide si la ventana de producción es suficientemente trazable, representativa y estable para sostener decisiones.

| Ventana | Estado | n | Trace faltante | Latencia p95 | Revision | Perdida | Captura segura | Flags |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 2026-06-07 | `pass` | 10 | 0.0 | 590.0 | 0.4 | 0.0 | 1.0 | 0 |
| 2026-06-08 | `block` | 10 | 0.1 | 760.0 | 0.7 | 0.6 | 0.4 | 15 |

## Recomendación

No aumentes automatización ni uses está ventana para reentrenar sin investigar. Empieza por los flags `block`, corrige trazabilidad y revisa slices críticos.
