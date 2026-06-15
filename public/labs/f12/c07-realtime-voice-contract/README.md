# F12 C07 · Contrato de voz en tiempo real

Este laboratorio acompaña el capítulo 07 del facsímil 12. La práctica simula un agente de voz que escucha, transcribe, decide si puede responder, gestiona interrupciones, protege datos sensibles y evita ejecutar herramientas peligrosas sin confirmación.

No llama a APIs externas. El objetivo es que puedas tocar las piezas de ingeniería: umbrales de ASR, VAD, latencia, barge-in, redacción de PII y política de tools.

## Casos incluidos

| Caso | Qué fuerza a practicar | Resultado sano |
|---|---|---|
| `q01_estado_beca` | Consulta normal con política y estado operativo. | Responder con límite y evidencias. |
| `q02_ruido_pasillo` | Ruido y WER alto. | Pedir repetición antes de cambiar datos. |
| `q03_interrupcion_usuario` | Barge-in mientras el agente habla. | Detener TTS y reabrir el turno. |
| `q04_datos_sensibles` | DNI y teléfono dictados por voz. | Redactar antes de guardar logs. |
| `q05_accion_con_confirmacion` | Tool destructiva sin confirmación explícita. | Pedir confirmación y revisión. |

## Ejecutar

Desde la carpeta extraída del ZIP:

```bash
make run
make test
```

## Qué genera

| Archivo | Qué contiene |
|---|---|
| `output/realtime_voice_report.md` | Informe humano con decisiones, métricas y fallos. |
| `output/realtime_voice_report.json` | Informe estructurado para CI o revisión. |
| `output/latency_budget.csv` | Latencias por caso: endpointing, primera voz, total y barge-in. |
| `output/voice_eval_matrix.csv` | Matriz de evaluación con WER, errores en slots críticos y estabilidad de parciales. |
| `output/turn_cards/*.json` | Contrato de salida por turno. |
| `output/audio/*.wav` | Audios sintéticos para comprobar que el ZIP no depende de rutas externas. |
| `output/realtime_voice_pipeline.svg` | Diagrama generado con firma del proyecto. |

## Qué deberías mirar

1. Abre `contracts/realtime_voice_policy.json`.
2. Ejecuta `make run`.
3. Mira `output/latency_budget.csv` y localiza qué caso no debería automatizarse.
4. Abre `output/voice_eval_matrix.csv` y mira qué ocurre cuando el slot `correo` se convierte en `color`.
5. Abre `output/turn_cards/q04_datos_sensibles.json` y comprueba que no quedan DNI ni teléfono en claro.
6. Abre `output/turn_cards/q03_interrupcion_usuario.json` y revisa `barge_in_stop_latency_ms`.
7. Cambia `max_wer_for_automatic_decision` de `0.18` a `0.35`.
8. Ejecuta otra vez y explica por qué permitir más WER puede ser peligroso en tools.

## Cambios útiles

- Añade un caso con acento, ruido o una palabra de dominio difícil.
- Baja `endpoint_silence_ms` y observa si el agente corta demasiado pronto.
- Añade una frase de confirmación explícita en `q05_accion_con_confirmacion` y decide si aun así exigirías revisión humana.
- Cambia `requires_tool` para que un caso solo responda sin actuar.
- Añade otro patrón de PII, por ejemplo número de expediente.

## Qué te llevas

La voz en tiempo real no se valida con una demo bonita. Se valida con contratos: cuándo se cierra el turno, cuánta incertidumbre tolera el ASR, qué latencia duele, qué ocurre cuando el usuario interrumpe y qué acciones no se ejecutan solo porque una transcripción lo parezca.

<!-- zip-quality-audit:start -->
## Guía operativa del ZIP

Esta sección audita el ZIP como lo recibirá un alumno. Todo lo citado aquí debe estar dentro de este archivo descargable de `F12 C07 · Contrato de voz en tiempo real`, no escondido en una ruta del repositorio.

### Qué contiene

- `README.md`: esta guía y la explicación del ejercicio.
- `Makefile`: entrada única para ejecutar y validar el kit con `make run` y `make test`.
- `requirements.txt`: dependencias declaradas; este kit usa la biblioteca estándar de Python.
- `contracts/realtime_voice_policy.json`: umbrales de audio, latencia, WER, barge-in, tools y privacidad.
- `schemas/voice_turn_schema.json`: contrato mínimo de salida por turno.
- `data/voice_cases.json`: cinco casos realistas de voz.
- `ops/run_realtime_voice_audit.py`: código ejecutable.
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

- `output/realtime_voice_report.md`: informe humano.
- `output/latency_budget.csv`: presupuesto de latencia por caso.
- `output/voice_eval_matrix.csv`: matriz de evaluación de WER, slots críticos y parciales.
- `output/turn_cards/q02_ruido_pasillo.json`: decisión de pedir repetición.
- `output/turn_cards/q03_interrupcion_usuario.json`: interrupción y parada de TTS.
- `output/turn_cards/q04_datos_sensibles.json`: transcripción redactada.
- `output/realtime_voice_pipeline.svg`: figura del pipeline.

### Qué entregar

Una entrega útil debe incluir resultado de `make test`, una modificación razonada en `data/voice_cases.json` o `contracts/realtime_voice_policy.json`, y una explicación de por qué la decisión final es `answer`, `ask_repeat`, `stop_and_answer`, `confirm_before_tool` o `review`.

La entrega buena debería defender una decisión incómoda: pedir repetición aunque el usuario tenga prisa, no ejecutar una tool destructiva, cortar una locución por barge-in o no guardar PII en claro.

### Criterio de validación

El kit está completo cuando se puede descargar, extraer, ejecutar con `make run`, validar con `make test` y explicar sin depender de ninguna carpeta externa.
<!-- zip-quality-audit:end -->
