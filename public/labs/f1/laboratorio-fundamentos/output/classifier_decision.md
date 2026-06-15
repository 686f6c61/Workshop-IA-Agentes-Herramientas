# Decisión de clasificador

Decisión: `publicar_piloto`.
Modelo elegido: `modelo_b`.

## Motivo

`modelo_b` alcanza F1 `0.766` y manda `44` tickets a revisión prioritaria, por debajo de la capacidad diaria de `60`.

| Modelo | Precisión | Recall | F1 | Cola prioritaria |
|---|---:|---:|---:|---:|
| `modelo_a` | 0.6111 | 0.88 | 0.7213 | 72 |
| `modelo_b` | 0.8182 | 0.72 | 0.766 | 44 |

## Lectura para una persona no técnica

El primer modelo encuentra más casos importantes, pero genera una cola demasiado grande. El segundo manda menos ruido y cabe en la capacidad diaria del equipo.
