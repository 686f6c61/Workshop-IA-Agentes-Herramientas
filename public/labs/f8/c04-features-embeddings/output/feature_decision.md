# Decisión de features

Contrato: `f8-c04-feature-contract-v1`.
Gate: `pass`.

## Lectura

El pipeline ajusta vocabulario, categorias e IDF solo con train. Genera 49 features tabulares/textuales y embeddings densos locales de 64 dimensiones.

## Checks

- Categorias desconocidas: 0
- Columnas prohibidas usadas como feature: 0
- Vectores densos con norma inesperada: 0

## Cómo adaptarlo

Cambia `contracts/feature_contract.json` para tu dataset: columnas permitidas, columnas prohibidas, dimension del embedding local, top-k y splits indexables. Si sustituyes el encoder local por un modelo neural, conserva el manifest de dimension, versión y metadata.
