# Decisión de producto con IA

Este documento funciona como PRD breve y ADR de IA. Su objetivo es dejar una decisión revisable: qué problema se resuelve, por qué se propone IA, qué baseline compite, cómo se mide, qué cuesta y cuándo no se publica.

## 1. Problema

**Usuario principal:**  
<!-- Ejemplo: personal académico que revisa solicitudes de matrícula. -->

**Tarea concreta:**  
<!-- Describe la tarea sin nombrar IA. -->

**Situación actual:**  
<!-- Cómo se resuelve hoy, cuánto tarda, dónde duele, qué evidencia existe. -->

**Qué no vamos a resolver:**  
<!-- Límites explícitos. Si no hay límites, la evaluación se vuelve borrosa. -->

## 2. Baseline sin IA

**Alternativa propuesta:**  
<!-- Regla, buscador, formulario, plantilla, SQL, workflow manual, dashboard. -->

**Por qué no basta o dónde se queda corta:**  

**Métrica del baseline:**  
<!-- Tiempo, precisión, coste, recontacto, escalado, satisfacción, trazas. -->

## 3. Intervención con IA

**Tipo de intervención:**  
<!-- Prompt, salida estructurada, RAG, tool, workflow, agente, política. -->

**Capacidad mínima necesaria:**  
<!-- Qué debe hacer la IA y qué no debe hacer. -->

**Datos o sistemas que usa:**  

**Nivel de autonomía:**  
<!-- Sugerir, redactar, consultar, preparar acción, ejecutar con aprobación, ejecutar automáticamente. -->

## 4. Métrica norte

**Métrica principal:**  
<!-- Debe representar valor real de la tarea, no solo uso. -->

**Por qué representa valor:**  

**Antimétrica que evitaremos optimizar:**  
<!-- Ejemplo: número de conversaciones, longitud de respuesta, menos escalados sin mirar calidad. -->

## 5. Guardrails

| Capa | Métrica | Umbral mínimo | Fuente |
|---|---|---:|---|
| Calidad |  |  |  |
| UX |  |  |  |
| Coste |  |  |  |
| Operación |  |  |  |
| Gobernanza |  |  |  |

## 6. Unidad económica

| Componente | Estimación por tarea | Cómo se calcula |
|---|---:|---|
| Modelo |  |  |
| Retrieval / embeddings |  |  |
| Tools / APIs |  |  |
| Observabilidad |  |  |
| Revisión humana esperada |  |  |
| Soporte / recontactos |  |  |
| Mantenimiento prorrateado |  |  |
| **Total** |  |  |

**Margen útil esperado:**  
<!-- p_ok * valor - coste_total. -->

## 7. Análisis de sensibilidad

**p_ok mínimo aceptable:**  
<!-- coste_total / valor_por_tarea. Explica si usarías un margen adicional. -->

**Variable que más rompe la decisión:**  
<!-- Coste P95, groundedness, abstención, revisión humana, recontacto, latencia, volumen, slice concreto. -->

| Escenario | p_ok | Coste total | Valor esperado | Decisión |
|---|---:|---:|---:|---|
| Base |  |  |  |  |
| Coste alto |  |  |  |  |
| Calidad baja |  |  |  |  |
| Escenario de ruptura |  |  |  |  |

## 8. Slices críticos

| Slice | Por qué importa | Métrica mínima | Decisión si falla |
|---|---|---:|---|
|  |  |  |  |

## 9. Evidencias obligatorias

- [ ] Árbol de métricas.
- [ ] Snapshot de evaluación.
- [ ] Unidad económica.
- [ ] Revisión de privacidad.
- [ ] Contrato de trazas.
- [ ] Plan de retorno.
- [ ] Caminos de recuperación UX.

## 10. Criterios de no construir

No construiremos o no pilotaremos si:

1. 
2. 
3. 

## 11. Plan de piloto

**Alcance:**  
<!-- Qué casos entran y qué casos quedan fuera. -->

**Duración o volumen:**  
<!-- Ejemplo: 2 semanas o 200 tareas, lo que ocurra antes. -->

**Población:**  
<!-- Usuarios internos, beta controlada, equipo concreto, segmento de bajo riesgo. -->

**Métrica norte del piloto:**  

**Guardrails de parada:**  
<!-- Umbrales concretos de calidad, UX, coste, operación y gobernanza. -->

**Responsables:**  
<!-- Producto, ingeniería, evaluación/datos, UX, privacidad/gobernanza, operación. -->

**Ritmo de revisión:**  

## 12. Decisión

**Decisión:**  
<!-- pilot_limited, pilot_with_conditions, do_not_pilot. -->

**Alcance:**  

**Condiciones antes de piloto:**  

**Condición de retirada:**  

**Responsable de revisar la decisión:**  

**Fecha de próxima revisión:**  
