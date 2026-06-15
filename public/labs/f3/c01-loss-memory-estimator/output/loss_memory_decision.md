# Pérdida y memoria de un LLM

Pérdida antes: `2.3026`. Pérdida después: `0.7853`.
Perplexity antes: `2.1544`. Perplexity después: `1.2992`.

| Modelo | Precisión | Memoria de pesos |
|---|---|---:|
| 7B | FP16 | 14 GB |
| 7B | INT8 | 7 GB |
| 7B | INT4 | 3.5 GB |
| 13B | FP16 | 26 GB |
| 13B | INT8 | 13 GB |
| 13B | INT4 | 6.5 GB |

La memoria de pesos no incluye KV cache, activaciones, runtime ni margen operativo. Es solo el primer cálculo para no hablar a ciegas.
