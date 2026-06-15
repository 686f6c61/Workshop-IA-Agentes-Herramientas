# Decisión: SAT y CSP verificables

## SAT: campaña con aprobación legal

Asignaciones probadas: 8. Modelos encontrados: 3.

| Modelo | A email | B banner | C legal |
|---:|---:|---:|---:|
| 1 | 0 | 1 | 1 |
| 2 | 1 | 0 | 1 |
| 3 | 1 | 1 | 1 |

## CSP: agenda con reglas duras y preferencias

Asignaciones probadas: 27. Soluciones válidas: 4.

| Agenda válida | Coste blando |
|---|---:|
| R1=9, R2=10, R3=11 | 0 |
| R1=11, R2=10, R3=11 | 1 |
| R1=9, R2=10, R3=9 | 2 |
| R1=11, R2=10, R3=9 | 3 |

## Mejor agenda válida

**R1=9, R2=10, R3=11** con coste 0.

No gana por ser la única posible: gana porque cumple todas las reglas duras y además minimiza preferencias blandas.

## Validación de candidatos

| Candidato | Estado | Coste | Explicación |
|---|---|---:|---|
| valid_best | válido | 0 | cumple reglas duras |
| valid_but_not_best | válido | 3 | cumple reglas duras |
| bad_overlap | rechazado |  | ana_no_solape: R1=10 y R2=10 |
| bad_client_time | rechazado |  | cliente_a_las_10: R2=11, esperado 10 |
| bad_room_conflict | rechazado |  | sala_no_solape: R2=10 y R3=10 |

## Lectura técnica

- SAT trabaja con interruptores. Aquí prueba 2^3 asignaciones y conserva las que satisfacen todas las cláusulas.
- CSP trabaja con variables y dominios. Aquí prueba 3^3 agendas antes de filtrar restricciones duras.
- Las preferencias blandas no hacen válida una agenda inválida: solo ordenan las que ya pasaron las reglas duras.
- Este patrón es directamente trasladable a permisos, configuración de producto, turnos, reservas y validación de acciones de agentes.
