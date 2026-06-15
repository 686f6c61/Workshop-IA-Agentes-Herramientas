# LayerNorm y sampling

LayerNorm: `[1.224741, -1.224741, 0.0]`.

| Temperatura | Entropía |
|---:|---:|
| 0.5 | 0.382645 |
| 1.0 | 0.773068 |
| 2.0 | 1.137899 |

Top-k: `{'París': 0.731059, 'Madrid': 0.268941, 'Lyon': 0.0, 'azul': 0.0}`.
Top-p: `{'París': 0.731059, 'Madrid': 0.268941, 'Lyon': 0.0, 'azul': 0.0}`.
Temperatura controla concentración; top-k y top-p recortan el conjunto candidato.
