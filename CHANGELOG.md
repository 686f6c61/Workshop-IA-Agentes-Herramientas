# Changelog

## [2.1.8] - 2026-05-08

### Added
- Nueva seccion `Evals y medicion avanzada` con eval de RAG, LLM-as-judge, eval de agentes y coste por tarea aceptada.
- Nueva seccion `Producto y UX de IA` con incertidumbre, citas, abstencion, aprobacion humana, rollback, memoria y handoff.
- Modelo de amenazas minimo en seguridad agentic para fronteras usuario/modelo, RAG/modelo, modelo/tools y tools/exterior.

### Changed
- Workshop ampliado de 160 a 171 slides numeradas, manteniendo el cierre final separado con `Mayo 2026 · update 05/26`.
- README, indice y metadatos SEO/JSON-LD sincronizados como portada + 171 slides numeradas + cierre.
- Slide de costes matizada como snapshot de API estandar con batch/flex, cache, region y coste por tarea aceptada.
- Slide multimodal ajustada para separar input/output por endpoint y usar `gpt-realtime-2` para audio realtime.

### Fixed
- Gemini textual/razonamiento actualizado a `Gemini 3.1 Pro Preview` (`gemini-3.1-pro-preview`), ya que `gemini-3-pro-preview` esta discontinuado desde el 26 de marzo de 2026.
- SWE-bench Lite corregido a 534 instancias oficiales y SWE-bench Multimodal a 100 dev / 500 test.
- Sora 2 / Sora 2 Pro marcado con matiz `legacy/deprecated` segun catalogo API actual.

## [2.1.7] - 2026-05-07

### Added
- Cuatro slides finales nuevas: glosario de siglas, checklist de exactitud para claims de IA, pipeline de entrega IA y benchmarks contaminados/eval privada.
- Referencias de rigor para Gemini 3.1 Pro Preview, OpenAI Evals/RFT, SWE-bench contamination, OWASP GenAI y model cards.

### Changed
- Workshop ampliado de 156 a 160 slides numeradas, manteniendo el cierre final separado con `Mayo 2026 · update 05/26`.
- Corregida la referencia antigua de Gemini Pro a `Gemini 3.1 Pro Preview` donde aplica y añadidas notas de snapshot mayo 2026.
- Reforzado el pipeline real de entrenamiento: datos/tokenizer, pre-training, SFT, preferencias/refuerzo, safety/evals, deploy y monitorización.
- Matizados chain-of-thought visible, privacidad/coste/latencia local, prompt caching, open weights/open source y lectura de leaderboards.
- Ampliadas siglas en contexto: BPE, MRL, GPTQ, AWQ, SSM, BM25, ADK, SDK, E2E, QA, TTFT, p95/p99, DLP, DPA, VPC, SBOM, SAST y ROI.

### Fixed
- Añadida advertencia de contaminación de SWE-bench Verified con recomendación de SWE-bench Pro/evals privadas.
- Referencia cruzada de la slide 4 corregida de slide 26 a slide 27.
- Configuración de Sentry movida a init de cliente y sourcemaps condicionados a `SENTRY_AUTH_TOKEN`, eliminando warnings de release/upload cuando no hay token.

## [2.1.6] - 2026-05-07

### Changed
- Slide 137 reestructurada para explicar post-training como eleccion de senal: ejemplos, preferencias, recompensa y optimizacion.
- Anadido RL verificable/RLVR como caso de refuerzo sin feedback humano directo cuando existe una recompensa objetiva, con matiz sobre sus limites.

## [2.1.5] - 2026-05-07

Ampliacion avanzada de estructura para separar operacion, seguridad y gobernanza.

### Added
- Nueva seccion `Operar IA en produccion` con LLMOps, serving open weights, escalado de inferencia, routing, fallback, budgets, EvalOps, DataOps y post-training avanzado.
- Nueva seccion `Seguridad, gobernanza y confianza` con seguridad agentic/MCP, OWASP LLM Top 10 aplicado, privacidad/private AI, EU AI Act, NIST AI RMF, NIST GenAI Profile, ISO/IEC 42001 e interpretabilidad.
- Referencias primarias y oficiales para vLLM, SGLang, TensorRT-LLM, OpenAI Evals/RFT/tracing, Anthropic evals, MCP Authorization, OWASP, NIST, ISO y EU AI Act.

### Changed
- Workshop ampliado de 140 a 156 slides numeradas, manteniendo el cierre final separado con `Mayo 2026 · update 05/26`.
- Indice, README, metadatos SEO y JSON-LD sincronizados con la nueva estructura y numeracion.

## [2.1.4] - 2026-05-07

Correcciones de exactitud en ejemplos copiables, costes y metadatos de publicacion.

### Fixed
- Ejemplos de Ollama Cloud actualizados a la API oficial de `ollama.com/api/chat` y `ollama.com/api/tags`, diferenciando API nativa de Ollama y compatibilidad OpenAI local bajo `/v1`.
- Catalogo de Ollama Cloud ajustado para marcar modelos con tag `cloud` y evitar listar modelos sin cloud como si fueran endpoint remoto garantizado.
- Integraciones de herramientas actualizadas a comandos `ollama launch` para Claude Code, Codex CLI y OpenCode.
- Precios DeepSeek actualizados a `deepseek-v4-pro` y `deepseek-v4-flash`, con cache hit/miss segun documentacion actual.
- Ejemplo de tool use de Anthropic corregido para incluir `tool_use.id`, `tool_result.tool_use_id` y el siguiente turno de conversacion.
- Ejemplo MCP convertido en ejemplo autocontenido con datos mock en vez de una variable `db` inexistente.
- Metadatos sincronizados como portada + 140 slides numeradas y anadido fichero `LICENSE` MIT.
- Cierre final separado de la slide 140 con la fecha `Mayo 2026 · update 05/26` y feedback a `@686f6c61`.
- Branding publico ajustado a `Workshop de IA para gente curiosa`.
- Conceptos teoricos matizados para evitar garantias absolutas: tokens, embeddings, attention, MoE, hallucinations, structured output, prompt caching, streaming, evals y agentes.

## [2.1.3] - 2026-05-07

Decision de fine-tuning, calculo de memoria, lectura de fichas y arquitecturas documentadas de agentes integradas en el workshop.

### Added
- Slide nueva sobre fine-tuning: casos donde si tiene sentido, casos donde es mejor no meterse y regla RAG vs cambio de comportamiento.
- Slides nuevas para Hugging Face/local: formula de RAM/VRAM con pesos + KV cache + margen, ejemplo 7B Q4 y separacion de formatos safetensors/GGUF/GPTQ/AWQ.
- Dos slides nuevas para traducir los terminos de una ficha real DeepSeek-V4: tags, licencia, runtimes, MoE, context length y precision FP4/FP8.
- Slide nueva con repos y Colabs de referencia para practicar inferencia HF, Trainer/PEFT, RAG, Diffusers y evals.
- Dos slides nuevas con diagramas SVG de arquitecturas documentadas de agentes: ReAct, ReWOO, Reflexion, manager/supervisor, handoffs y workflow critic.
- Bloque final de recursos ampliado a cuatro slides: mapa de estudio, papers/benchmarks, laboratorio practico y ruta de 30 dias.
- Imagen social 1200x630 para compartir en X/Twitter, LinkedIn y WhatsApp, con metadatos Open Graph y Twitter Card completos.
- Referencias oficiales de OpenAI, Google Vertex AI y Anthropic para fine-tuning, evals y limitaciones de acceso en Claude API.

### Changed
- Slide de modelos de razonamiento actualizada con routing por tarea: esfuerzo bajo para tareas cerradas/latencia, reasoning medio/alto para planificacion, herramientas, ambiguedad y riesgo, con Claude 4.7/4.6/4.5 y GPT-5.5/GPT-5.4-mini referenciados.
- Slide de arquitecturas actualizada a 2026: Transformer sigue dominante, pero se explican MoE, SSM/Mamba, Mamba-2, RWKV/RetNet, Hyena, Jamba e ideas byte/latent sin presentarlas como reemplazo universal.
- Slide de quantizacion reescrita para explicar formato, bits/peso, memoria estimada, trade-offs y terminos FP32, BF16/FP16, FP8/INT8 e INT4/NF4 sin darlos por sabidos.
- Slide practica de fine-tuning ajustada para distinguir APIs de fine-tuning, LoRA/QLoRA y alternativas con prompt, RAG, tools o proveedor.
- Slide de costes ampliada con modelos chinos estado del arte: Qwen3-Max/Qwen Plus, DeepSeek chat/reasoner y GLM-5.1/4.7/4.5, con notas sobre region, cache y thinking.
- Slides de Google Colab reescritas para explicar que toca el alumno y que aprende en inferencia HF, fine-tuning pequeño, RAG minimo, imagen/difusion y eval propia, mas limites, secretos y entregable reproducible.
- Indice, recaps, README y metadatos sincronizados con la nueva numeracion de 140 slides.

## [2.1.2] - 2026-05-06

Ampliacion integrada de Hugging Face y lectura de fichas de modelos.

### Added
- Tres slides nuevas sobre Hugging Face: caso real DeepSeek-V4 Pro/Flash, glosario de terminos de model cards y lectura de eval results.
- Siete slides nuevas de metodologia practica: mantenerse actualizado, matriz de eleccion de modelos, mini-lab Hugging Face, Google Colab, experimentos buenos, eval interna y errores comunes.
- Explicacion de terminos como base, instruct, adapter, LoRA, merge, quantized, safetensors, GGUF, gated y chat template.
- Guia de metricas de benchmarks en fichas: EM, Pass@1, Resolved, Accuracy, F1, Elo/rating y campos de setup.

### Changed
- Indice, recaps de seccion, README y metadatos sincronizados con la nueva numeracion de 128 slides.
- Estado del arte revisado con fuentes primarias: Claude Opus 4.7, Qwen3.6-35B-A3B y DeepSeek-V4 Pro/Flash.
- Revisión final de mayo 2026: gpt-oss-120b, Mistral Large 3 / Medium 3.5, embeddings Voyage/Cohere, SWE-bench Lite y precios de coding assistants.

## [2.1.1] - 2026-05-06

Ampliacion de benchmarks y evaluacion de agentes de coding.

### Added
- Bloque de benchmarks: que mide cada familia, que no mide y como leer resultados sin extrapolar de mas.
- Slide dedicada a SWE-bench: flujo issue -> patch -> Docker/test harness -> % Resolved, con variantes Full, Verified, Lite, Multilingual y Multimodal.
- Checklist para interpretar leaderboards: split, scaffold, coste, reproducibilidad, contaminacion y transferencia al repo propio.

## [2.1.0] - 2026-05-06

Actualizacion de mayo 2026 manteniendo el estilo academico del workshop.

### Changed
- Portada y metadatos actualizados a mayo 2026 (05/26).
- Modelos actualizados: GPT-5.5/GPT-5.4, Claude Opus 4.7/Sonnet 4.6, Gemini 3.1 Pro Preview, gpt-oss-120b, Llama 4, Qwen3.6, DeepSeek-V4 Pro/Flash y Mistral Large 3 / Medium 3.5.
- MoE ampliado con parametros totales vs activos, routing, ejemplos reales y advertencias de comparacion.
- Quantizacion ampliada: GGUF/GGML, bitsandbytes, GPTQ/AWQ, FP8, Q4-Q8 e importancia de calibracion.
- Hugging Face + LM Studio convertido en checklist de model cards, licencias, formatos, base model y quantizaciones.
- README actualizado para Coolify/Docker y URL actual del despliegue.

## [2.0.0] - 2026-03-24

Workshop reescrito y ampliado. De 69 slides a 113. Nuevo nombre, nuevo repo, nueva estructura.

### Added
- **Fundamentos de redes neuronales**: neurona artificial, capas, backpropagation, funciones de perdida, optimizadores, CNNs, RNNs/LSTMs (slides 6-11)
- **Arquitecturas avanzadas**: atencion en detalle (Q, K, V), tokenizacion en profundidad, transfer learning, modelos multimodales nativos (slides 22-24, 29)
- **Context engineering**: las 6 capas del contexto, mas alla del prompt engineering (slide 36)
- **Voz y APIs en tiempo real**: OpenAI Realtime API, ElevenLabs, Deepgram, Gemini Live (slide 40)
- **Generacion de imagenes en profundidad**: modelos de difusion, LoRA/DreamBooth/Textual Inversion, ComfyUI/Forge/Civitai, ControlNet/IP-Adapter (slides 42-46)
- **Agentic RAG y GraphRAG**: evolucion del retrieval con razonamiento y grafos de conocimiento (slides 49-51)
- **Text-to-SQL**: consultas en lenguaje natural a bases de datos (slide 55)
- **Arquitectura de apps con LLM**: retry, fallback, circuit breaker, model routing, cache semantica (slide 61)
- **Memoria persistente para agentes**: CLAUDE.md, memoria episodica, Zep, MemGPT (slide 67)
- **Coding agents**: comparativa Devin, Claude Code, OpenHands, Aider, Codex CLI (slide 77)
- **MCP en la practica**: ejemplo completo de servidor MCP en TypeScript (slide 79)
- **AI coding benchmarks**: SWE-bench, Aider Polyglot, HumanEval, WebArena, TAU-bench (slide 87)
- **Gestion de prompts como codigo**: versionado, evals, A/B testing, rollback (slide 95)
- **Testing de codigo generado por IA**: mutation testing, property-based testing (slide 97)
- **Vibe coding**: el concepto de Karpathy, con disciplina (slide 98)
- **Configurar Claude Code, OpenCode y Cursor**: ejemplos reales de CLAUDE.md, AGENTS.md, .cursorrules (slides 101-102)
- **Agentes en produccion: lecciones aprendidas**: que funciona, que no, el "agent tax" (slide 103)
- **Edge AI**: modelos en navegador, movil e IoT (slide 33)
- **6 slides de recapitulacion**: "lo que deberias saber" al final de cada seccion con referencias cruzadas
- **Seccion Ollama Cloud**: 6 slides sobre modelos OSS en la nube (slides 106-111)
- Soporte de Astro 6

### Changed
- Titulo: de "IA entre amigos" a "Workshop de IA para gente curiosa"
- Repo: de `IA-Entre-Amigos` a `Workshop-IA-Agentes-Herramientas`
- URL: de `ia-entre-amigos.onrender.com` a `workshop-ia-agentes-herramientas.onrender.com`
- Tildes corregidas en todas las slides
- Layout de slides con two-cols revisado y equilibrado
- Slide de catalogo de modelos Ollama: de 4 tablas separadas a tabla unica con columna de categoria
- Callout "Clave" en agente-vs-prompt movido fuera del two-cols
- Referencia cruzada corregida: slide de parametros actualizada en todas las menciones
- Slides de Ollama Cloud reescritas: de 8 slides dispersas a 6 focalizadas

### Removed
- Slide "Demo (por definir)"
- Slides redundantes de configuracion de Cursor/OpenCode dentro de la seccion Ollama Cloud

## [1.0.0] - 2026-03-09

Version inicial con 69 slides en 5 secciones: fundamentos, arquitecturas, uso practico, agentes y realidad de construir con IA.
