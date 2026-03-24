# Workshop de IA: agentes, modelos y herramientas

De la neurona al agente: 113 slides para entender la IA moderna y aplicarla en tu dia a dia como ingeniero. Desde backpropagation hasta desplegar agentes en produccion, pasando por RAG, MCP, ControlNet y vibe coding.

**[Ver presentacion](https://workshop-ia-agentes-herramientas.onrender.com)** | Actualizado a marzo 2026 (update 04/26)

## Contenido

### Fundamentos (slides 2-17)
- [x] Que es (y que no es) la IA
- [x] Determinismo vs sistemas estocasticos
- [x] La neurona artificial, redes neuronales, backpropagation
- [x] Funciones de perdida, optimizadores (Adam, SGD)
- [x] CNNs para vision, RNNs y LSTMs para secuencias
- [x] Tokens, embeddings, similitud coseno
- [x] Entrenamiento vs inferencia, quantizacion (GGUF, Q4, Q8)

### Arquitecturas y modelos (slides 19-34)
- [x] LLMs, Transformers, Mixture of Experts
- [x] Atencion en detalle: matrices Q, K, V, multi-head, RoPE
- [x] Tokenizacion en profundidad: BPE, WordPiece, SentencePiece
- [x] Transfer learning: de ImageNet a GPT
- [x] Modelos multimodales nativos (texto + imagen + audio + video)
- [x] Parametros: temperature, top_p, top_k
- [x] Modelos de razonamiento (thinking tokens)
- [x] Open source vs propietario, destilacion, inferencia optimizada
- [x] Edge AI: modelos en navegador, movil e IoT

### Uso practico (slides 36-62)
- [x] Prompt engineering y context engineering
- [x] Alucinaciones y como protegerte
- [x] Structured output / JSON mode con schema
- [x] Vision, multimodalidad, voz en tiempo real (OpenAI Realtime, ElevenLabs)
- [x] Generacion de imagenes: difusion, latent space, CFG
- [x] Entrenamiento de imagen: LoRA, DreamBooth, Textual Inversion
- [x] Herramientas: ComfyUI, Forge, Civitai, Replicate, RunPod
- [x] Tecnicas de control: ControlNet, IP-Adapter, inpainting, upscaling
- [x] RAG, agentic RAG, GraphRAG, hybrid search, contextual retrieval
- [x] Fine-tuning con LoRA/QLoRA (Unsloth, Axolotl)
- [x] Datos sinteticos, bases de datos vectoriales
- [x] Text-to-SQL, prompt caching, context window
- [x] API hello world, streaming (SSE)
- [x] Arquitectura de apps con LLM: retry, fallback, circuit breaker, model routing

### Agentes y orquestacion (slides 64-83)
- [x] Cuando usar un agente y cuando un prompt
- [x] Bucle ReAct, Plan-and-Execute, Reflexion
- [x] Memoria persistente: CLAUDE.md, Zep, MemGPT
- [x] Function calling (tool use) con ejemplo completo
- [x] Patrones: chaining, routing, paralelizacion, orchestrator-workers
- [x] Orquestadores: LangGraph, CrewAI, Claude Agent SDK, Google ADK, Mastra
- [x] Claude Code: rules, skills, hooks, MCPs, subagentes, plugins
- [x] Coding agents: Claude Code, Devin, OpenHands, Aider, Codex CLI
- [x] MCP: concepto (el "USB de la IA") + servidor minimo en TypeScript
- [x] Computer Use, Browser Use, A2A (Agent-to-Agent)
- [x] Human-in-the-loop: niveles de autonomia

### Realidad del ingeniero (slides 85-104)
- [x] IDE web vs terminal, comparativa de coding assistants
- [x] Benchmarks: SWE-bench, Aider Polyglot, HumanEval, WebArena, TAU-bench
- [x] IA en CI/CD, seguridad (OWASP Top 10 for LLMs), guardrails
- [x] Testing adversarial, red teaming, prompt injection
- [x] EU AI Act: clasificacion por riesgo, calendario
- [x] Costes, observabilidad (Langfuse, Helicone)
- [x] Prompts como codigo: versionado, evals, A/B testing
- [x] Testing de codigo generado: mutation testing, property-based
- [x] Vibe coding con disciplina
- [x] Configurar Claude Code, OpenCode y Cursor como un pro
- [x] Agentes en produccion: lecciones aprendidas y el "agent tax"

### Modelos OSS con Ollama Cloud (slides 106-111)
- [x] Ollama Cloud: modelos OSS sin GPU
- [x] Catalogo, setup, integracion con herramientas
- [x] Cloud vs local: cuando usar cada uno

Cada seccion termina con una slide de recapitulacion con referencias cruzadas.

## Arrancar en local

```bash
git clone https://github.com/686f6c61/Workshop-IA-Agentes-Herramientas.git
cd Workshop-IA-Agentes-Herramientas
npm install
npm run dev
```

## Build y deploy

```bash
npm run build    # genera dist/
npm run preview  # preview local del build
```

Deploy automatico en Render via `render.yaml`. Cada push a `main` redespliega.

## Stack

- Astro 6 (static site)
- Lucide Icons (CDN)
- Space Grotesk + IBM Plex Mono
- Google Analytics + Search Console
- Render (hosting)

## Autor

[686f6c61](https://github.com/686f6c61)

## Licencia

MIT
