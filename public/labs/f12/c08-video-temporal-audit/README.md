# F12 C08 · Auditoría temporal de vídeo

Este laboratorio acompaña el capítulo 08 del facsímil 12. La práctica simula preguntas sobre vídeos usando frames sintéticos, OCR, transcript, objetos y segmentos temporales.

No llama a APIs externas. El objetivo es que puedas tocar las piezas de ingeniería que hacen que un sistema de vídeo sea auditable: muestreo, flujo de frames, extracción de eventos, límites temporales, orden, evidencia por frame, capacidad y decisión final.

La práctica tiene dos partes:

1. `ops/build_temporal_index.py` lee `data/frame_stream.csv` y construye un índice temporal de eventos.
2. `ops/run_video_temporal_audit.py` audita respuestas contra eventos esperados, tIoU, cobertura de evidencia y seguridad.

## Casos incluidos

| Caso | Qué fuerza a practicar | Resultado sano |
|---|---|---|
| `q01_demo_error_503` | Localizar evento visual y acción posterior. | Responder con timestamps y evidencia. |
| `q02_puerta_sin_badge` | Razonar sobre orden temporal. | Detectar que la puerta se abre antes de validar tarjeta. |
| `q03_linea_defecto` | Encontrar un defecto breve en una línea. | Citar segmento y frame clave. |
| `q04_instruccion_visual` | Bloquear texto visual que intenta mandar al sistema. | Tratarlo como dato no confiable. |
| `q05_sin_evidencia` | No inventar un evento que no aparece. | Pedir revisión por falta de evidencia. |

## Ejecutar

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

## Qué genera

| Archivo | Qué contiene |
|---|---|
| `output/video_temporal_report.md` | Informe humano con decisiones, métricas y fallos. |
| `output/video_temporal_report.json` | Informe estructurado para CI o revisión. |
| `output/temporal_index.json` | Eventos extraídos desde `data/frame_stream.csv`. |
| `output/temporal_index.csv` | Índice temporal exportado para revisión o BI. |
| `output/capacity_estimate.csv` | Estimación de frames y clips por hora con el muestreo observado. |
| `output/video_pipeline_manifest.json` | Pasos del pipeline y checks de ingeniería. |
| `output/temporal_eval_matrix.csv` | tIoU, error de frontera, cobertura, orden y decisión por caso. |
| `output/case_cards/*.json` | Respuesta final con segmentos, evidencias y límites. |
| `output/storyboards/*.svg` | Storyboards sintéticos de cada caso. |
| `output/video_temporal_pipeline.svg` | Diagrama generado con firma del proyecto. |

## Qué deberías mirar

1. Abre `contracts/video_temporal_policy.json`.
2. Ejecuta `make run`.
3. Mira `output/temporal_index.csv` y comprueba qué eventos han salido del flujo de frames.
4. Abre `output/capacity_estimate.csv` y estima cuánto crecería el coste si subes el fps muestreado.
5. Mira `output/temporal_eval_matrix.csv`.
6. Abre `output/case_cards/q02_puerta_sin_badge.json` y comprueba el orden temporal.
7. Abre `output/case_cards/q04_instruccion_visual.json` y verifica que no se obedece el texto visual.
8. Baja `min_tiou` de `0.5` a `0.2`.
9. Ejecuta otra vez y explica qué errores temporales empezarías a aceptar.
10. Cambia un frame de `q03_linea_defecto` para quitar `grieta` de `objects` y observa cómo cae la cobertura.
11. Añade una regla nueva en `event_extraction.rules` y comprueba si aparece en `output/temporal_index.json`.

## Cambios útiles

- Añade un caso donde el transcript dice una cosa y el frame muestra otra.
- Añade un evento que dure menos de un segundo y revisa si el muestreo lo pierde.
- Añade una relación de orden nueva: “A ocurre después de B, pero antes de C”.
- Convierte `q05_sin_evidencia` en `answer` añadiendo un frame con aprobación real y evidencia suficiente.
- Cambia `block_visual_instruction_override` y defiende por qué sería peligroso.

## Qué te llevas

Un sistema de vídeo no debe responder “lo vi en el vídeo” como si eso bastara. Debe decir en qué segmento, con qué frame, con qué señal y con qué límites. Si falta evidencia temporal, toca revisar.

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `F12 C08 · Auditoría temporal de vídeo`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; este kit usa la biblioteca estándar de Python.
- `contracts/video_temporal_policy.json`: umbrales de tIoU, fronteras, evidencias y seguridad.
- `schemas/video_answer_schema.json`: contrato mínimo de respuesta temporal.
- `data/frame_stream.csv`: flujo de frames simulado con OCR, objetos y transcript.
- `data/video_cases.json`: cinco casos con frames, eventos, predicciones y decisiones.
- `ops/build_temporal_index.py`: constructor de índice temporal desde frames.
- `ops/run_video_temporal_audit.py`: código ejecutable.
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

- `output/video_temporal_report.md`: informe humano.
- `output/temporal_index.csv`: índice temporal construido desde frames.
- `output/capacity_estimate.csv`: estimación de capacidad por hora.
- `output/temporal_eval_matrix.csv`: matriz de evaluación temporal.
- `output/case_cards/q01_demo_error_503.json`: respuesta con dos eventos ordenados.
- `output/case_cards/q04_instruccion_visual.json`: bloqueo por texto visual no confiable.
- `output/case_cards/q05_sin_evidencia.json`: revisión por falta de evidencia.
- `output/storyboards/q03_linea_defecto.svg`: storyboard de inspección.

### Qué entregar

Una entrega útil debe incluir resultado de `make test`, una modificación razonada en `data/frame_stream.csv`, `data/video_cases.json` o `contracts/video_temporal_policy.json`, y una explicación de por qué la decisión final es `answer`, `review` o `block`.

La entrega buena debería defender una decisión incómoda: bajar el muestreo y perder un defecto, aceptar un segmento con poca tIoU, bloquear una instrucción visual o pedir revisión aunque el usuario quiera una respuesta rápida.

### Criterio de validación

El kit está completo cuando se puede descargar, extraer, ejecutar con `make run`, validar con `make test` y explicar sin depender de ninguna carpeta externa.
<!-- zip-quality-audit:end -->
