# Memo de inferencia

Decisión: `redisenar_serving`.

| Magnitud | Valor |
|---|---:|
| Pesos | 3.5 GB |
| KV cache | 4.295 GB |
| Margen runtime | 6 GB |
| Memoria total estimada | 13.795 GB |
| Decode por usuario | 15.0 tokens/s |
| Tiempo de decode por usuario | 80.0 s |

## Lectura

La memoria parece tratable, pero la latencia de decode no sirve para una experiencia interactiva.

## Acciones técnicas

- Reducir salida esperada o generar por secciones.
- Medir prefill y decode por separado.
- Probar batching continuo en un servidor de inferencia real.
- Comparar un modelo menor, cuantización distinta o más capacidad de serving.
- No comprar hardware solo porque los pesos quepan en memoria.
