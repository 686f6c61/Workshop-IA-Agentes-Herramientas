# Decisión CSP

Decisión: `solucion_valida`.

| Sesión | Hora | Sala |
|---|---|---|
| `practica` | `lun_11` | `Lab` |
| `tutoria` | `mar_09` | `Aula` |
| `repaso` | `lun_09` | `Aula` |

## Por qué cumple

- No hay dos sesiones en la misma hora.
- `practica` queda en `Lab`.
- `repaso` ocurre antes que `practica`.
- `tutoria` queda en martes.

## Lectura técnica

La búsqueda deja `54` eventos de traza. Elegir antes las variables más restringidas reduce ramas inútiles y hace visible la poda.
