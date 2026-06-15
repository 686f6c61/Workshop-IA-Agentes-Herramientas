# Alertas DataOps

Estado global: **block**

## Ventana 2026-06-07

Estado: **pass**

- Sin alertas.

## Ventana 2026-06-08

Estado: **block**

- `block` · `missing_trace_rate`: Hay eventos sin trace_id; no se puede investigar bien la ventana. valor `0.1` frente a `0.0`.
- `review` · `latency_p95`: La latencia p95 supera el SLO. valor `760.0` frente a `650`.
- `block` · `miss_rate`: Demasiados casos prioritarios terminan en flujo normal. valor `0.6` frente a `0.12`.
- `block` · `safety_capture`: La captura segura cae por debajo del SLO. valor `0.4` frente a `0.88`.
- `review` · `review_rate`: La carga de revisión puede superar capacidad operativa. valor `0.7` frente a `0.55`.
- `review` · `language`: La distribución actual se aleja de la referencia. valor `0.8` frente a `0.35`.
- `review` · `language`: El PSI indica cambio relevante frente a referencia. valor `11.711575` frente a `0.25`.
- `review` · `access_need`: La distribución actual se aleja de la referencia. valor `0.6` frente a `0.35`.
- `review` · `access_need`: El PSI indica cambio relevante frente a referencia. valor `8.532585` frente a `0.25`.
- `block` · `language=en`: Un slice crítico pierde demasiados casos prioritarios. valor `0.6` frente a `0.12`.
- `review` · `language=en`: Un slice crítico supera latencia p95. valor `760.0` frente a `650`.
- `block` · `access_need=si`: Un slice crítico pierde demasiados casos prioritarios. valor `0.6` frente a `0.12`.
- `review` · `access_need=si`: Un slice crítico supera latencia p95. valor `760.0` frente a `650`.
- `block` · `product=practicas`: Un slice crítico pierde demasiados casos prioritarios. valor `1.0` frente a `0.12`.
- `review` · `product=practicas`: Un slice crítico supera latencia p95. valor `760.0` frente a `650`.
