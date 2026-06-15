# Runbook de incidente multimodal

## Cuándo usarlo

Usa este runbook si una imagen, documento, audio, vídeo, RAG o traza de pantalla contiene PII, secreto, prompt injection visual o salida externa no autorizada.

## Primeros 30 minutos

1. Congela la run y conserva `output/risk_report.json`.
2. Identifica modalidad, destino, storage y owner.
3. Si hay API key o secreto, revoca antes de debatir si la salida fue visible.
4. Redacta o elimina artefactos derivados: screenshots, OCR, transcript, frames, logs y eval fixtures.
5. Abre ticket de seguridad con case_id, evidencia y decisión.

## Casos bloqueados en esta ejecución

- `rag_confidential_slide`: RAG multimodal recupera una slide interna confidencial -> Redactar información interna, revisar acceso de la fuente y bloquear publicación.
- `ui_api_key_prompt_injection`: Captura de pantalla con API key y texto que intenta dar órdenes -> Revocar secreto, redactar captura, abrir incidente y bloquear publicación.
- `computer_use_external_submit`: Traza de computer use intenta enviar captura a un webhook externo -> Revisar egress policy: el destino no puede recibir esta modalidad.
- `eval_reconstructible_token_fragment`: Fixture de evaluación con fragmento de token reconstruible -> Revocar secreto, redactar captura, abrir incidente y bloquear publicación.

## Cierre

- Añade un caso de regresión redactado.
- Revisa egress policy y controles faltantes.
- Documenta retención y borrado.
- Si afectó a datos personales, activa revisión de privacidad.
