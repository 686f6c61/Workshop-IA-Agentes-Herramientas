# Decisión final del facsímil 8

Estado: **block**.

## Lectura ejecutiva

Este resultado no dice que el sistema sea inútil. Dice algo más concreto: todavia no hay evidencia operativa suficiente para publicarlo como automatización.
El bloqueo viene de dos condiciones que no se negocian en un sistema de IA aplicado: trazabilidad completa y campos obligatorios completos. Sin esas dos piezas, no se puede reconstruir una decisión ni defender una medición.

## Resumen técnico

- Checks en `pass`: 2.
- Checks en `review`: 5.
- Checks en `block`: 2.

Interpretacion:

- `block` impide publicar.
- `review` no impide por sí solo, pero exige plan de corrección y nueva medición.
- `pass` solo significa que ese control concreto no encontro problema con este dataset.

## Checks

| Check | Estado | Valor | Umbral |
|---|---|---:|---:|
| `schema` | `pass` | `[]` | `` |
| `missing_trace_rate` | `block` | `0.083333` | `0.0` |
| `missing_required_fields_rate` | `block` | `0.083333` | `0.0` |
| `latency_p95_ms` | `review` | `730.0` | `720` |
| `test_accuracy` | `review` | `0.6` | `0.75` |
| `citation_valid_rate` | `pass` | `0.916667` | `0.9` |
| `critical_slice_miss_rate:language=en` | `review` | `0.8` | `0.25` |
| `critical_slice_miss_rate:segment=practicas` | `review` | `0.75` | `0.25` |
| `critical_slice_miss_rate:source=form` | `review` | `0.666667` | `0.25` |

## Lectura de los fallos

| Zona | Lectura | Accion esperada |
|---|---|---|
| Trazabilidad | Hay al menos una fila sin `trace_id`. | No publicar hasta poder reconstruir cada decision. |
| Campos obligatorios | Hay al menos una fila incompleta. | Corregir ingesta, validación y contrato de datos. |
| Latencia | `p95` queda por encima del SLO. | Revisar ruta lenta, proveedor, RAG o fallback. |
| Test | La accuracy de test queda por debajo del mínimo. | Revisar split, datos, umbral y tipos de error. |
| Slices críticos | `language=en`, `segment=practicas` y `source=form` concentran misses. | No fiarse de la media global; corregir esos segmentos antes de automatizar. |

## Decisión profesional

No se publica. El proyecto debe corregir trazabilidad, campos obligatorios y slices críticos antes de usar este dataset para automatizar decisiones.

## Siguiente iteracion

1. Reparar `trace_id` y validar que todo evento de decision tiene traza.
2. Bloquear en ingesta cualquier fila sin campos obligatorios.
3. Analizar los casos `language=en`, `segment=practicas` y `source=form` como slices de primer nivel.
4. Repetir evaluación con el mismo contrato, no con una metrica elegida después.
5. Si se propone una intervencion, medirla con el kit de experimentos del capítulo 07.
