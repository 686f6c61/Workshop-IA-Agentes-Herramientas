# Alcance de release de datos

## Sistema

Mini sistema de priorizacion académica usado en el laboratorio final del facsímil 8.

## Alcance permitido

- Uso: revisión técnica y aprendizaje.
- Decisión: no automatizar publicación si el estado final es `block`.
- Slices bajo vigilancia: `language=en`, `segment=practicas`, `source=form`.
- Contrato fijo: `contracts/final_review_contract.json`.

## Condiciones para avanzar

1. Trazabilidad completa.
2. Campos obligatorios completos.
3. Test revisado con el mismo split.
4. Slices críticos por debajo de umbral o alcance limitado.
5. Plan experimental conectado con el fallo detectado.
