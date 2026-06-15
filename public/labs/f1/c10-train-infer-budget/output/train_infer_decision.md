# Presupuesto de entrenamiento e inferencia

Este informe separa pesos, KV cache y memoria aproximada de entrenamiento. Los números son de orden de magnitud: sirven para decidir si una idea merece prueba real.

## local_support_assistant_7b

- Objetivo: Inferencia local para asistente de soporte con documentos internos.
- Modo: `inference`.
- Pesos: `3.5` GB.
- KV cache: `4.29` GB.
- Memoria total de inferencia: `7.79` GB frente a `10.2` GB seguros.
- Memoria aproximada de entrenamiento: `None` GB.
- Recomendación: **inferencia local viable con medición de latencia y calidad**.
- Riesgos: sin bloqueo inicial.

## support_tone_lora_8b

- Objetivo: Ajustar tono y formato de respuestas de soporte.
- Modo: `lora_finetune`.
- Pesos: `4.0` GB.
- KV cache: `4.29` GB.
- Memoria total de inferencia: `8.29` GB frente a `20.4` GB seguros.
- Memoria aproximada de entrenamiento: `32.0` GB.
- Recomendación: **LoRA/QLoRA si el problema es formato o tono estable, no conocimiento vivo**.
- Riesgos: sin bloqueo inicial.

## pretrain_domain_model_1b

- Objetivo: Entrenar desde cero un modelo pequeño de dominio.
- Modo: `pretraining`.
- Pesos: `2.0` GB.
- KV cache: `3.22` GB.
- Memoria total de inferencia: `5.22` GB frente a `68.0` GB seguros.
- Memoria aproximada de entrenamiento: `16.0` GB.
- Recomendación: **no entrenar desde cero sin corpus, presupuesto y evaluación mucho más sólidos**.
- Riesgos: tokens_insuficientes_para_preentrenamiento.

## api_rag_policy_search

- Objetivo: Responder sobre políticas internas cambiantes.
- Modo: `api_rag`.
- Pesos: `0.0` GB.
- KV cache: `0.0` GB.
- Memoria total de inferencia: `0.0` GB frente a `0.0` GB seguros.
- Memoria aproximada de entrenamiento: `None` GB.
- Recomendación: **API + RAG antes que fine-tuning**.
- Riesgos: sin bloqueo inicial.
