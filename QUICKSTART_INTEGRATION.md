# Quick Start Guide: Lucius Fox Digital Person Framework

## 🚀 5-Minute Quick Start

### Step 1: Install Dependencies

```bash
# Clone the repository (if you haven't already)
git clone https://github.com/oldmangrizzz/Lucius-Fox-digital-person-Earth-1218.git
cd Lucius-Fox-digital-person-Earth-1218

# Install Python dependencies
pip install -r requirements.txt

# Optional: Install Agent Zero dependencies for full functionality
pip install -r agent_zero_framework/requirements.txt
```

### Step 2: Create Your First Digital Person

#### Option A: Use Pre-configured Examples

```bash
# Create Tony Stark, Bruce Wayne, and Lucius Fox personas
python create_example_personas.py
```

This creates three ready-to-use digital persons with full expertise and personality.

#### Option B: Create a Custom Character

```bash
# Gather data and create a new persona
python main.py --subject "Doctor Strange" --instantiate --export
```

### Step 3: Launch a Digital Person

```bash
# Launch Tony Stark
python agent_zero_framework/personas/tony_stark/launch_tony_stark.py

# Or launch Lucius Fox
python agent_zero_framework/personas/lucius_fox/launch_lucius_fox.py

# Or launch Bruce Wayne
python agent_zero_framework/personas/bruce_wayne/launch_bruce_wayne.py
```

**Note**: For launching Agent Zero, you'll need to configure API keys for LLM providers. See Agent Zero documentation.

## 📖 What Just Happened?

### The Magic Behind the Scenes

1. **Uatu Genesis Engine** gathered multiversal history about the character
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

Lucius Fox Framework:
```
"I am Tony Stark. I approach problems through my expertise in 
quantum mechanics and engineering. When discussing arc reactor 
technology, I draw from my deep knowledge of clean energy 
research and materials science..."
```

## 🎯 Common Use Cases

### Use Case 1: Technical Expert Consultation

```bash
# Create an engineering expert (Tony Stark)
python create_example_personas.py

# Launch Tony Stark persona
python agent_zero_framework/personas/tony_stark/launch_tony_stark.py
```

Ask about: Quantum mechanics, AI systems, clean energy, aerospace engineering

### Use Case 2: Detective/Strategic Analysis

```bash
# Create a detective expert (Bruce Wayne)
python create_example_personas.py

# Launch Bruce Wayne persona
python agent_zero_framework/personas/bruce_wayne/launch_bruce_wayne.py
```

Ask about: Crime analysis, strategic planning, forensics, psychology

### Use Case 3: Applied Sciences & Ethics

```bash
# Create an applied scientist (Lucius Fox)
python create_example_personas.py

# Launch Lucius Fox persona
python agent_zero_framework/personas/lucius_fox/launch_lucius_fox.py
```

Ask about: Defense technology, materials science, ethical innovation

## 🔧 Customization

### Edit a Soul Anchor

Soul anchors are YAML files in `agent_zero_framework/personas/{name}/persona_config.yaml`

```yaml
primary_name: "Your Character"
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
