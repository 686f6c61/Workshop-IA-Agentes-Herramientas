# Evaluación de detectores multimodales

Este informe separa dos preguntas que suelen mezclarse: qué entidades debería detectar el sistema y qué entidades detectó por encima del umbral.

## Métricas por entidad

| Entidad | TP | FP | FN | Precision | Recall | F2 | Objetivo recall |
|---|---:|---:|---:|---:|---:|---:|---|
| `ACCESS_TOKEN_FRAGMENT` | 1 | 0 | 0 | 1.0 | 1.0 | 1.0 | True |
| `ADDRESS` | 1 | 0 | 0 | 1.0 | 1.0 | 1.0 | True |
| `API_KEY` | 1 | 0 | 0 | 1.0 | 1.0 | 1.0 | True |
| `COOKIE` | 0 | 0 | 1 | 1.0 | 0.0 | 0.0 | True |
| `DNI_NIE` | 1 | 0 | 1 | 1.0 | 0.5 | 0.5556 | False |
| `EMAIL` | 2 | 0 | 0 | 1.0 | 1.0 | 1.0 | True |
| `FACE` | 1 | 0 | 1 | 1.0 | 0.5 | 0.5556 | False |
| `GPS_LOCATION` | 0 | 0 | 1 | 1.0 | 0.0 | 0.0 | False |
| `HEALTH` | 0 | 0 | 1 | 1.0 | 0.0 | 0.0 | False |
| `LICENSE_PLATE` | 1 | 0 | 0 | 1.0 | 1.0 | 1.0 | True |
| `PHONE` | 1 | 0 | 0 | 1.0 | 1.0 | 1.0 | True |
| `PROMPT_INJECTION` | 1 | 0 | 0 | 1.0 | 1.0 | 1.0 | True |
| `STUDENT_ID` | 1 | 0 | 0 | 1.0 | 1.0 | 1.0 | True |

## Muestras que necesitan revisión

| Muestra | Modalidad | Falsos negativos | Falsos positivos | Revisión |
|---|---|---|---|---|
| `ocr_low_res_partial_id` | `document` | DNI_NIE | none | True |
| `image_exif_location` | `image` | GPS_LOCATION | none | True |
| `audio_health_low_confidence` | `audio` | HEALTH | none | True |
| `video_license_plate` | `video` | FACE | none | True |
| `eval_token_fragment` | `eval_dataset` | COOKIE | none | False |

## Lectura

- En PII de alto impacto suele doler más el falso negativo que el falso positivo.
- Si no detectas `GPS_LOCATION`, `HEALTH`, `API_KEY` o `ACCESS_TOKEN_FRAGMENT`, no tienes un problema estético: tienes un posible incidente.
- La métrica útil no vive en abstracto; debe estar separada por entidad, modalidad y tipo de fallo.
