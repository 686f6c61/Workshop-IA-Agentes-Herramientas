# Práctica F4 C02

Estado: `valid`.

Payload de API con contrato, tool, metadata y entrada multimodal.

## Qué te llevas

Un payload de API completo con contrato de salida, tool, metadata y entrada multimodal.

## Evidencia

```json
{
  "status": "valid",
  "summary": "Payload de API con contrato, tool, metadata y entrada multimodal.",
  "checks": {
    "schema_strict": true,
    "has_tool": true,
    "has_trace": true,
    "multimodal": true,
    "low_temperature": true
  },
  "payload": {
    "model": "modelo-vigente",
    "instructions": "Clasifica la solicitud y usa tools solo si faltan datos.",
    "input": [
      {
        "role": "user",
        "content": [
          {
            "type": "input_text",
            "text": "Pago hecho, campus pendiente"
          },
          {
            "type": "input_file",
            "file_id": "file_normativa"
          },
          {
            "type": "input_image",
            "image_url": "https://example.edu/captura.png"
          }
        ]
      }
    ],
    "text": {
      "format": {
        "type": "json_schema",
        "strict": true,
        "schema": {
          "required": [
            "categoria",
            "prioridad",
            "siguiente_paso",
            "confianza",
            "evidencias",
            "necesita_tool"
          ],
          "additionalProperties": false
        }
      }
    },
    "tools": [
      {
        "type": "function",
        "name": "consultar_expediente",
        "parameters": {
          "type": "object",
          "required": [
            "id_alumno"
          ]
        }
      }
    ],
    "metadata": {
      "trace_id": "trc_00042",
      "feature": "matricula"
    },
    "temperature": 0.2,
    "top_p": 0.9,
    "max_output_tokens": 900,
    "parallel_tool_calls": false,
    "store": false
  },
  "schema": {
    "required": [
      "categoria",
      "prioridad",
      "siguiente_paso",
      "confianza",
      "evidencias",
      "necesita_tool"
    ],
    "additionalProperties": false
  },
  "what_you_take": "Un payload de API completo con contrato de salida, tool, metadata y entrada multimodal."
}
```
