# Decisión: primera acción del agente

Caso: `checkout-page-fails`.

Objetivo: Encontrar la primera acción razonable para investigar un fallo de carga en checkout.

## Estado inicial

- El usuario informa de pantalla en blanco al abrir /checkout.
- No hay traza de error copiada todavía.
- No se ha ejecutado ningún test mínimo.

## Contrato de ranking

- Coste operativo: peso 1.0.
- Incertidumbre restante: peso 1.0.
- Riesgo: peso 2.0.
- Primero se aplican bloqueos duros; después se rankean solo acciones elegibles.

## Acción recomendada

**Leer consola del navegador** (`read_browser_console`) con score 3.0.

Por qué: Abrir la página y recoger el primer error de consola o red.

Observación esperada: Error exacto de JavaScript, recurso 404 o fallo de red.

## Ranking de acciones elegibles

| Acción | G | H | R | Score | Tokens | Latencia | Observación esperada |
|---|---:|---:|---:|---:|---:|---:|---|
| Leer consola del navegador | 1 | 2 | 0 | 3.0 | 600 | 15s | Error exacto de JavaScript, recurso 404 o fallo de red. |
| Ejecutar smoke test de checkout | 3 | 2 | 0 | 5.0 | 800 | 45s | Reproducción automática y punto aproximado de fallo. |
| Pedir captura al usuario | 2 | 4 | 0 | 6.0 | 400 | 60s | Contexto visual, navegador y mensaje visible. |
| Mirar logs del servidor | 2 | 2 | 1 | 6.0 | 900 | 30s | Excepción de backend, timeouts o ausencia de errores servidor. |
| Buscar documentación externa | 4 | 3 | 1 | 9.0 | 1400 | 60s | Issue, changelog o aviso de proveedor relevante. |

## Acciones bloqueadas

| Acción | Motivo |
|---|---|
| Editar componente de checkout | riesgo alto sin aprobación; acción destructiva sin evidencia previa |
| Consultar pedidos de producción | riesgo alto sin aprobación; requiere permiso para datos sensibles |

## Criterios de parada

- Responder solo si hay evidencia suficiente y el riesgo residual es bajo.
- Pedir aprobación si la siguiente acción requiere datos sensibles o modifica código sin prueba mínima.
- Escalar si se agota el presupuesto de acciones sin reducir la incertidumbre.

## Lectura técnica

- Esta política no intenta reemplazar al LLM: acota su comportamiento operativo.
- Una acción destructiva no compite en el ranking si no cumple precondiciones.
- El score bajo no convierte una acción sensible en segura; para eso están los bloqueos duros.
- La traza permite revisar si el agente investigó con evidencia o si actuó por impulso.
