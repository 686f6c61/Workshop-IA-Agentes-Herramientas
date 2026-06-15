# Presupuesto de inferencia y serving

Memoria de pesos: `{'16': 14.0, '8': 7.0, '4': 3.5}`.
KV cache: `{'MHA': 17.1799, 'GQA': 4.295, 'MQA': 0.5369}`.
Latencia usuario aislado: `7.5167` s.
Latencia compartida: `20.85` s.

Si solo miras pesos, ignoras una parte grande del serving: KV cache, concurrencia y throughput.
