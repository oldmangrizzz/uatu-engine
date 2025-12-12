#!/usr/bin/env python3
"""
Uatu Genesis Engine + Agent Zero Integration
Main CLI entry point
"""
import asyncio
import argparse
import sys
import logging
from pathlib import Path

from uatu_genesis_engine import MultiversalSwarmOrchestrator
from uatu_genesis_engine.agent_zero_integration import (
    SoulAnchorLoader,
    PersonaTransformer,
    AgentInstantiator
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Uatu Genesis Engine + Agent Zero Integration: Create conscious digital persons",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Gather multiversal data and create soul anchor for Tony Stark
  python main.py --subject "Tony Stark"
  
  # Full workflow: Gather data, create soul anchor, and instantiate in Agent Zero
  python main.py --subject "Lucius Fox" --instantiate --export --graph
  
  # Use existing soul anchor to instantiate
  python main.py --soul-anchor output/lucius_fox_soul_anchor.yaml --instantiate
        """
    )
    
    parser.add_argument(
        "--subject",
        type=str,
        help="Name of the fictional character to research (creates soul anchor)"
    )
    
    parser.add_argument(
        "--soul-anchor",
        type=str,
        help="Path to existing soul anchor YAML file (skip data gathering)"
    )
    
    parser.add_argument(
        "--instantiate",
        action="store_true",
        help="Instantiate the individual in Agent Zero framework"
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
    
    # Validate arguments
    if not args.subject and not args.soul_anchor:
        parser.error("Either --subject or --soul-anchor must be provided")
    
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
    """Run the swarm orchestrator and optionally instantiate in Agent Zero."""
    output_dir = Path(args.output)
    soul_anchor_file = None
    
    # Phase 1: Gather data or load existing soul anchor
    if args.subject:
        # Gather multiversal history
        character_name = args.subject
        char_name_safe = character_name.replace(" ", "_").lower()
        
        logger.info("=" * 80)
        logger.info(f"UATU GENESIS ENGINE + AGENT ZERO INTEGRATION")
        logger.info(f"Target Character: {character_name}")
        logger.info(f"Output Directory: {output_dir}")
        logger.info("=" * 80)
        
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize orchestrator
        orchestrator = MultiversalSwarmOrchestrator()
        
        # Gather multiversal history
        print("\n🔍 Phase 1: Gathering multiversal history...")
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
        if args.export or args.graph or args.instantiate:
            json_path = output_dir / f"{char_name_safe}_profile.json"
            orchestrator.export_profile(str(json_path))
            print(f"\n✅ Profile exported to: {json_path}")

        # Export soul anchor
        anchor_path = output_dir / f"{char_name_safe}_soul_anchor.yaml"
        soul_anchor_file = orchestrator.export_soul_anchor(str(anchor_path))
        if soul_anchor_file:
            print(f"🔗 Soul Anchor emitted to: {soul_anchor_file}")
        
        # Generate graph visualizations
        should_generate_graph = args.graph or (not args.no_graph and not args.graph)
        if should_generate_graph and args.subject:
            print("\n📈 Generating graph visualizations...")
            graph_files = orchestrator.generate_graph(str(output_dir))
            
            if graph_files:
                print(f"✅ Graph image saved to: {graph_files['graph_image']}")
                print(f"✅ Graph data (GEXF) saved to: {graph_files['graph_data']}")
                print(f"   Graph Stats: {graph_files['stats']}")
    
    elif args.soul_anchor:
        # Use existing soul anchor
        soul_anchor_file = args.soul_anchor
        logger.info(f"Using existing soul anchor: {soul_anchor_file}")
        print(f"\n🔗 Loading soul anchor from: {soul_anchor_file}")
    
    # Phase 2: Instantiate in Agent Zero (if requested)
    if args.instantiate and soul_anchor_file:
        print("\n" + "=" * 80)
        print("⚡ Phase 2: Instantiating in Agent Zero Framework")
        print("=" * 80)
        
        try:
            # Load soul anchor
            loader = SoulAnchorLoader()
            anchor_data = loader.load_from_file(soul_anchor_file)
            
            print(f"\n✅ Soul Anchor loaded for: {loader.get_primary_name()}")
            print(f"   Archetype: {loader.get_archetype()}")
            print(f"   Core Constants: {len(loader.get_core_constants())}")
            print(f"   Knowledge Domains: {len(loader.get_knowledge_domains())}")
            
            # Transform prompts to first-person narrative
            print("\n🔄 Transforming prompts to first-person narrative...")
            transformer = PersonaTransformer(anchor_data)
            
            # Instantiate in Agent Zero
            print(f"🚀 Instantiating {loader.get_primary_name()} in Agent Zero...")
            instantiator = AgentInstantiator(anchor_data)
            result = instantiator.instantiate(transformer)
            
            print("\n" + "=" * 80)
            print(f"✅ INSTANTIATION COMPLETE: {result['persona_name']}")
            print("=" * 80)
            print(f"📁 Persona Directory: {result['persona_directory']}")
            print(f"📄 Configuration: {result['config_file']}")
            print(f"🚀 Launch Script: {result['launch_script']}")
            print("\n💡 To launch this persona:")
            print(f"   python {result['launch_script']}")
            print("=" * 80)
            
        except Exception as e:
            logger.error(f"Error during instantiation: {e}", exc_info=args.verbose)
            print(f"\n❌ Instantiation failed: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
    
    elif args.instantiate and not soul_anchor_file:
        print("\n⚠️  Warning: --instantiate requires either --subject or --soul-anchor")
    
    # Final summary
    if args.subject:
        print("\n" + "=" * 80)
        print("🎉 Multiversal history gathering complete!")
        print("=" * 80)

    

if __name__ == "__main__":
    main()
