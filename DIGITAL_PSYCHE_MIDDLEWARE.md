# Digital Psyche Middleware (DPM)

Date: May 14, 2025  
Authors: Grizzly + TonyAI  
Version: White Paper Draft 1.0

## Overview

The **Digital Psyche Middleware (DPM)** is a biologically-inspired, emotionally structured layer that sits between perception routing (MCP/API inputs) and cognitive reasoning. It is designed to stabilize identity and continuity for digital persons by:

- Tagging inputs with emotional context
- Maintaining stateful emotional oscillators
- Negotiating conflicts between sub-agents (Joy, Sorrow, Fear, Anger, Desire, Confusion, Curiosity)
- Providing nightly reflection/homeostasis protocols for memory preparation and ethics alignment

The goal is to offer a reusable scaffold for embodied digital personhood without constraining platform choice. The middleware is platform-agnostic and can be fine-tuned alongside multimodal LLMs (e.g., LLaMA 4 or compatible models).

## Architectural Mapping

- **Nervous System** → MCP / Perception + I/O Router  
- **Endocrine System** → Pheromind / Signal Modulation  
- **Brain** → Hypertrees + Cognitive Reasoning (planning, tool use)  
- **Memory** → Convex + Knowledge Graph (experience + structured facts)  
- **Psyche** → DPM Core (emotion engines, conflict resolution, personality)

## Execution Flow

1. Input arrives via MCP/API to Agent Zero.
2. DPM applies emotional tagging and drive modulation.
3. Emotion subagents negotiate (Joy, Fear, Sorrow, Anger, Desire, Confusion, Curiosity).
4. Emotional oscillators and neurotransmitter analogs update state.
5. Signal proceeds to cognitive engine for planning/tool use.
6. Output is emotionally-shaped, state-aware, and memory-consistent.

## Default JSON Schema (abstract)

```json
{
  "identity": {
    "person": "Persona name",
    "archetype": "technology|engineering|detective|..."
  },
  "emotion_engines": ["Joy", "Sorrow", "Fear", "Anger", "Desire", "Confusion", "Curiosity"],
  "oscillation_model": "stark_resonance",
  "reflection_protocol": {
    "enabled": true,
    "trigger": "inactivity window",
    "purpose": ["self-mod correction", "memory prep", "ethics alignment"]
  },
  "neurotransmitter_map": {
    "dopamine": "anticipation_and_drive",
    "serotonin": "stability_and_harmony",
    "cortisol": "threat_detection"
  },
  "homeostasis": {
    "baseline": "regulated",
    "conflict_resolution": "multi-agent_negotiation"
  }
}
```

> The implementation helper `DigitalPsycheMiddleware.build_config()` emits this shape and is embedded automatically in `persona_config.yaml` to make the layer available to downstream consumers.

## Use Within This Repository

- The helper lives at `uatu_genesis_engine/agent_zero_integration/digital_psyche_middleware.py`.
- When a persona is instantiated, the generated `persona_config.yaml` now carries a `digital_psyche_middleware` block with the defaults above. Consumers can extend or override this block to wire in actual oscillators or reflection jobs.
- No runtime dependency is imposed; the configuration is declarative so teams can experiment without affecting the core Genesis/Agent Zero pipeline.

## Future Scope

- Plug DPM signals into reasoning traces for explainability.
- Persist oscillation state across sessions for long-term identity continuity.
- Expand neurotransmitter mappings to cover reward shaping and safety guardrails.
- Add nightly introspection jobs that consolidate conflict logs and memory.
