#!/usr/bin/env python3
"""
Example demonstrating the Uatu Genesis Engine Multiversal Swarm Framework.
This script shows how to use the framework programmatically.

Note: This uses generic subject examples for demonstration.
The system is designed to work with ANY subject, real or fictional.
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
    """Demonstrate the framework with example subjects."""
    
    # List of example subjects to analyze (can be real or fictional)
    # Replace with your own subjects of interest
    example_subjects = [
        "Example Subject A",  # Replace with actual subject
        "Example Subject B",  # Replace with actual subject
        "Example Subject C"   # Replace with actual subject
    ]
    
    output_dir = Path("./demo_output")
    output_dir.mkdir(exist_ok=True)
    
    print("=" * 80)
    print("UATU GENESIS ENGINE - MULTIVERSAL HISTORY FRAMEWORK DEMO")
    print("=" * 80)
    print()
    print("This demo shows how to generate soul anchors for any subject.")
    print("Update the example_subjects list above with your subjects of interest.")
    print()
    
    for subject_name in example_subjects:
        if "Example Subject" in subject_name:
            print(f"\n⚠️  Skipping '{subject_name}' (placeholder)")
            print("    Update example_subjects in the script with real subjects")
            continue
            
        print(f"\n{'='*80}")
        print(f"Processing: {subject_name}")
        print(f"{'='*80}\n")
        
        # Initialize orchestrator
        orchestrator = MultiversalSwarmOrchestrator()
        
        try:
            # Gather data
            profile = await orchestrator.gather_multiversal_history(subject_name)
            
            # Display summary
            print(f"\n✅ Data gathered for {profile.primary_name}")
            print(f"   Completeness: {profile.completeness_score:.1f}%")
            print(f"   Knowledge Domains: {len(profile.knowledge_domains)}")
            print(f"   Economic Events: {len(profile.economic_history)}")
            print(f"   Data Sources: {len(profile.data_sources)}")
            
            # Export data
            subject_safe = subject_name.replace(" ", "_").lower()
            json_path = output_dir / f"{subject_safe}_profile.json"
            orchestrator.export_profile(str(json_path))
            anchor_path = output_dir / f"{subject_safe}_soul_anchor.yaml"
            orchestrator.export_soul_anchor(str(anchor_path))
            
            # Generate graph
            graph_files = orchestrator.generate_graph(str(output_dir))
            
            print(f"   📁 Profile: {json_path}")
            print(f"   🔗 Soul Anchor: {anchor_path}")
            if graph_files:
                print(f"   📊 Graph: {graph_files['graph_image']}")
            
        except Exception as e:
            logger.error(f"Error processing {subject_name}: {e}", exc_info=True)
            continue
    
    print(f"\n{'='*80}")
    print("DEMO COMPLETE")
    print(f"All outputs saved to: {output_dir}")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    asyncio.run(demo())
