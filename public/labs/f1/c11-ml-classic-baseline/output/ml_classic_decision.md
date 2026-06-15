# Baseline clásico de tickets

Filas de entrenamiento: `20`. Filas de test: `4`.

## Métricas

| Modelo | Accuracy | Precision | Recall | F1 | FP | FN |
|---|---:|---:|---:|---:|---:|---:|
| Regresión logística | 1.0 | 1.0 | 1.0 | 1.0 | 0 | 0 |
| Mayoría | 0.5 | 0.5 | 1.0 | 0.6667 | 2 | 0 |

## Decisión

La regresión logística supera la baseline y cumple el mínimo de recall/F1. El siguiente paso no es meter un LLM: es validar con más datos, separar por tiempo y revisar errores.

## Predicciones de test

| Ticket | Real | Probabilidad | Predicción |
|---|---:|---:|---:|
| T005 | 1 | 0.9959 | 1 |
| T010 | 0 | 0.0025 | 0 |
| T015 | 1 | 0.9997 | 1 |
| T020 | 0 | 0.0073 | 0 |
