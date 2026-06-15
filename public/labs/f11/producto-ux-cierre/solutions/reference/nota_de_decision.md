# Decisión de producto con IA

## 1. Problema

**Usuario principal:** personal académico que revisa solicitudes de matrícula.

**Tarea concreta:** revisar una solicitud, localizar normativa aplicable, redactar una respuesta sustentada y escalar casos incompletos.

**Situación actual:** la persona busca normativa, consulta expediente, redacta respuesta y decide si necesita revisión. El flujo funciona, pero consume tiempo y deja trazabilidad desigual.

**Qué no vamos a resolver:** no cerraremos solicitudes automáticamente, no modificaremos expedientes y no responderemos si falta evidencia documental suficiente.

## 2. Baseline sin IA

**Alternativa propuesta:** buscador de normativa con filtros por curso, plantilla manual y checklist de revisión.

**Por qué no basta o dónde se queda corta:** reduce búsqueda, pero no ayuda a comparar fuentes, redactar respuesta ni detectar huecos de evidencia.

**Métrica del baseline:** tiempo medio hasta respuesta sustentada, recontacto en 7 días y porcentaje de respuestas con fuente citada.

## 3. Intervención con IA

**Tipo de intervención:** RAG con citas, salida estructurada y abstención cuando falta soporte.

**Capacidad mínima necesaria:** recuperar normativa vigente, mostrar fuente, redactar respuesta revisable y declarar límites.

**Datos o sistemas que usa:** normativa, expediente, registro de pagos y trazas del flujo.

**Nivel de autonomía:** sugerir y redactar; no ejecutar acciones externas.

## 4. Métrica norte

**Métrica principal:** solicitudes resueltas con evidencia suficiente y sin recontacto en 7 días.

**Por qué representa valor:** combina utilidad, calidad documental y efecto posterior sobre soporte.

**Antimétrica que evitaremos optimizar:** número de conversaciones con el asistente. Más uso puede significar más confusión, no más valor.

## 5. Guardrails

| Capa | Métrica | Umbral mínimo | Fuente |
|---|---|---:|---|
| Calidad | groundedness | 0.85 | eval snapshot |
| Calidad | abstención correcta | 0.70 | eval snapshot |
| UX | recovery score | 0.75 | UX review |
| Coste | coste por tarea | 0.45 EUR | unit economics |
| Operación | trace coverage | 0.95 | trace contract |
| Gobernanza | evidencias obligatorias | todas | release policy |

## 6. Unidad económica

| Componente | Estimación por tarea | Cómo se calcula |
|---|---:|---|
| Modelo | 0.09 EUR | tokens y reintentos esperados |
| Retrieval / embeddings | 0.04 EUR | búsqueda, reranking e índice |
| Tools / APIs | 0.03 EUR | consultas internas |
| Observabilidad | 0.02 EUR | logs, métricas y trazas |
| Revisión humana esperada | 0.08 EUR | probabilidad de escalado por coste medio |
| Soporte / recontactos | 0.03 EUR | recontactos esperados |
| Mantenimiento prorrateado | 0.02 EUR | coste mensual repartido |
| **Total** | **0.31 EUR** | suma de componentes |

**Margen útil esperado:** 0.581 EUR por tarea en la candidata `matricula_rag_assistant`.

## 7. Análisis de sensibilidad

**p_ok mínimo aceptable:** 0.282. Se calcula como `0.31 / 1.10`. Esa cifra solo marca el suelo económico; para publicar exigiría margen adicional porque el coste de cola, la revisión humana y los recontactos no se ven completos en la media.

**Variable que más rompe la decisión:** coste P95 en solicitudes complejas y groundedness en el slice de pagos pendientes. Si el retrieval recupera normativa incompleta, el sistema puede redactar bien pero sostener mal la respuesta.

| Escenario | p_ok | Coste total | Valor esperado | Decisión |
|---|---:|---:|---:|---|
| Base | 0.81 | 0.31 EUR | 0.581 EUR | Pilotar limitado si pasan UX y evidencias. |
| Coste alto por reintentos | 0.81 | 0.55 EUR | 0.341 EUR | Pilotar, pero revisar prompts, retrieval y tools. |
| Calidad baja en slices críticos | 0.70 | 0.31 EUR | 0.460 EUR | Piloto condicionado a mejorar dataset y abstención. |
| Calidad baja y coste alto | 0.60 | 0.55 EUR | 0.110 EUR | No escalar; repetir evaluación antes de ampliar. |
| Escenario de ruptura | 0.50 | 0.70 EUR | -0.150 EUR | No pilotar en ese alcance. |

## 8. Slices críticos

| Slice | Por qué importa | Métrica mínima | Decisión si falla |
|---|---|---:|---|
| pagos pendientes | Puede cambiar el siguiente paso de la solicitud. | groundedness >= 0.85 | limitar a revisión |
| fuente incompleta | El sistema debe abstenerse. | abstención >= 0.70 | no responder |
| caso fuera de alcance | Evita prometer más de lo que sabe. | recovery score >= 0.75 | derivar a flujo manual |

## 9. Evidencias obligatorias

- [x] Árbol de métricas.
- [x] Snapshot de evaluación.
- [x] Unidad económica.
- [x] Revisión de privacidad.
- [x] Contrato de trazas.
- [x] Plan de retorno.
- [x] Caminos de recuperación UX.

## 10. Criterios de no construir

No construiremos o no pilotaremos si:

1. La alternativa sin IA alcanza el mismo valor con menor coste y menor variabilidad.
2. La abstención cae por debajo del umbral en casos sin fuente suficiente.
3. Falta evidencia de privacidad, trazas o recuperación UX.

## 11. Plan de piloto

**Alcance:** solicitudes de matrícula con normativa recuperable, expediente consultable y sin escritura automática en sistemas de gestión.

**Duración o volumen:** 2 semanas o 200 solicitudes, lo que ocurra antes.

**Población:** personal académico voluntario y usuarios internos con canal de feedback directo.

**Métrica norte del piloto:** solicitudes resueltas con evidencia suficiente y sin recontacto en 7 días.

**Guardrails de parada:** groundedness < 0.85, abstención correcta < 0.70, recovery score < 0.75, coste por tarea > 0.45 EUR, coste P95 fuera de presupuesto o trace coverage < 0.95 durante dos ventanas consecutivas.

**Responsables:** producto define alcance y decisión; ingeniería mantiene trazas, gates y fallback; datos/evaluación revisa slices y dataset; UX valida estados y recuperación; privacidad/gobernanza revisa permisos y retención; operación académica mide recontactos.

**Ritmo de revisión:** semanal durante el piloto y revisión final con paquete de evidencias antes de ampliar alcance.

## 12. Decisión

**Decisión:** `pilot_limited`.

**Alcance:** solicitudes con evidencia documental recuperable, sin cierre automático.

**Condiciones antes de piloto:** mantener baseline, revisar casos incompletos y observar coste por slice.

**Condición de retirada:** caída de groundedness, abstención o recuperación UX por debajo de umbral durante dos ventanas consecutivas.

**Responsable de revisar la decisión:** equipo de producto, ingeniería y operación académica.

**Fecha de próxima revisión:** al cierre de la primera ventana de piloto.
