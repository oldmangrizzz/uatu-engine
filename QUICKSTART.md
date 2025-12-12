# Quick Start Guide

## Installation

```bash
# Clone the repository
git clone https://github.com/oldmangrizzz/Lucius-Fox-digital-person-Earth-1218.git
cd Lucius-Fox-digital-person-Earth-1218

# Install dependencies
pip install -r requirements.txt
```

## Basic Usage

### 1. Gather Character Data (Simple)
```bash
python main.py --subject "Tony Stark"
```

### 2. With JSON Export and Graph
```bash
python main.py --subject "Tony Stark" --export --graph
```

### 3. Custom Output Directory
```bash
python main.py --subject "Bruce Wayne" --output ./batman_results
```

### 4. Verbose Logging
```bash
python main.py --subject "Hermione Granger" --verbose
```

## Running the Demo

### Mock Demo (Works Without Internet)
```bash
python demo_mock.py
```
This creates a complete example with sample data for Tony Stark, showing:
- Multiversal identities across 3 universes
- 5 knowledge domains mapped to Earth-1218
- 5 economic events totaling $90B
- Complete graph visualization

### Example Demo (Requires Internet)
```bash
python example.py
```
Processes multiple characters: Tony Stark, Bruce Wayne, Hermione Granger

## Output Files

After running, you'll get:
- `{character}_profile.json` - Complete character data
- `{character}_soul_anchor.yaml` - Anchor YAML distilled from invariants/variants
- `{character}_multiversal_history.png` - Visual graph
- `{character}_multiversal_history.gexf` - Graph data for Gephi

## Programmatic Usage

```python
import asyncio
from uatu_genesis_engine import MultiversalSwarmOrchestrator

async def main():
    orchestrator = MultiversalSwarmOrchestrator()
    
    # Gather data
    profile = await orchestrator.gather_multiversal_history("Tony Stark")
    
    # Export JSON
    orchestrator.export_profile("./output/profile.json")
    
    # Generate graph
    graphs = orchestrator.generate_graph("./output")
    
    print(f"Completeness: {profile.completeness_score}%")
    print(f"Knowledge Domains: {len(profile.knowledge_domains)}")

asyncio.run(main())
```

## Understanding the Output

### Character Profile Structure
```json
{
  "primary_name": "Character Name",
  "aliases": ["Alias1", "Alias2"],
  "multiversal_identities": [
    {
      "universe_designation": "Earth-616",
      "character_name": "Name in that universe",
      "occupation": "Their job",
      "first_appearance": "Comic/Movie (Year)"
    }
  ],
  "knowledge_domains": [
    {
      "category": "engineering",
      "original_context": "How it works in their world",
      "earth_1218_equivalent": "Real-world equivalent",
      "proficiency_level": "Expert/Advanced/Intermediate"
    }
  ],
  "economic_history": [
    {
      "timestamp": "Year",
      "event_type": "inheritance/business_growth/etc",
      "amount": 1000000000.0,
      "description": "What happened"
    }
  ],
  "total_wealth_estimate": 12400000000.0,
  "completeness_score": 95.0
}
```

### Graph Visualization

The generated graph shows:
- **Red node**: The character (center)
- **Teal nodes**: Universes they exist in
- **Light teal nodes**: Knowledge domains
- **Yellow nodes**: Economic events
- **Orange node**: Total wealth

All nodes connect to the central character in a directed acyclic graph (DAG).

## Tips

1. **Internet Access Required**: The framework needs internet to scrape wikis
2. **Rate Limiting**: Add delays between requests for production use
3. **Data Quality**: Results depend on available online sources
4. **Custom Agents**: Easy to add more specialized agents
5. **Export Formats**: GEXF files can be opened in Gephi for advanced analysis

## Troubleshooting

### No data found
- Check internet connection
- Verify character name spelling
- Try alternative names/aliases

### Import errors
- Ensure all dependencies installed: `pip install -r requirements.txt`

### Graph not generating
- Check matplotlib installed correctly
- Verify output directory is writable

## Next Steps

1. Try different fictional characters
2. Examine the generated graphs in Gephi
3. Explore the JSON data structure
4. Extend with custom agents for specific data sources

For more information, see README.md and IMPLEMENTATION_SUMMARY.md
