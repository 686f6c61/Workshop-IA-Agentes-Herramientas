# Decisión Bellman

Escenario: `support_mdp_v1`.
Estado del gate: `pass`.
Gamma: `0.9`.
Iteraciones: `10`.

## Política resultante

| Estado | Acción elegida | Valor Q | Margen | Lectura |
|---|---|---:|---:|---|
| `nuevo` | `pedir_dato` | 1.190579 | 0.924579 | pedir evidencia compensa porque aumenta la probabilidad de resolver con cita. |
| `evidencia` | `responder_con_cita` | 1.7 | 1.298 | responder con cita domina escalar si la evidencia ya está disponible. |
| `critico` | `escalar` | 0.556 | 1.576 | escalar evita respuestas directas con alto coste de reapertura. |

## Decisión técnica

Esta política puede usarse como ejercicio y como especificación inicial, no como despliegue directo. Para pasar a un sistema real harían falta eventos de interacción, trazas de propensión, evaluación offline y serving con política de reserva.

## Qué cambiaría para experimentar

- Subir el coste de `pedir_dato` para ver cuándo deja de compensar.
- Reducir la probabilidad de éxito de `responder_con_cita` para detectar sensibilidad.
- Cambiar `gamma` y observar si el sistema se vuelve más miope.
- Añadir un estado `pendiente_legal` si la decisión depende de una revisión externa.
