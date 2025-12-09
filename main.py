#!/usr/bin/env python3
"""
Lucius Fox Multiversal History Swarm Framework
Main CLI entry point
"""
import asyncio
import argparse
import sys
import logging
from pathlib import Path

from lucius_fox_swarm import MultiversalSwarmOrchestrator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Gather complete multiversal history and economic data for fictional characters",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Gather data for Tony Stark
  python main.py "Tony Stark"
  
  # Gather data and specify output directory
  python main.py "Bruce Wayne" --output ./batman_data
  
  # Export to JSON and generate graph
  python main.py "Doctor Strange" --export --graph
        """
    )
    
    parser.add_argument(
        "character_name",
        type=str,
        help="Name of the fictional character to research"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="./output",
        help="Output directory for generated files (default: ./output)"
    )
    
    parser.add_argument(
        "-e", "--export",
        action="store_true",
        help="Export character profile to JSON file"
    )
    
    parser.add_argument(
        "-g", "--graph",
        action="store_true",
        help="Generate graph visualizations"
    )
    
    parser.add_argument(
        "--no-graph",
        action="store_true",
        help="Disable graph generation (overrides --graph)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run the swarm framework
    try:
        asyncio.run(run_swarm(args))
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=args.verbose)
        sys.exit(1)


async def run_swarm(args):
    """Run the swarm orchestrator."""
    character_name = args.character_name
    output_dir = Path(args.output)
    
    logger.info("=" * 80)
    logger.info(f"LUCIUS FOX MULTIVERSAL HISTORY SWARM FRAMEWORK")
    logger.info(f"Target Character: {character_name}")
    logger.info(f"Output Directory: {output_dir}")
    logger.info("=" * 80)
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize orchestrator
    orchestrator = MultiversalSwarmOrchestrator()
    
    # Gather multiversal history
    print("\n🔍 Gathering multiversal history...")
    profile = await orchestrator.gather_multiversal_history(character_name)
    
    # Display summary
    print("\n" + "=" * 80)
    print(f"📊 SUMMARY FOR {profile.primary_name}")
    print("=" * 80)
    print(f"Aliases: {', '.join(profile.aliases) if profile.aliases else 'None found'}")
    print(f"Multiversal Identities: {len(profile.multiversal_identities)}")
    print(f"Knowledge Domains: {len(profile.knowledge_domains)}")
    print(f"Economic Events: {len(profile.economic_history)}")
    
    if profile.total_wealth_estimate:
        print(f"Estimated Wealth (Earth-1218 USD): ${profile.total_wealth_estimate:,.2f}")
    else:
        print("Estimated Wealth: Not available")
    
    print(f"Data Sources: {len(profile.data_sources)}")
    print(f"Completeness Score: {profile.completeness_score:.1f}%")
    print("=" * 80)
    
    # Print knowledge domains
    if profile.knowledge_domains:
        print("\n🧠 KNOWLEDGE DOMAINS (Cross-Dimensional Mapping):")
        print("-" * 80)
        for domain in profile.knowledge_domains:
            print(f"  • {domain.category.upper()}")
            print(f"    Original: {domain.original_context}")
            print(f"    Earth-1218 Equivalent: {domain.earth_1218_equivalent}")
            print(f"    Proficiency: {domain.proficiency_level}")
            print()
    
    # Print multiversal identities
    if profile.multiversal_identities:
        print("\n🌍 MULTIVERSAL IDENTITIES:")
        print("-" * 80)
        for identity in profile.multiversal_identities:
            print(f"  • {identity.universe_designation}: {identity.character_name}")
    
    # Print economic history sample
    if profile.economic_history:
        print("\n💰 ECONOMIC HISTORY (Sample):")
        print("-" * 80)
        for event in profile.economic_history[:5]:  # Show first 5
            print(f"  • {event.event_type}: {event.description[:100]}...")
        if len(profile.economic_history) > 5:
            print(f"  ... and {len(profile.economic_history) - 5} more events")
    
    # Export profile to JSON
    if args.export or args.graph:
        char_name_safe = character_name.replace(" ", "_").lower()
        json_path = output_dir / f"{char_name_safe}_profile.json"
        orchestrator.export_profile(str(json_path))
        print(f"\n✅ Profile exported to: {json_path}")
    
    # Generate graph visualizations
    # Generate by default unless --no-graph is specified
    should_generate_graph = args.graph or (not args.no_graph and not args.graph)
    if should_generate_graph:
        print("\n📈 Generating graph visualizations...")
        graph_files = orchestrator.generate_graph(str(output_dir))
        
        if graph_files:
            print(f"✅ Graph image saved to: {graph_files['graph_image']}")
            print(f"✅ Graph data (GEXF) saved to: {graph_files['graph_data']}")
            print(f"   Graph Stats: {graph_files['stats']}")
    
    print("\n" + "=" * 80)
    print("🎉 Multiversal history gathering complete!")
    print("=" * 80)
    

if __name__ == "__main__":
    main()
