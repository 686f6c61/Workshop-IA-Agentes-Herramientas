# Reporte de patches visuales

Imagen: `data/synthetic_ticket.ppm` (8x8x3)
Patch size: `2`
Tokens visuales: `16`
Pares de atención si todos miran a todos: `256`
Gate válido: `True`

## Primeros patches

| Patch | Posición | RGB medio | Embedding de juguete |
|---|---|---|---|
| p0 | fila 0, col 0 | (72.5, 72.5, 72.5) | [-0.5, -0.4463, -0.3925, -0.5969, -0.5431, -0.4894] |
| p1 | fila 0, col 1 | (125.0, 125.0, 125.0) | [-0.44, -0.3239, -0.2078, -0.638, -0.522, -0.4059] |
| p2 | fila 0, col 2 | (72.5, 72.5, 72.5) | [-0.38, -0.3663, -0.3525, -0.5969, -0.5831, -0.5694] |
| p3 | fila 0, col 3 | (20.0, 20.0, 20.0) | [-0.32, -0.4086, -0.4973, -0.5557, -0.6443, -0.7329] |
| p4 | fila 1, col 0 | (236.25, 236.25, 236.25) | [-0.46, -0.1894, 0.0812, -0.6653, -0.3947, -0.1241] |
| p5 | fila 1, col 1 | (227.5, 227.5, 227.5) | [-0.4, -0.1631, 0.0737, -0.6584, -0.4216, -0.1847] |
| p6 | fila 1, col 2 | (236.25, 236.25, 236.25) | [-0.34, -0.1094, 0.1212, -0.6653, -0.4347, -0.2041] |
| p7 | fila 1, col 3 | (245.0, 245.0, 245.0) | [-0.28, -0.0557, 0.1686, -0.6722, -0.4478, -0.2235] |

## Presupuesto por resolución

| Caso | Resolución | Patch | Tokens visuales | Pares atención | Ratio tokens | Ratio atención |
|---|---:|---:|---:|---:|---:|---:|
| mini_demo | 8x8 | 2 | 16 | 256 | 0.0816 | 0.0067 |
| vit_base_224_p16 | 224x224 | 16 | 196 | 38416 | 1.0 | 1.0 |
| captura_hd_p16 | 1280x720 | 16 | 3600 | 12960000 | 18.3673 | 337.3594 |
| captura_hd_p32 | 1280x720 | 32 | 920 | 846400 | 4.6939 | 22.0325 |
| captura_beca_larga_p16 | 3200x1440 | 16 | 18000 | 324000000 | 91.8367 | 8433.9858 |
| captura_beca_region_alerta_p16 | 512x320 | 16 | 640 | 409600 | 3.2653 | 10.6622 |
| captura_movil_larga_p16 | 1170x2532 | 16 | 11766 | 138438756 | 60.0306 | 3603.6744 |
| documento_alta_res_p16 | 2339x1654 | 16 | 15288 | 233722944 | 78.0 | 6084.0 |
| factura_region_total_p16 | 640x320 | 16 | 800 | 640000 | 4.0816 | 16.6597 |

## Decisión de ingeniería

- Regla: bajar patch_size aumenta detalle, pero tambien tokens visuales y coste cuadratico de atencion.
- Vigila: visual_tokens, attention_pairs, padding_ratio, texto_pequeno, aspect_ratio.

Si una captura contiene texto pequeño, quizá necesitas más resolución o patches más pequeños. Si solo necesitas una señal gruesa de producto, quizá puedes aceptar patches mayores y menos tokens.