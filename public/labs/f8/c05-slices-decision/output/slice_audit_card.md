# Slice audit card

- Estado: **block**
- Unidad evaluada: `decision_policy_on_test_predictions`
- Campos auditados: `product, channel, language, access_need, student_profile`
- Campos usados solo para auditoria: `access_need, student_profile`
- Slices críticos: `access_need=si, language=en, product=practicas|access_need=si`

## Uso previsto

Auditar una política de triaje antes de permitir más automatización.

## Límites

El reporte no demuestra justicia universal. Mide el comportamiento de está muestra, con estos campos, estos umbrales y este contrato.

## Próxima acción

Recolectar más datos en slices críticos y volver a evaluar con umbrales congelados desde validation.
