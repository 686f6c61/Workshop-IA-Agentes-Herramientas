# Decisión: ¿qué principio de IA domina el caso?

El objetivo no es encasillar el proyecto en una palabra. El objetivo es detectar qué pieza manda la decisión técnica y qué artefactos hacen falta antes de construir.

| Caso | Principio dominante | Principios secundarios | Artefactos mínimos | Revisión |
|---|---|---|---|---|
| Clasificar tickets de soporte académico | `supervised_learning` | `unsupervised_learning`, `scaling_cost` | dataset etiquetado + métrica de error, perfilado de clusters + validación de dominio, eval pequeña + curva coste/calidad/latencia | sin bloqueo inicial |
| Descubrir segmentos de alumnos sin etiquetas previas | `unsupervised_learning` | - | perfilado de clusters + validación de dominio | sin bloqueo inicial |
| Asistente que responde sobre becas y sabe abstenerse | `post_training` | `supervised_learning`, `unsupervised_learning`, `attention_context`, `scaling_cost` | pares de preferencia + política de rechazo, dataset etiquetado + métrica de error, perfilado de clusters + validación de dominio, presupuesto de contexto + estrategia de recuperación, eval pequeña + curva coste/calidad/latencia | pocos ejemplos etiquetados: valida antes de prometer fine-tuning; impacto alto: exige evaluación y revisión antes de publicar |
| Resumir contratos largos con cláusulas cruzadas | `attention_context` | `supervised_learning`, `unsupervised_learning`, `post_training`, `scaling_cost` | presupuesto de contexto + estrategia de recuperación, dataset etiquetado + métrica de error, perfilado de clusters + validación de dominio, pares de preferencia + política de rechazo, eval pequeña + curva coste/calidad/latencia | pocos ejemplos etiquetados: valida antes de prometer fine-tuning; impacto alto: exige evaluación y revisión antes de publicar |
| Elegir modelo local para respuestas internas de baja latencia | `scaling_cost` | `supervised_learning`, `unsupervised_learning`, `post_training` | eval pequeña + curva coste/calidad/latencia, dataset etiquetado + métrica de error, perfilado de clusters + validación de dominio, pares de preferencia + política de rechazo | sin bloqueo inicial |

## Lectura técnica

### Clasificar tickets de soporte académico

Principio dominante: `supervised_learning`.
Por qué: hay suficientes ejemplos etiquetados para medir error; hay mucho dato sin etiquetar para explorar estructura; hay que comparar calidad, latencia y coste.
Siguiente lugar del facsímil: capítulo 4 y capítulo 6.

### Descubrir segmentos de alumnos sin etiquetas previas

Principio dominante: `unsupervised_learning`.
Por qué: hay mucho dato sin etiquetar para explorar estructura.
Siguiente lugar del facsímil: facsímil 8.

### Asistente que responde sobre becas y sabe abstenerse

Principio dominante: `post_training`.
Por qué: hay mucho dato sin etiquetar para explorar estructura; el comportamiento deseado depende de preferencias y abstención; el presupuesto de contexto condiciona coste y recuperación; hay que comparar calidad, latencia y coste.
Siguiente lugar del facsímil: facsímil 3 y facsímil 4.
Cuidado: pocos ejemplos etiquetados: valida antes de prometer fine-tuning; impacto alto: exige evaluación y revisión antes de publicar.

### Resumir contratos largos con cláusulas cruzadas

Principio dominante: `attention_context`.
Por qué: hay mucho dato sin etiquetar para explorar estructura; el presupuesto de contexto condiciona coste y recuperación; hay que comparar calidad, latencia y coste.
Siguiente lugar del facsímil: facsímil 3 y facsímil 4.
Cuidado: pocos ejemplos etiquetados: valida antes de prometer fine-tuning; impacto alto: exige evaluación y revisión antes de publicar.

### Elegir modelo local para respuestas internas de baja latencia

Principio dominante: `scaling_cost`.
Por qué: hay suficientes ejemplos etiquetados para medir error; hay mucho dato sin etiquetar para explorar estructura; la generación tiene objetivo estricto de latencia.
Siguiente lugar del facsímil: capítulo 10 y facsímil 7.

