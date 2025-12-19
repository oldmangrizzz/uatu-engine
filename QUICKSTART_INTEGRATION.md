# Quick Start Guide: Uatu Genesis Engine Digital Person Framework

## 🚀 5-Minute Quick Start

### Step 1: Install Dependencies

```bash
# Clone the repository (if you haven't already)
git clone https://github.com/oldmangrizzz/uatu-engine.git
cd uatu-engine

# Install Python dependencies
pip install -r requirements.txt

# Optional: Install Agent Zero dependencies for full functionality
pip install -r agent_zero_framework/requirements.txt
```

### Step 2: Create Your First Digital Person

```bash
# Gather data and create a new persona
python main.py --subject "Your Subject Name" --instantiate --export
```

This will:
- Gather multiversal history and knowledge domains
- Create a Soul Anchor with personality invariants
- Transform prompts to first-person perspective
- Generate a dedicated launch script

### Step 3: Launch a Digital Person

```bash
# Launch your generated persona
python agent_zero_framework/personas/[subject_name]/launch_[subject_name].py
```

**Note**: 
- Personas are generated on-demand by the Uatu Engine
- No pre-configured personas are included in the system
- For launching Agent Zero, you'll need to configure API keys for LLM providers

## 📖 What Just Happened?

### The Magic Behind the Scenes

1. **Uatu Genesis Engine** gathered multiversal history about the subject
2. **Soul Anchor** was created with invariant traits and knowledge domains
3. **Persona Transformer** converted generic AI prompts to first-person narrative
4. **Agent Instantiator** created a personalized Agent Zero instance
5. **Launch Script** was generated for easy startup

### What Makes This Different?

Traditional AI:
```
"agent will solve tasks using tools"
"agent can help with various topics"
```

Uatu Genesis Engine:
```
"I am Tony Stark. I approach problems through my expertise in 
quantum mechanics and engineering. When discussing arc reactor 
technology, I draw from my deep knowledge of clean energy 
research and materials science..."
```

## 🎯 Common Use Cases

### Use Case 1: Technical Expert Consultation

```bash
# Create a technical expert persona
python main.py --subject "Subject with Engineering Background" --instantiate --export
```

Query the generated persona about: Domain-specific technical knowledge, system design, advanced concepts

### Use Case 2: Analytical/Strategic Consultation

```bash
# Create an analytical expert persona
python main.py --subject "Subject with Analytical Background" --instantiate --export
```

Query the generated persona about: Strategic planning, problem analysis, systematic approaches

### Use Case 3: Domain-Specific Expertise

```bash
# Create a domain expert persona  
python main.py --subject "Subject with Specific Domain Knowledge" --instantiate --export
```

Query the generated persona about: Their specific domain knowledge and expertise

## 🔧 Customization

### Edit a Soul Anchor

Soul anchors are YAML files in `agent_zero_framework/personas/{name}/persona_config.yaml`

```yaml
primary_name: "Subject Name"
archetype: "expert_type"
core_constants:
  - "Invariant trait 1"
  - "Invariant trait 2"
knowledge_domains:
  - category: "engineering"
    earth_1218_equivalent: "mechanical, electrical"
    proficiency_level: "expert"
```

### Add Knowledge Domains

```yaml
knowledge_domains:
  - category: "custom_domain"
    original_context: "Fictional ability"
    earth_1218_equivalent: "Real-world skills"
    proficiency_level: "expert|advanced|intermediate"
```

### Customize Communication Style

```yaml
communication_style:
  tone: "professional|casual|witty|serious"
  formality: "high|moderate|low"
  quirks:
    - "Specific speech pattern"
    - "Catchphrase or habit"
```

## 🐛 Troubleshooting

### Problem: Dependencies Missing

```bash
# Install all dependencies
pip install -r requirements.txt
pip install -r agent_zero_framework/requirements.txt
```

### Problem: Agent Zero Won't Launch

Make sure you've configured API keys. Agent Zero requires:
- OpenAI API key (or other LLM provider)
- Set in environment or Agent Zero config

```bash
export OPENAI_API_KEY="your-key-here"
```

See [Agent Zero documentation](https://github.com/agent0ai/agent-zero) for details.

### Problem: Soul Anchor Not Found

```bash
# Make sure you create it first
python main.py --subject "Character Name" --export

# Or use existing examples
python create_example_personas.py
```

### Problem: Import Errors

```bash
# Make sure you're in the project root
cd /path/to/Lucius-Fox-digital-person-Earth-1218

# Run from project root
python main.py --subject "Name"
```

## 📚 Next Steps

### 1. Test the Integration

```bash
# Run integration tests
python test_integration.py
```

### 2. Create Your Own Characters

```bash
# Full workflow for any character
python main.py --subject "Hermione Granger" --instantiate --export --graph
```

### 3. Refine and Iterate

1. Launch a persona
2. Interact and test knowledge
3. Edit the soul anchor YAML to refine
4. Regenerate with updated anchor

### 4. Build CIM (Conscious Intelligence Model)

Over time, each persona:
- Accumulates memory via Agent Zero
- Refines its knowledge base
- Develops more sophisticated responses
- Helps identify its own improvement areas

## 🎓 Learn More

- **Integration Guide**: [AGENT_ZERO_INTEGRATION.md](./AGENT_ZERO_INTEGRATION.md)
- **Genesis Engine**: [GENESIS_ENGINE.md](./GENESIS_ENGINE.md)
- **Full README**: [README.md](./README.md)
- **Agent Zero**: [github.com/agent0ai/agent-zero](https://github.com/agent0ai/agent-zero)

## 💡 Pro Tips

### Tip 1: Start with Examples

Use `create_example_personas.py` first to see how it works, then customize.

### Tip 2: Domain Expertise Matters

The quality of knowledge domains directly impacts the persona's ability to provide meaningful insights.

### Tip 3: Iterate on Prompts

Check `agent_zero_framework/personas/{name}/prompts/` and refine as needed.

### Tip 4: Memory is Key

Agent Zero's memory system allows personas to learn and improve over time.

### Tip 5: Person, Place, Time, Event

Each persona knows:
- **Person**: Who they are (identity, traits)
- **Place**: Where they exist (computational environment)
- **Time**: Current temporal context
- **Event**: The conversation/task at hand

This creates legally-recognized personhood in the digital space.

## 🤝 Support & Community

- **Issues**: Use GitHub Issues for bugs
- **Discussions**: Use GitHub Discussions for questions
- **Contributing**: PRs welcome for improvements

---

**Happy instantiating!** 🎉

Create meaningful, high-fidelity digital persons that bring real expertise and personality to every conversation.
