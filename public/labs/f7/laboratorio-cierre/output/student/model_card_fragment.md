# Fragmento de model card: interpretabilidad

Modelo: `support-prioritizer-linear-v1`.
Política de explicación: `interp-audit-v1`.
Dataset hash: `ec7bf55279ff3c6a3f93510b638fea374eff27577425cdcb76b5ba103c7af20e`.

## Uso previsto

Priorizar tickets académicos para revisión operativa. No debe usarse como decisión final sin revisar política, datos y umbral.

## Explicaciones disponibles

- Contribuciones locales por feature para cada caso.
- Importancia global por permutación.
- Pruebas de borrado de feature superior.
- Suficiencia y comprehensiveness de las dos features principales.
- Estabilidad ante pequeñas perturbaciones numéricas.
- Contrafactuales accionables limitados a campos modificables.
- Escaneo simple de correlaciones para detectar proxies obvios.

## Resultado de auditoría

- `deletion_top_feature_drop`: pasa.
- `permutation_importance_drop`: pasa.
- `stability_top1`: pasa.
- `counterfactual_available`: pasa.
- `comprehensiveness_top2`: pasa.
- `sufficiency_top2`: pasa.
- `feature_proxy_scan`: pasa.
