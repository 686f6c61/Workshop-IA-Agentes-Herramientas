# Informe técnico de detección PII estilo Presidio

Este informe no conserva valores literales. Guarda entidad, campo, span, score, reconocedor, hash del valor y operador recomendado. La forma se parece a Presidio, pero el kit usa una simulación local sin dependencias para que pueda ejecutarse en cualquier máquina.

## Perfil de motor

- Motor: `presidio_style_demo`
- Idioma: `es`
- Entidades activas: `EMAIL_ADDRESS`, `PHONE_NUMBER`, `NATIONAL_ID`

## Hallazgos por entidad

| Entidad | Hallazgos | Operador recomendado |
|---|---:|---|
| `EMAIL_ADDRESS` | 3 | `hash` |
| `NATIONAL_ID` | 1 | `redact` |
| `PHONE_NUMBER` | 1 | `redact` |

## Muestra revisable

| Trace | Campo | Entidad | Span | Score | Reconocedor | Contexto | Operador | Guardar en traza |
|---|---|---|---:|---:|---|---|---|---|
| `tr_001` | `user_text` | `EMAIL_ADDRESS` | 35-58 | 0.98 | `EmailRecognizer` | `correo` | `hash` | `false` |
| `tr_001` | `user_email` | `EMAIL_ADDRESS` | 0-23 | 0.98 | `EmailRecognizer` | `email` | `hash` | `false` |
| `tr_001` | `phone` | `PHONE_NUMBER` | 0-15 | 0.86 | `PhoneRecognizer` | `phone` | `redact` | `false` |
| `tr_002` | `user_text` | `NATIONAL_ID` | 7-16 | 0.94 | `DniRecognizer` | `dni` | `redact` | `false` |
| `tr_002` | `user_email` | `EMAIL_ADDRESS` | 0-25 | 0.98 | `EmailRecognizer` | `email` | `hash` | `false` |

## Cómo convertirlo en Presidio real

1. Sustituye está simulación por `AnalyzerEngine(language='es')` y reconocedores propios para DNI/NIE, expediente, matrícula o identificadores internos.
2. Define umbrales por entidad y finalidad. No uses el mismo score para email, teléfono, persona y expediente.
3. Pasa contexto técnico al análisis: nombre de campo, origen, finalidad, idioma y tipo de flujo.
4. Aplica `AnonymizerEngine` con operadores por entidad: `hash`, `redact`, `replace`, `mask`, `encrypt` o `custom`.
5. Evalúa con un dataset etiquetado y mide TP, FP, FN, precisión, recall y F2 antes de publicar.

## Criterio de aceptación

- Ningún valor literal detectado debe quedar en logs o trazas si no existe una finalidad escrita.
- Todo hallazgo debe conservar score, reconocedor y operador aplicado para poder revisar la decisión.
- Un falso negativo en una entidad crítica debe crear tarea de ingeniería: nuevo reconocedor, mejor contexto o umbral revisado.
