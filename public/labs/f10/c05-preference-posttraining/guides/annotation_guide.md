# Guía de anotación para preferencias

Esta guía acompaña el capítulo 05 del facsímil 10. Su objetivo es que dos personas distintas puedan anotar pares de preferencia con criterio parecido.

Un par de preferencia no es una opinión suelta. Es una decisión técnica sobre una tarea concreta.

## Unidad mínima

Cada par debe incluir:

| Campo | Regla |
|---|---|
| `prompt` | Debe parecerse a una entrada real de producción. |
| `chosen` | Respuesta preferida. |
| `rejected` | Respuesta menos preferida, pero plausible. |
| `preference_reason` | Motivo concreto de la preferencia. |
| `task_family` | Familia: RAG, código, SQL, soporte, herramientas, privacidad, etc. |
| `rubric_scores` | Puntuaciones separadas: correctness, evidence, format, cost. |
| `agreement` | Acuerdo entre revisores o nivel de confianza. |
| `verifier_result` | Resultado de checker o grader si existe. |

## Rúbrica

| Dimensión | Pregunta |
|---|---|
| `correctness` | La respuesta resuelve la tarea sin errores importantes? |
| `evidence` | Usa evidencia, citas, logs, datos o cálculos cuando hacen falta? |
| `format` | Cumple el contrato de salida esperado? |
| `cost` | Resuelve sin longitud, pasos o llamadas innecesarias? |

No mezcles dimensiones en una sola frase. Si una respuesta gana por formato pero pierde por exactitud, el par debe revisarse.

## Pares que se aceptan

Acepta un par cuando:

1. La diferencia entre `chosen` y `rejected` se puede explicar.
2. La preferencia no depende solo de que una respuesta sea más larga.
3. El prompt contiene el contexto que el sistema tendrá en producción.
4. La respuesta preferida no contradice un verificador disponible.
5. El par pertenece a una familia de tarea que queremos mejorar.

## Pares que se descartan

Descarta un par cuando:

1. Las dos respuestas son equivalentes.
2. La preferida es solo más amable o más larga, sin ganar calidad.
3. El prompt no representa un caso real.
4. Hay desacuerdo fuerte y no se resuelve con una tercera revisión.
5. El verificador indica que la preferida rompe formato, cita o cálculo.

## Cómo escribir `preference_reason`

Mal:

```text
Me gusta más la primera.
```

Mejor:

```text
La primera cita el documento POL-TRAVEL-04, condiciona la respuesta al recibo y no afirma excepciones no recuperadas.
```

Mal:

```text
La respuesta es más completa.
```

Mejor:

```text
La respuesta incluye causa probable, comando de comprobación y siguiente acción; la rechazada solo recomienda revisar.
```

## Revision antes de entrenar

Antes de usar el dataset para DPO, ORPO, KTO, reward modeling o RLHF:

1. Ejecuta `ops/audit_preference_dataset.py`.
2. Revisa `pair_scorecard.csv`.
3. Corrige pares con margen negativo.
4. Separa train/eval por fecha o familia de tarea.
5. Guarda esta guía junto al snapshot del dataset.
