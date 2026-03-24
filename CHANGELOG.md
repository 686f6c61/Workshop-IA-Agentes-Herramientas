# Changelog

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
- Titulo: de "IA entre amigos" a "Workshop de IA: agentes, modelos y herramientas"
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

Version inicial con 69 slides en 5 secciones: fundamentos, arquitecturas, uso practico, agentes, realidad del ingeniero.
