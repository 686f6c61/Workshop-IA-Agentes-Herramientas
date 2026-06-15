# Decisión de split

Estrategia recomendada: **time_group_holdout**.
Gate: **review**.

## Lectura

revisar label_distribution_shift antes de cerrar time_group_holdout.

## Comparación

| Estrategia | Gate | Bloqueos | Revisiones |
|---|---|---|---|
| `random_row` | `block` | student_group_overlap, source_overlap, near_text_leakage, temporal_leakage | missing_required_test_labels |
| `stratified_label` | `block` | student_group_overlap, source_overlap, near_text_leakage, temporal_leakage | ninguna |
| `group_holdout` | `block` | temporal_leakage | label_distribution_shift |
| `time_cutoff` | `block` | student_group_overlap, source_overlap, near_text_leakage | ninguna |
| `time_group_holdout` | `review` | ninguno | label_distribution_shift |

## Próxima acción

Si la estrategia elegida no queda en `pass`, revisa la política, el agrupamiento, la ventana temporal o el dataset fuente antes de usar esa evaluación.

Antes de publicar resultados, guarda también `split_manifest.json`: contiene hashes, estrategia, contrato de uso y asignaciones por split.
