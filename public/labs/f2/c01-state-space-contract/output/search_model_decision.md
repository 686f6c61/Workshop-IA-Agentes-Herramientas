# Decisión: contrato de búsqueda

Problema: `rutas_peninsula_demo`.

| Elemento | Valor |
|---|---|
| Estados | 6 |
| Acciones | 8 |
| Estado inicial | `Madrid` |
| Metas | `Barcelona` |
| Factor de ramificación medio | 1.3333 |
| Profundidad estimada | 6 |
| Nodos estimados | 19 |
| Ciclos | sí |

## Estado del modelo

Estado: **válido**.

- hay ciclos; el algoritmo debe mantener visitados

## Planes candidatos

| Plan | Camino | Coste | ¿Solución? | Observación |
|---|---|---:|---|---|
| `directo_por_zaragoza` | Madrid -> Zaragoza -> Barcelona | 615 | sí | llega a meta |
| `por_valencia` | Madrid -> Valencia -> Barcelona | 710 | sí | llega a meta |
| `ciclo_y_meta` | Madrid -> Zaragoza -> Madrid -> Zaragoza -> Barcelona | 1245 | sí | llega a meta; repite estados: Madrid, Zaragoza |
| `accion_imposible` | Madrid | 0 | no | acción burgos_bilbao requiere origen Burgos, pero el estado actual es Madrid |
| `no_llega_a_meta` | Madrid -> Burgos -> Bilbao | 405 | no | el plan termina en Bilbao, que no pertenece a goals |

## Decisión

El mejor plan candidato válido es `directo_por_zaragoza` con coste 615.

Esta conclusión no demuestra optimalidad global: solo compara los planes candidatos. Para demostrar optimalidad necesitas ejecutar un algoritmo con garantías, como UCS o A* con una heurística admisible.
