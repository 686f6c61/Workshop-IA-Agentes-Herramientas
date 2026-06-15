# Decisión de auditoria por slices

- Estado: **block**
- Dataset: `18a9ab02683e`
- Politica: `96c1b1401974`
- Split evaluado: `test`
- Umbrales: priorizar si score >= `0.78`, normal si score < `0.38`

## Lectura

La muestra evaluada tiene 36 casos, 18 prioritarios y 18 no prioritarios.
La captura segura global es 0.7778, la tasa de perdida operativa es 0.2222 y la tasa de revisión es 0.3611.
La media global no basta: la decisión queda determinada por los slices críticos y por las diferencias de comportamiento entre segmentos.

## Principales señales
- `block` · `global_safety_capture`: La captura global de casos prioritarios queda por debajo del mínimo. valor `0.7778` frente a `0.88`.
- `block` · `global_miss_rate`: La tasa global de casos prioritarios enviados a flujo normal es demasiado alta. valor `0.2222` frente a `0.12`.
- `review` · `auto_recall_gap`: La diferencia entre slices en auto_recall supera el gate. valor `1.0` frente a `0.25`.
- `review` · `miss_rate_gap`: La diferencia entre slices en miss_rate supera el gate. valor `1.0` frente a `0.2`.
- `review` · `false_positive_rate_gap`: La diferencia entre slices en false_positive_rate supera el gate. valor `0.3333` frente a `0.25`.
- `review` · `review_rate_gap`: La diferencia entre slices en review_rate supera el gate. valor `0.75` frente a `0.35`.
- `review` · `cost_per_case_gap`: La diferencia entre slices en cost_per_case supera el gate. valor `4.36` frente a `2.0`.
- `block` · `language=en`: Un slice crítico contiene casos prioritarios enviados a flujo normal. valor `0.25` frente a `0`.
- `block` · `access_need=si`: Un slice crítico contiene casos prioritarios enviados a flujo normal. valor `0.6667` frente a `0`.
- `review` · `product=becas|access_need=si`: Slice con muestra insuficiente para sostener una conclusion. valor `2` frente a `4`.

## Recomendación
No automatices está política en su forma actual. Amplia muestra en slices críticos, revisa umbrales con validation y separa la decisión automatica de los casos que necesitan revisión.

## Entregables

- `slice_audit_report.json` para maquina.
- `slice_metrics.csv` para analisis.
- `slice_audit_card.md` para documentación.
