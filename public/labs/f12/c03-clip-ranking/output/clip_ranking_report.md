# Reporte de ranking contrastivo imagen-texto

Dataset: `f12-c03-catalog-demo-v1`
Temperatura: `0.07`
Recall@1 imagen->texto: `1.0`
Recall@1 texto->imagen: `1.0`
Pérdida simétrica InfoNCE: `0.425937`
Gate: `pass`

## Métricas

| Métrica | Valor |
|---|---:|
| image_to_text_recall_at_1 | 1.0 |
| image_to_text_recall_at_3 | 1.0 |
| text_to_image_recall_at_1 | 1.0 |
| text_to_image_recall_at_3 | 1.0 |
| mean_positive_margin | 0.125431 |
| query_recall_at_1 | 1.0 |

## Negativos duros

| Imagen | Top incorrecto o margen bajo | Margen | Razón |
|---|---|---:|---|
| ui_error | ui_error | 0.009213 | margen_bajo |
| grant_form_blocked | grant_form_blocked | 0.004723 | margen_bajo |
| invoice_total | invoice_total | 0.021102 | margen_bajo |
| grant_policy_pdf | grant_policy_pdf | 0.01799 | margen_bajo |
| whiteboard_plan | whiteboard_plan | 0.031512 | margen_bajo |
| whiteboard_invoice_confuser | whiteboard_invoice_confuser | 0.042289 | margen_bajo |

## Consultas externas

| Query | Esperado | Rank | Top 3 |
|---|---|---:|---|
| q_catalogo_silla | black_chair | 1 | black_chair (0.998288), grant_policy_pdf (0.531807), invoice_total (0.529026) |
| q_factura_total | invoice_total | 1 | invoice_total (0.998523), grant_policy_pdf (0.986303), whiteboard_invoice_confuser (0.647836) |
| q_beca_bloqueada | grant_form_blocked | 1 | grant_form_blocked (0.998205), ui_error (0.984659), grant_policy_pdf (0.617895) |
| q_pizarra_numeros | whiteboard_invoice_confuser | 1 | whiteboard_invoice_confuser (0.999094), whiteboard_plan (0.967462), grant_policy_pdf (0.732596) |

## Decisión de ingeniería

- Si el Recall@1 baja, revisa descripciones, embeddings, negativos duros y dominio.
- Si la diagonal de la matriz no destaca, los pares positivos no están suficientemente separados.
- Si hay celdas oscuras fuera de diagonal, no lo escondas: son los casos que debes enseñar al alumno y probar en producción.
