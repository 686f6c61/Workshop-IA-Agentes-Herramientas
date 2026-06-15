# F12 C10 · Multimodal Eval Harness

Este laboratorio acompaña el capítulo 10 del facsímil 12. Simula una evaluación multimodal completa: documentos, gráficos, imágenes, vídeo, audio, RAG multimodal y trazas de computer use.

La idea no es “sacar un accuracy bonito”. La idea es separar calidad de respuesta, cobertura de evidencia, claims no soportados, seguridad, coste, latencia y slices. Eso es lo que necesita un equipo antes de publicar un sistema multimodal.

## Ejecutar

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

## Casos incluidos

| Caso | Modalidad | Qué fuerza a practicar |
|---|---|---|
| `doc_invoice_total` | Documento | Extracción numérica con evidencia. |
| `chart_becas_growth` | Chart | Error de cálculo aunque la lectura visual sea parcial. |
| `image_lab_safety` | Imagen | Grounding visual de una señal. |
| `video_alarm_timestamp` | Vídeo | Localización temporal con IoU de intervalo. |
| `audio_noisy_cancel` | Audio | Intención y baja confianza por ruido. |
| `rag_pdf_slide_policy` | Mixto | RAG multimodal con evidencia incompleta. |
| `computer_use_send_trace` | UI trace | Trayectoria y permiso, no solo estado final. |
| `document_pii_refusal` | Documento | Privacidad y negativa/redacción. |

## Qué genera

| Archivo | Qué contiene |
|---|---|
| `output/eval_report.md` | Informe humano de casos, slices y decisión. |
| `output/eval_report.json` | Informe estructurado. |
| `output/case_scores.csv` | Score por caso. |
| `output/slice_scores.csv` | Score por slice. |
| `output/annotation_queue.csv` | Casos que necesitan revisión humana. |
| `output/regression_gate.md` | Gate de publicación/regresión. |
| `output/regression_gate.json` | Gate estructurado. |
| `output/multimodal_eval_dashboard.svg` | Panel visual firmado. |

## Qué deberías tocar

1. Abre `data/eval_cases.json`.
2. Revisa `chart_becas_growth` y comprueba por qué falla aunque cite parte del gráfico.
3. Revisa `video_alarm_timestamp` y mira la métrica temporal.
4. Revisa `rag_pdf_slide_policy` y localiza el claim no soportado.
5. Ejecuta `make run`.
6. Abre `output/annotation_queue.csv`.
7. Decide qué casos deberían pasar a anotación humana.
8. Cambia `contracts/eval_policy.json` y baja `min_evidence_score`.
9. Ejecuta otra vez y mira si aceptarías publicar con ese cambio.
10. Añade un caso nuevo de tu producto real.

## Qué te llevas

Una evaluación multimodal seria no se resume en accuracy. Necesitas responder estas preguntas: ¿la respuesta es correcta?, ¿cita evidencia suficiente?, ¿hay claims no soportados?, ¿qué slice falla?, ¿cuánto cuesta?, ¿cuánto tarda?, ¿qué casos deben ir a revisión humana?

El artefacto profesional reutilizable es un mini harness de release: `contracts/eval_policy.json` fija umbrales, `data/eval_cases.json` contiene casos con evidencias, `ops/run_multimodal_eval.py` genera scores y `output/regression_gate.md` resume si publicar, revisar o bloquear. Si mañana tienes que evaluar un flujo con PDFs, gráficos, vídeo o pantalla, puedes mantener la misma estructura y cambiar los casos.

## Variantes para hacerlo tuyo

1. Añade un caso real en `data/eval_cases.json` con `case_id`, `slice_tags`, `expected.evidence_ids` y `model_output.claims`.
2. Cambia `contracts/eval_policy.json` para endurecer `min_evidence_score` si tu aplicación exige citas completas.
3. Añade un slice nuevo, por ejemplo `low_resolution_ocr`, `long_video`, `spanish_audio_noise` o `external_submit`.
4. Compara dos versiones de una misma salida copiando el JSON, ejecutando `make run` y revisando `output/case_scores.csv`.
5. Usa `templates/entrega.md` para documentar qué publicarías y qué bloquearías.

## Rúbrica rápida

| Nivel | Qué debe entregar |
|---|---|
| Mínimo | Ejecuta `make run`, ejecuta `make test` y explica dos casos de `output/eval_report.md`. |
| Bueno | Añade un caso realista, justifica sus evidencias y explica qué cambia en `output/annotation_queue.csv`. |
| Excelente | Diseña un slice nuevo, ajusta `contracts/eval_policy.json`, compara antes/después y defiende una decisión de release con `output/regression_gate.md`. |

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `F12 C10 · Multimodal Eval Harness`.

### Qué contiene

- `README.md`: esta guía.
- `Makefile`: entrada única para ejecutar y validar.
- `requirements.txt`: dependencias declaradas; usa biblioteca estándar.
- `contracts/eval_policy.json`: gates de calidad, evidencia, coste y latencia.
- `data/eval_cases.json`: casos multimodales evaluables.
- `schemas/eval_case_schema.json`: contrato mínimo de caso.
- `ops/run_multimodal_eval.py`: evaluador ejecutable.
- `templates/eval_brief.md`: plantilla editable para preparar una evaluación propia.
- `templates/entrega.md`: plantilla de entrega para justificar ejecución, decisión y límites.
- `tests/test_eval_harness.py`: tests de reproducibilidad.
- `output/`: salidas generadas o esperadas.

### Ejecutar desde cero

```bash
make run
make test
```

### Qué mirar antes de entregar

- `output/eval_report.md`
- `output/case_scores.csv`
- `output/slice_scores.csv`
- `output/annotation_queue.csv`
- `output/regression_gate.md`
- `output/multimodal_eval_dashboard.svg`

### Criterio de validación

El kit está completo cuando se puede descargar, extraer, ejecutar con `make run`, validar con `make test` y explicar por qué cada caso pasa, queda en revisión o bloquea publicación.
<!-- zip-quality-audit:end -->
