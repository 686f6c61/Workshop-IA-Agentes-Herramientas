# Reward card

Decision: `publicar_reward_spec`.

## Objetivo

Premiar respuestas correctas, con evidencia, abstención cuando falta fuente, formato validable y coste controlado.

## Términos de recompensa

| Término | Peso | Lectura |
|---|---:|---|
| `correctness` | 4.0 | componente explícito de la recompensa |
| `citation` | 2.0 | componente explícito de la recompensa |
| `abstention` | 3.0 | componente explícito de la recompensa |
| `format` | 1.0 | componente explícito de la recompensa |
| `cost_per_tool` | -0.2 | componente explícito de la recompensa |
| `cost_per_100_tokens` | -0.05 | componente explícito de la recompensa |

## Casos de auditoría

| Caso | Ganador | Score | Estado |
|---|---|---:|---|
| `cita_vacaciones` | `a` | 6.71 | `pass` |
| `sin_fuente_cafeteria` | `b` | 7.725 | `pass` |
| `formato_json` | `b` | 6.7175 | `pass` |

## Límites

- No hay bonus por longitud.
- Una respuesta correcta sin cita no gana cuando el caso requiere evidencia.
- Una pregunta sin fuente debe abstenerse.
- El coste se resta, pero nunca debe dominar exactitud y evidencia.

## Repetición del gate

Repetir el gate si cambian documentos, formato de salida, herramienta de recuperación, modelo base o pesos de recompensa.
