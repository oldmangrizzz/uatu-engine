#!/usr/bin/env python3
"""
Example demonstrating the Lucius Fox Multiversal Swarm Framework.
This script shows how to use the framework programmatically.
"""
import asyncio
import logging
from pathlib import Path

from uatu_genesis_engine import MultiversalSwarmOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def demo():
    """Demonstrate the framework with example characters."""
    
    # List of example characters to analyze
    example_characters = [
        "Tony Stark",
        "Bruce Wayne", 
        "Hermione Granger"
    ]
    
    output_dir = Path("./demo_output")
    output_dir.mkdir(exist_ok=True)
    
    print("=" * 80)
    print("LUCIUS FOX MULTIVERSAL HISTORY SWARM FRAMEWORK - DEMO")
    print("=" * 80)
    print()
    
    for character_name in example_characters:
        print(f"\n{'='*80}")
        print(f"Processing: {character_name}")
        print(f"{'='*80}\n")
        
        # Initialize orchestrator
        orchestrator = MultiversalSwarmOrchestrator()
        
        try:
            # Gather data
            profile = await orchestrator.gather_multiversal_history(character_name)
            
            # Display summary
            print(f"\n✅ Data gathered for {profile.primary_name}")
            print(f"   Completeness: {profile.completeness_score:.1f}%")
            print(f"   Knowledge Domains: {len(profile.knowledge_domains)}")
            print(f"   Economic Events: {len(profile.economic_history)}")
            print(f"   Data Sources: {len(profile.data_sources)}")
            
            # Export data
            char_safe = character_name.replace(" ", "_").lower()
            json_path = output_dir / f"{char_safe}_profile.json"
            orchestrator.export_profile(str(json_path))
            anchor_path = output_dir / f"{char_safe}_soul_anchor.yaml"
            orchestrator.export_soul_anchor(str(anchor_path))
            
            # Generate graph
            graph_files = orchestrator.generate_graph(str(output_dir))
            
            print(f"   📁 Profile: {json_path}")
            print(f"   🔗 Soul Anchor: {anchor_path}")
            if graph_files:
                print(f"   📊 Graph: {graph_files['graph_image']}")
            
        except Exception as e:
            logger.error(f"Error processing {character_name}: {e}", exc_info=True)
            continue
    
    print(f"\n{'='*80}")
    print("DEMO COMPLETE")
    print(f"All outputs saved to: {output_dir}")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    asyncio.run(demo())
