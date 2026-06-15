# Decisión: auditoría de modelo CSP

Modelo: `horario-cursos-csp`.

## Variables y dominios

| Variable | Dominio original | Dominio podado |
|---|---:|---:|
| IA | 4 | 4 |
| Python | 4 | 2 |
| Datos | 4 | 2 |

## Tamaño del espacio

- Candidatos brutos: 64.
- Candidatos tras podar dominios unarios: 16.
- Candidatos evaluados después de podar: 16.
- Soluciones válidas: 4.

## Restricciones

| Restricción | Aridad | Tipo | Explicación |
|---|---:|---|---|
| python_hora_10 | 1 | component_equals | Python solo puede impartirse a las 10. |
| datos_sala_b | 1 | component_equals | Datos necesita sala B. |
| ana_no_solape | 2 | component_not_equals | Ana imparte IA y Python, no puede estar en dos cursos a la misma hora. |
| sala_hora_unica | 3 | all_different_values | Dos cursos no pueden ocupar la misma sala en la misma hora. |

## Soluciones válidas

| Solución | Coste blando |
|---|---:|
| IA=(9, A), Python=(10, A), Datos=(9, B) | 0 |
| IA=(9, A), Python=(10, B), Datos=(9, B) | 0 |
| IA=(9, A), Python=(10, A), Datos=(10, B) | 1 |
| IA=(9, B), Python=(10, A), Datos=(10, B) | 2 |

## Mejor solución

**IA=(9, A), Python=(10, A), Datos=(9, B)** con coste 0.

## Rechazos por restricción

| Restricción | Candidatos rechazados |
|---|---:|
| sala_hora_unica | 10 |
| ana_no_solape | 8 |

## Candidatos manuales

| Candidato | Estado | Coste | Motivo |
|---|---|---:|---|
| valid_best | válido | 0 | cumple reglas duras |
| valid_but_more_cost | válido | 2 | cumple reglas duras |
| bad_python_time | rechazado |  | python_hora_10: Python=(9, 'A'), esperado hour=10 |
| bad_teacher_overlap | rechazado |  | ana_no_solape: IA=(10, 'A'), Python=(10, 'B') |
| bad_room_slot | rechazado |  | sala_hora_unica: IA=(9, 'B'), Python=(10, 'A'), Datos=(9, 'B') |

## Lectura técnica

- La poda unaria reduce el espacio antes de probar combinaciones completas.
- Las restricciones binarias y globales explican por qué se rechaza cada candidato.
- Las preferencias blandas solo ordenan soluciones que ya cumplen las reglas duras.
- Si una restricción aparece como causa de muchos rechazos, conviene revisar si está bien modelada o si el dominio debería limpiarse antes.
