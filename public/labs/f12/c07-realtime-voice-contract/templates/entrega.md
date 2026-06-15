# Entrega del kit F12 C07

## Resultado de ejecución

- Resultado de `make run`:
- Resultado de `make test`:
- Caso que he modificado:

## Auditoría de voz

| Caso | Decisión original | Decisión tras mi cambio | Por qué |
|---|---|---|---|
| q01_estado_beca | answer |  |  |
| q02_ruido_pasillo | ask_repeat |  |  |
| q03_interrupcion_usuario | stop_and_answer |  |  |
| q04_datos_sensibles | answer |  |  |
| q05_accion_con_confirmacion | confirm_before_tool |  |  |

## Cambio técnico defendible

Describe qué has cambiado: umbral de WER, silencio de endpointing, latencia máxima, política de confirmación, redacción de PII o tiempos de barge-in.

## Evidencia

Pega aquí las líneas relevantes de:

- `output/realtime_voice_report.md`
- `output/latency_budget.csv`
- `output/turn_cards/*.json`

## Qué llevaría a producción

Explica qué añadirías antes de poner esto delante de usuarios: trazas, consentimiento, evaluación con acentos, pruebas de ruido, confirmación de herramientas, retención de audio o SLOs.
