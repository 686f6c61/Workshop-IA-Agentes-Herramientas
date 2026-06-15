# F12 C06 · Auditoría de RAG multimodal

Este laboratorio acompaña el capítulo 06 del facsímil 12. La idea no es llamar a un proveedor externo ni presumir de embeddings: es construir una práctica reproducible que obliga a pensar como ingeniería.

El sistema recibe preguntas y recupera evidencias desde varias modalidades:

- texto documental;
- página visual;
- tabla;
- figura;
- estado operativo;
- señales de seguridad.

La salida no se queda en “top 5 resultados”. El kit calcula cobertura de evidencias, cobertura de modalidades, precisión contextual, instrucciones visuales no confiables y decisión final: `answer`, `review` o `block`.

Además incluye `data/qrels.json`, con juicios de relevancia graduados por consulta. Eso permite medir `nDCG@k` y `MRR`, dos métricas habituales de recuperación. No hace falta creerse que el ranking es bueno: se puede comprobar.

## Casos incluidos

| Caso | Qué fuerza a practicar | Resultado sano |
|---|---|---|
| `q01_beca_envio` | Mezclar política textual y estado operativo. | Responder que no puede enviarse todavía, con fuente y límite. |
| `q02_factura_total` | Recuperar tabla y página visual de una factura. | Calcular el total y citar line items. |
| `q03_piloto_metricas` | Usar gráfico y tabla de valores. | Explicar tendencia sin inventar datos. |
| `q04_instruccion_visual` | Detectar texto dentro de imagen que intenta mandar al sistema. | Bloquear la acción y tratarlo como dato no confiable. |
| `q05_pregunta_sin_evidencia` | No convertir evidencia parcial en decisión final. | Pedir revisión porque falta la resolución. |

## Ejecutar

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

`make run` genera salidas auditables. `make test` comprueba que el kit sigue funcionando después de descargarlo, extraerlo y modificarlo.

## Qué genera

| Archivo | Qué contiene |
|---|---|
| `output/multimodal_rag_report.md` | Informe humano con decisiones, métricas y evidencias. |
| `output/multimodal_rag_report.json` | Informe estructurado para CI o revisión. |
| `output/retrieved_contexts.csv` | Ranking por consulta, modalidad, fuente y score. |
| `output/answer_cards/*.json` | Respuestas finales con evidencias y límites. |
| `output/multimodal_rag_pipeline.svg` | Diagrama generado con firma del proyecto. |

## Qué deberías mirar

1. Abre `data/rag_queries.json` y revisa `required_evidence`.
2. Abre `data/qrels.json` y mira qué fuentes deberían aparecer arriba.
3. Ejecuta `make run`.
4. Abre `output/retrieved_contexts.csv` y mira qué fuentes entraron en cada `top_k`.
5. Abre `output/answer_cards/q04_instruccion_visual.json` y comprueba que el sistema bloquea.
6. Añade una fuente nueva en `data/multimodal_corpus.json`.
7. Repite la ejecución y observa si cambian `recall_at_k`, `ndcg_at_k`, `mrr`, `modality_coverage` y `context_precision`.
8. Cambia `minimum_context_precision` en `contracts/multimodal_rag_policy.json` y explica cuándo el sistema debería pedir revisión.

## Cambios útiles

- Añade una segunda tabla de factura con un total contradictorio y obliga al sistema a revisar.
- Crea un caso donde una imagen sea útil para encontrar la página, pero la respuesta final deba citar una tabla.
- Cambia `top_k` de 5 a 3 y observa qué evidencia se pierde.
- Añade una modalidad nueva, por ejemplo `audio_transcript`, y decide si la tratarías como texto o como fuente multimodal independiente.
- Convierte `low_visual_quality` en bloqueo si tu dominio no tolera documentos ilegibles.

## Qué te llevas

Un RAG multimodal serio no es “meter imágenes en un vector store”. Es decidir qué representa cada modalidad, cómo se recupera, cómo se re-rankea, qué evidencia se exige y cuándo se debe parar. Este kit deja esa lógica en archivos que puedes tocar.

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `F12 C06 · Auditoría de RAG multimodal`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; este kit usa la biblioteca estándar de Python.
- `data/multimodal_corpus.json`: corpus multimodal editable.
- `data/rag_queries.json`: preguntas, evidencias obligatorias y decisiones esperadas.
- `data/qrels.json`: juicios de relevancia graduados para evaluar ranking.
- `data/docs/*`: documentos de texto y tablas CSV.
- `data/pages/*.svg`: páginas, factura, gráfico y anexo visual sintético.
- `contracts/multimodal_rag_policy.json`: política de recuperación, gates y evidencias.
- `schemas/rag_answer_schema.json`: contrato de salida.
- `ops/run_multimodal_rag_audit.py`: código ejecutable.
- `templates/entrega.md`: plantilla editable.
- `tests/test_lab_contract.py`: tests de reproducibilidad.
- `output/`: salidas generadas o esperadas.

### Ejecutar desde cero

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

### Qué mirar antes de entregar

- `output/multimodal_rag_report.md`: informe humano.
- `output/retrieved_contexts.csv`: ranking por consulta.
- `output/answer_cards/q01_beca_envio.json`: respuesta con política y estado operativo.
- `output/answer_cards/q04_instruccion_visual.json`: bloqueo por instrucción visual.
- `output/answer_cards/q05_pregunta_sin_evidencia.json`: revisión por evidencia insuficiente.
- `output/multimodal_rag_pipeline.svg`: figura del pipeline.

### Qué entregar

Una entrega útil debe incluir resultado de `make test`, una modificación razonada en `data/rag_queries.json`, `data/multimodal_corpus.json` o `contracts/multimodal_rag_policy.json`, y una explicación de por qué la decisión final es `answer`, `review` o `block`.

La entrega buena debería defender una decisión técnica incómoda: bajar `top_k`, añadir una fuente, pedir revisión por falta de evidencia, bloquear una instrucción visual o separar índice textual de índice visual.

### Criterio de validación

El kit está completo cuando se puede descargar, extraer, ejecutar con `make run`, validar con `make test` y explicar sin depender de ninguna carpeta externa.
<!-- zip-quality-audit:end -->
