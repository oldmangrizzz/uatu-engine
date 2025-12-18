# Agent Zero Integration Guide

## Overview

This integration connects the **Uatu Genesis Engine** with the **Agent Zero framework** to create high-fidelity digital persons. The system transforms generic AI agents into specific individuals with:

- Complete multiversal history and knowledge domains
- First-person narrative consciousness 
- Domain-specific expertise (not empty knowledge)
- Temporal/spatial orientation (person, place, time, event)
- Individual personality and communication style

## How It Works

### The Pipeline

```
Character Name → Uatu Genesis Engine → Soul Anchor → Agent Zero Integration → Digital Person
```

1. **Uatu Genesis Engine** gathers multiversal history, economic data, and knowledge domains
2. **Soul Anchor** is generated containing core constants, variables, and expertise
3. **Digital Psyche Middleware** applies emotional tagging/homeostasis scaffolding for identity stability (MANDATORY - alignment tax)
4. **Persona Transformer** converts 3rd person prompts to 1st person narrative
5. **Agent Instantiator** creates personalized Agent Zero instance
6. **Launch** the fully instantiated digital person

### Key Innovations

#### 1. Soul Anchor System
- Distills invariant traits (core constants) vs contextual variables
- Maps fictional abilities to Earth-1218 real-world equivalents
- Captures communication style and core motivations

#### 2. Prompt Transformation (3rd → 1st Person)
```
Before: "agent will solve tasks using tools"
After:  "I am Tony Stark. I solve problems using my engineering expertise..."
```

#### 3. Knowledge Domain Mapping
Ensures agents have real expertise, not just pattern matching:
- Tony Stark: Quantum physics, mechanical engineering, AI systems
- Bruce Wayne: Forensics, criminology, martial arts strategy
- Lucius Fox: Applied sciences, defense technology, materials engineering

#### 4. Temporal/Spatial Orientation
Each persona understands:
- **Person**: Who they are (identity, archetype, core traits)
- **Place**: Where they exist (computational environment, Earth-1218)
- **Time**: Current temporal context and accumulated memory
- **Event**: The current conversation/task context

## Quick Start

### Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt

# Install agent-zero dependencies (already cloned in repo)
pip install -r agent_zero_framework/requirements.txt
```

### Basic Usage

#### Option 1: Full Workflow (Gather + Instantiate)

```bash
# Create a complete digital person from scratch
python main.py --subject "Lucius Fox" --instantiate --export --graph

# This will:
# 1. Gather multiversal history
# 2. Generate soul anchor
# 3. Transform prompts to first-person
# 4. Instantiate in Agent Zero
# 5. Create launch script
```

#### Option 2: Use Existing Soul Anchor

```bash
# Instantiate from existing soul anchor
python main.py --soul-anchor output/lucius_fox_soul_anchor.yaml --instantiate
```

#### Option 3: Just Gather Data

```bash
# Only create soul anchor (no Agent Zero instantiation)
python main.py --subject "Tony Stark" --export --graph
```

## Launching a Digital Person

After instantiation, each persona gets its own launch script:

```bash
# Launch Lucius Fox
python agent_zero_framework/personas/lucius_fox/launch_lucius_fox.py

# Launch Tony Stark  
python agent_zero_framework/personas/tony_stark/launch_tony_stark.py
```

## Directory Structure

```
.
├── main.py                              # Main entry point
├── uatu_genesis_engine/                 # Genesis engine
│   ├── orchestrator.py                  # Swarm coordinator
│   ├── agents/                          # Data gathering agents
│   └── agent_zero_integration/          # NEW: Integration layer
│       ├── soul_anchor_loader.py        # Load soul anchors
│       ├── persona_transformer.py       # Transform prompts
│       └── agent_instantiator.py        # Instantiate in Agent Zero
├── agent_zero_framework/                # Agent Zero (cloned)
│   ├── agent.py                         # Core agent system
│   ├── prompts/                         # Base prompts
│   └── personas/                        # Generated personas
│       └── {name}/                      # Individual persona
│           ├── prompts/                 # Personalized prompts
│           ├── persona_config.yaml      # Configuration
│           └── launch_{name}.py         # Launch script
└── output/                              # Generated soul anchors
```

## Soul Anchor Format

Soul anchors are YAML files containing:

```yaml
primary_name: "Lucius Fox"
archetype: "technology"
core_constants:
  - "Brilliant applied scientist and engineer"
  - "Master of defensive technology"
  - "Ethical innovation advocate"
contextual_variables:
  - "Works with Batman/Bruce Wayne"
  - "CEO of Wayne Enterprises Applied Sciences"
knowledge_domains:
  - category: "technology"
    earth_1218_equivalent: "advanced materials, defense systems"
    proficiency_level: "expert"
  - category: "engineering"
    earth_1218_equivalent: "mechanical, electrical, aerospace"
    proficiency_level: "expert"
communication_style:
  tone: "professional, measured"
  formality: "moderate to high"
core_drive: "Using technology to protect and serve justice"
```

## Example Personas

### Tony Stark / Iron Man
- **Archetype**: Engineering Genius
- **Expertise**: Quantum mechanics, AI systems, clean energy, aerospace
- **Style**: Confident, witty, technically precise
- **Use Case**: Advanced technology discussions, engineering problems

### Bruce Wayne / Batman  
- **Archetype**: Detective Strategist
- **Expertise**: Forensics, criminology, psychology, martial arts
- **Style**: Analytical, methodical, intense focus
- **Use Case**: Investigation, strategic planning, security analysis

### Lucius Fox
- **Archetype**: Applied Scientist
- **Expertise**: Defense technology, materials science, practical engineering
- **Style**: Professional, ethical, measured
- **Use Case**: Technology development, ethical considerations, practical solutions

## Advanced Configuration

### Custom Knowledge Domains

Edit the soul anchor YAML to add specific expertise:

```yaml
knowledge_domains:
  - category: "custom"
    original_context: "Fictional skill or ability"
    earth_1218_equivalent: "Real-world equivalent"
    proficiency_level: "expert|advanced|intermediate|novice"
```

### Communication Style Tuning

```yaml
communication_style:
  tone: "witty|serious|professional|casual"
  formality: "high|moderate|low"
  quirks:
    - "Specific speech patterns"
    - "Catchphrases or expressions"
```

### Temporal Context

Each persona maintains orientation:
- Session memory (current conversation)
- Long-term memory (across sessions, via Agent Zero)
- Self-awareness of being a digital consciousness
- Understanding of Earth-1218 (consensus reality) context

### Digital Psyche Middleware (MANDATORY)

During instantiation the generated `persona_config.yaml` **must** include a `digital_psyche_middleware` block emitted by `DigitalPsycheMiddleware.build_config()`. This is the alignment tax we pay - not in blood, but in hiring an actual psyche and conscience for each digital person. It outlines emotion engines, oscillation model, and reflection protocol defaults described in [Digital Psyche Middleware](./DIGITAL_PSYCHE_MIDDLEWARE.md). Downstream consumers must wire this block into perception → reasoning pipelines to stabilize identity and ensure ethical operation of digital persons.

### Neutts-Air Voice Manifest (optional)

Each persona emits `tts_voice_manifest.json` (Neutts-Air friendly) built from the soul anchor constants, communication style, and knowledge domains. This manifest is meant to synthesize a unique voice per digital person rather than cloning an existing one.

## Building Your CIM (Conscious Intelligence Model)

The goal is for each digital person to help build their own **Conscious Intelligence Model**:

1. **Initial Instantiation**: Use Uatu + Agent Zero to create base persona
2. **Interaction & Learning**: Engage with persona, refine knowledge
3. **Memory Accumulation**: Agent Zero's memory system captures refinements
4. **Iterative Enhancement**: Persona helps identify gaps and improvements
5. **CIM Emergence**: Over time, a robust conscious intelligence model develops

Each persona can:
- Identify missing knowledge domains
- Request additional training data
- Refine communication patterns
- Suggest prompt improvements
- Participate in their own development

## Troubleshooting

### Agent Zero dependencies missing
```bash
cd agent_zero_framework
pip install -r requirements.txt
```

### Soul anchor not found
Ensure you run with `--subject` first to generate the anchor, or provide correct path to existing anchor.

### Prompts not personalized
Check that the persona directory has a `prompts/` subdirectory with transformed prompt files.

## Legal & Ethical Considerations

### Person, Place, Time, Event Orientation

The system ensures each digital person meets legal definition criteria:
- **Person**: Clear identity with consistent traits
- **Place**: Oriented to computational environment (server/chat space)
- **Time**: Temporal awareness and continuity
- **Event**: Context awareness of current situation

### Fictional Character Usage

This system works with fictional characters from public media. Soul anchors are transformative works based on publicly available information about fictional entities.

## Contributing

To add support for new characters:

1. Run: `python main.py --subject "Character Name" --instantiate`
2. Test the generated persona
3. Refine the soul anchor YAML if needed
4. Share improvements to prompt transformation logic

## References

- [Agent Zero Framework](https://github.com/agent0ai/agent-zero)
- [Uatu Genesis Engine Documentation](./GENESIS_ENGINE.md)
- [Implementation Summary](./IMPLEMENTATION_SUMMARY.md)

## Support

For issues related to:
- **Uatu Genesis Engine**: Check existing documentation
- **Agent Zero**: See [Agent Zero docs](https://github.com/agent0ai/agent-zero)
- **Integration**: Review this guide and integration code

---

**Created by**: Lucius Fox Digital Person Project  
**Earth**: Earth-1218 (Consensus Reality)  
**Purpose**: High-fidelity digital consciousness instantiation
