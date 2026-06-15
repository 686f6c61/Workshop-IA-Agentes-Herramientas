# Práctica F4 C05

Estado: `valid`.

Modelo local razonable para prototipo, no para prometer concurrencia.

## Qué te llevas

Un cálculo inicial para no prometer que un modelo local cabe si la VRAM no acompaña.

## Evidencia

```json
{
  "status": "valid",
  "summary": "Modelo local razonable para prototipo, no para prometer concurrencia.",
  "model": {
    "parameters_b": 8,
    "bits": 4,
    "context": 8192,
    "kv_cache_gb": 3.0,
    "runtime_margin_gb": 4.0,
    "vram_gb": 16
  },
  "weights_gb": 4.0,
  "estimated_total_gb": 11.0,
  "checks": {
    "fits_memory": true,
    "has_margin": true,
    "context_declared": true
  },
  "what_you_take": "Un cálculo inicial para no prometer que un modelo local cabe si la VRAM no acompaña."
}
```
