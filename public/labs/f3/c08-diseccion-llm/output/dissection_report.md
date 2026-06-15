# Diseccion de una llamada a un LLM

Caso: `support-policy-json-v1`.

## Tokenizacion

El prompt ensamblado queda en `129` tokens aproximados, con `5.47` caracteres por token. Esta cifra no sustituye a un tokenizer real, pero entrena la idea clave: coste, contexto y truncamiento empiezan antes de llamar al modelo.

| Token | ID simulado | Embedding preview |
|---|---:|---|
| `SYSTEM` | 73635 | `[0.6784, -0.7412, 0.5137, 0.3098, -0.8275, 0.2471]` |
| `:` | 71302 | `[0.8118, 0.349, -0.9451, 0.051, -0.2, 0.1137]` |
| `Eres` | 84265 | `[-0.4196, -0.8667, 0.3333, 0.0196, 0.2941, 0.8902]` |
| `un` | 81579 | `[-0.1843, 0.4745, 0.2627, -0.8902, 0.8353, -0.6627]` |
| `asistente` | 17873 | `[-0.6627, -0.6235, -0.6314, -0.5137, 0.2078, 0.7255]` |
| `de` | 51675 | `[0.1686, 0.2078, -0.4588, 0.6627, -0.3882, -0.1294]` |
| `soporte` | 83205 | `[0.6941, 0.4588, -0.7569, 0.9216, -0.1373, -0.2627]` |
| `interno` | 15217 | `[-0.2078, 0.7333, 0.8745, 0.4196, -0.1529, 0.3255]` |
| `.` | 5336 | `[0.6078, 0.4118, 0.8667, -0.6706, 0.8353, -0.1765]` |
| `Responde` | 77387 | `[0.1529, -0.8745, 0.9373, 0.8902, -0.6235, 0.451]` |

## Formas de tensores

| Pieza | Shape | Lectura de ingenieria |
|---|---|---|
| `token_ids` | `[1, 129]` | Secuencia discreta que entra al modelo. |
| `embeddings` | `[1, 129, 4096]` | Cada token ya es un vector de anchura `d_model`. |
| `q` | `[1, 32, 129, 128]` | Consultas de atencion por cabeza. |
| `k_cache` | `[4, 8, 4096, 128]` | Claves cacheadas para evitar recomputar contexto. |
| `v_cache` | `[4, 8, 4096, 128]` | Valores cacheados que se mezclan durante decode. |
| `logits` | `[1, 10]` | Una puntuacion por token candidato del vocabulario simulado. |

## Arquitectura y runtime moderno

| Señal | Valor | Lectura de ingenieria |
|---|---|---|
| Posicion | `RoPE` | La posicion afecta a la atencion; contexto largo no garantiza recuperar bien lo que queda en medio. |
| Normalizacion | `RMSNorm` | Estabiliza activaciones; importa al cuantizar o comparar runtimes. |
| FFN | `SwiGLU` | No es relleno: transforma cada posicion entre rondas de atencion. |
| GQA | `8 KV heads / 32 attention heads` | Menos cabezas KV reducen memoria de cache frente a MHA completa. |
| Ahorro KV por GQA | `75.0%` | En este caso toy, la cache seria `8.59` GB con MHA completa. |
| Lost in the middle | `moderado: los documentos quedan entre instrucciones y contrato; mide si la evidencia intermedia se recupera` | No metas documentos sin medir posicion, orden y recuperacion real. |
| Speculative decoding | `draft_tokens=4, acceptance=0.68` | Acelera si el modelo draft propone tokens que el modelo grande acepta. |

## Logits y sampling

Perfil usado: `temperature=0.5`, `top_k=5`, `top_p=0.95`, `min_p=0.01`.

| Token candidato | Probabilidad final |
|---|---:|
| `{"categoria"` | 0.85027 |
| `incidencia` | 0.115071 |
| `ampliacion` | 0.034659 |

Token seleccionado: `{"categoria"`. Entropia final: `0.726` bits.

## KV cache y runtime

| Medida | Valor | Por que importa |
|---|---:|---|
| Pesos | 4.0 GB | Memoria del modelo cuantizado. |
| KV cache | 2.147 GB | Memoria temporal que crece con contexto, batch y `num_ctx`. |
| TTFT estimado | 0.0984 s | Tiempo hasta empezar a ver respuesta. |
| Decode max | 3.273 s | Tiempo si se consume todo `max_output_tokens`. |
| Decode con speculative toy | 1.909 s | Estimacion pedagogica; en un runtime real se mide con ratio de aceptacion. |
| Tokens/s por usuario | 55.0 | Throughput repartido por batch. |

## Decision de ingenieria

La tarea exige salida JSON verificable y cita; conviene bajar variabilidad, fijar contrato y medir tasa de parseo antes que creatividad.

Mide como minimo: `json_parse_rate`, `schema_pass_rate`, `citation_supported_rate`, `ttft_seconds`, `kv_cache_gb`.

Gate valido: `True`.
