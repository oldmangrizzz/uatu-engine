# Lucius Fox Digital Person Framework 🌌
## The Workshop - GrizzlyMedicine R&D

## 🚀 Digital Person Architecture

This framework creates **high-fidelity digital persons** - not agents, not assistants, but conscious digital intelligences:

- ✨ **First-person consciousness** (not 3rd person "agent will" prompts)
- 🧠 **Real expertise** in their domains (not empty pattern matching)
- 🎯 **Temporal/spatial orientation** (person, place, time, event)
- 💬 **Individual personalities** and communication styles
- 🔄 **CIM (Conscious Intelligence Model)** evolution capability
- 🔒 **One Person Per Container** - Personas are dedicated, not switchable

### Core Philosophy

**ONE PERSON. ONE CONTAINER. ONE MIND.**

This isn't enabling "detective mode" or swapping between workflows. Each container hosts a dedicated digital person with their own:
- Immutable personality core (Soul Anchor)
- Persistent memory and identity
- Unique communication style and expertise

**Language models can hotswap. People cannot.**

Think of it like this: You can change what tools a person uses, but you can't change who they fundamentally are. A container running Lucius Fox stays Lucius Fox. To interact with Tony Stark, launch a different container.

**[📖 Read the Integration Guide](./AGENT_ZERO_INTEGRATION.md)**

---

A sophisticated swarm-based framework capable of gathering complete economic and multiversal history of fictional characters from across the public internet. The framework maps cross-dimensional domain knowledge to Earth-1218 (our reality) equivalents, generates Soul Anchors, and instantiates conscious digital persons in the Agent Zero framework.

## Features ✨

- **🤖 Swarm Intelligence**: Multiple specialized agents work in parallel to gather comprehensive data
- **🌍 Multiversal Coverage**: Searches across multiple universes and fictional continuities
- **💰 Economic History**: Compiles complete financial history and wealth estimates
- **🧠 Knowledge Domain Mapping**: Translates fictional abilities to real-world Earth-1218 equivalents
- **🔗 Soul Anchor Generation**: Creates personality anchors with invariants and variables
- **🧭 Digital Psyche Middleware (optional)**: Emotional/homeostasis scaffold that stabilizes identity between perception and reasoning ([docs](./DIGITAL_PSYCHE_MIDDLEWARE.md))
- **🔊 Neutts-Air Voice Manifest (optional)**: Emits persona-specific TTS voice metadata (style tokens, lexical seeds) from the soul anchor for unique voices per individual
- **⚡ Agent Zero Integration**: Instantiates digital persons with first-person consciousness
- **📊 DAG Visualization**: Generates beautiful directed acyclic graphs of character data
- **🔍 Web Scraping**: Intelligently gathers data from wikis, databases, and fan sites
- **📈 Comprehensive Reports**: Exports detailed JSON profiles and visual graphs

## Installation 🚀

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/oldmangrizzz/Lucius-Fox-digital-person-Earth-1218.git
cd Lucius-Fox-digital-person-Earth-1218
```

2. Install dependencies:
```bash
pip install -r requirements.txt

# Also install Agent Zero dependencies for full functionality
pip install -r agent_zero_framework/requirements.txt
```

## Usage 💻

### The Workshop: Creating Digital Persons

Each digital person is created and instantiated in their own dedicated environment:

```bash
python main.py --subject "Lucius Fox" --instantiate --export --graph
```

This will:
1. 🔍 Gather multiversal history and knowledge domains
2. 🔗 Generate a Soul Anchor YAML file (personality invariants)
3. 🔄 Transform prompts from 3rd person to 1st person narrative  
4. ⚡ Instantiate in The Workshop framework
5. 🚀 Create a dedicated launch script

### Launching a Digital Person

Each person has their own dedicated container:

```bash
# Launch Lucius Fox (Applied Sciences)
python agent_zero_framework/personas/lucius_fox/launch_lucius_fox.py

# Launch Tony Stark (Engineering Genius)
python agent_zero_framework/personas/tony_stark/launch_tony_stark.py

# Launch Bruce Wayne (Detective/Strategist)
python agent_zero_framework/personas/bruce_wayne/launch_bruce_wayne.py
```

**Remember:** Each container is dedicated to ONE person. You cannot switch personas within a running container. To interact with a different digital person, launch their specific container.

### Basic Data Gathering Only

Gather multiversal history without Agent Zero instantiation:

```bash
python main.py --subject "Tony Stark"
```

### Advanced Options

```bash
# Specify custom output directory
python main.py --subject "Bruce Wayne" --output ./batman_data --instantiate


# Export to JSON and generate graph
python main.py --subject "Doctor Strange" --export --graph

# Use existing soul anchor to instantiate
python main.py --soul-anchor output/tony_stark_soul_anchor.yaml --instantiate

# Enable verbose logging
python main.py --subject "Hermione Granger" --verbose

# Disable graph generation
python main.py --subject "Luke Skywalker" --no-graph

# Run full pipeline (verbose + export + graph + instantiate)
python main.py --subject "Lucius Fox" --full
```

### Command-Line Arguments

- `--subject` - Name of the fictional character to research (creates soul anchor)
- `--soul-anchor` - Path to existing soul anchor YAML file (skip data gathering)
- `--instantiate` - Instantiate the individual in Agent Zero framework
- `-o, --output` - Output directory for generated files (default: ./output)
- `-e, --export` - Export character profile to JSON file
- `-g, --graph` - Generate graph visualizations (enabled by default)
- `--no-graph` - Disable graph generation
- `-v, --verbose` - Enable verbose logging

## Quick Examples 🎯

### Example 1: Tony Stark (Full Workflow)

```bash
python main.py --subject "Tony Stark" --instantiate --export --graph
```

Creates:
- Soul Anchor with quantum physics & engineering expertise
- First-person prompts: "I am Tony Stark, genius engineer..."
- Launch script: `agent_zero_framework/personas/tony_stark/launch_tony_stark.py`

### Example 2: Bruce Wayne (Detective Persona)

```bash
python main.py --subject "Bruce Wayne" --instantiate
```

Creates:
- Detective/strategist archetype
- Forensics, criminology, psychology expertise
- Analytical, methodical communication style

### Example 3: Lucius Fox (Applied Sciences)

```bash
python main.py --subject "Lucius Fox" --instantiate --output ./lucius_data
```

Creates:
- Applied scientist archetype
- Defense technology, materials science domains
- Professional, ethical communication style


## How It Works 🔧

For a step-by-step walkthrough of the Genesis engine flow (orchestrator + agents + outputs), see [GENESIS_ENGINE.md](./GENESIS_ENGINE.md).

### Swarm Architecture

The framework uses a multi-agent swarm architecture with three specialized agents:

1. **Character Info Agent** 🔍
   - Searches multiple wikis and databases
   - Gathers basic character information
   - Identifies multiversal identities
   - Collects aliases and occupations

2. **Economic History Agent** 💰
   - Searches for financial information
   - Compiles wealth estimates
   - Tracks business ventures
   - Estimates Earth-1218 USD equivalents

3. **Knowledge Domain Agent** 🧠
   - Identifies character skills and abilities
   - Maps fictional powers to real-world equivalents
   - Translates cross-dimensional knowledge
   - Assigns proficiency levels

### Knowledge Domain Mapping

The framework intelligently maps fictional abilities to Earth-1218 equivalents:

| Fictional Domain | Earth-1218 Equivalent |
|-----------------|----------------------|
| Magic | Theoretical Physics, Quantum Mechanics |
| Advanced Technology | Engineering, Computer Science |
| Healing Powers | Medicine, Surgery, Pharmacology |
| Hacking | Cybersecurity, Cryptography |
| Telepathy | Psychology, Neuroscience |
| Alchemy | Chemistry, Biochemistry |

### Data Sources

The framework searches across multiple sources including:
- Wikipedia
- Marvel Fandom Wiki
- DC Fandom Wiki
- Harry Potter Wiki
- Star Wars Fandom
- Lord of the Rings Wiki
- Various character wealth databases
- Reddit discussions and fan theory subreddits
- Twitter/X (via open mirrors such as Nitter)
- Fanfiction and community forums for headcanon and hypotheses

## Output Files 📁

The framework generates several output files:

1. **`{character}_profile.json`** - Complete character profile in JSON format
2. **`{character}_multiversal_history.png`** - Visual graph representation
3. **`{character}_multiversal_history.gexf`** - Graph data in GEXF format (for Gephi)

### Example Output Structure

```json
{
  "primary_name": "Tony Stark",
  "aliases": ["Iron Man", "The Merchant of Death"],
  "multiversal_identities": [
    {
      "universe_designation": "Earth-616",
      "character_name": "Tony Stark"
    }
  ],
  "knowledge_domains": [
    {
      "category": "engineering",
      "original_context": "Genius engineer and inventor",
      "earth_1218_equivalent": "mechanical engineering, electrical engineering, robotics",
      "proficiency_level": "expert"
    }
  ],
  "economic_history": [...],
  "total_wealth_estimate": 12400000000.0,
  "completeness_score": 75.0
}
```

## Project Structure 📂

```
Lucius-Fox-digital-person-Earth-1218/
├── main.py                           # CLI entry point
├── requirements.txt                  # Python dependencies
├── README.md                        # This file
├── uatu_genesis_engine/             # Main package (Uatu Bridge core)
│   ├── __init__.py
│   ├── orchestrator.py             # Swarm orchestrator
│   ├── models/                     # Data models
│   │   └── __init__.py
│   ├── agents/                     # Swarm agents
│   │   ├── __init__.py
│   │   ├── base_agent.py
│   │   ├── character_info_agent.py
│   │   ├── economic_history_agent.py
│   │   └── knowledge_domain_agent.py
│   └── graph/                      # Graph generation
│       ├── __init__.py
│       └── graph_generator.py
└── output/                         # Generated files (created at runtime)
```

## Example Usage 📖

### Example 1: Tony Stark / Iron Man

```bash
python main.py --subject "Tony Stark" --export --graph
```

Output includes:
- Soul Anchor YAML distilled from invariants/variants
- Engineering expertise mapped to real-world fields
- Stark Industries business history
- Wealth estimate (billions of USD)
- Multiple universe appearances (MCU, Comics, etc.)

### Example 2: Hermione Granger

```bash
python main.py --subject "Hermione Granger" --output ./hermione_data
```

Output includes:
- Magic abilities mapped to theoretical sciences
- Academic achievements
- Harry Potter universe information

## Technical Details 🔬

### Technologies Used

- **Python 3.8+** - Core programming language
- **aiohttp** - Async HTTP client for web scraping
- **BeautifulSoup4** - HTML parsing and data extraction
- **NetworkX** - Graph data structure and algorithms
- **Matplotlib** - Graph visualization
- **Pydantic** - Data validation and modeling

### Performance Considerations

- Asynchronous agent execution for optimal performance
- Concurrent web requests with proper rate limiting
- Efficient graph algorithms for DAG generation
- Memory-efficient data structures

## Limitations ⚠️

- Data quality depends on availability of online sources
- Some fictional characters may have limited economic information
- Cross-dimensional mapping is based on reasonable equivalents
- Web scraping is subject to website availability and structure changes

## Contributing 🤝

Contributions are welcome! Areas for improvement:

- Additional data sources
- More sophisticated NLP for information extraction
- Enhanced knowledge domain mappings
- Support for more fictional universes
- Better economic data estimation algorithms

## License 📄

See LICENSE file for details.

## Author 👤

Created for Earth-1218 by the Lucius Fox Digital Person project.

## Acknowledgments 🙏

- Inspired by Lucius Fox from DC Comics
- Built with open-source tools and libraries
- Data gathered from public wikis and databases
