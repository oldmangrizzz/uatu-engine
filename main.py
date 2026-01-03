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
    AgentInstantiator,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
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
        """,
    )

    parser.add_argument(
        "--subject",
        type=str,
        help="Name of the fictional character to research (creates soul anchor)",
    )

    parser.add_argument(
        "--soul-anchor",
        type=str,
        help="Path to existing soul anchor YAML file (skip data gathering)",
    )

    parser.add_argument(
        "--instantiate",
        action="store_true",
        help="Instantiate the individual in Agent Zero framework",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="./output",
        help="Output directory for generated files (default: ./output)",
    )

    parser.add_argument(
        "-e",
        "--export",
        action="store_true",
        help="Export character profile to JSON file",
    )

    parser.add_argument(
        "-g", "--graph", action="store_true", help="Generate graph visualizations"
    )

    parser.add_argument(
        "--no-graph",
        action="store_true",
        help="Disable graph generation (overrides --graph)",
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging"
    )

    parser.add_argument(
        "--full",
        action="store_true",
        help="Run full pipeline: verbose logging, export profile, generate graph, and instantiate persona",
    )

    parser.add_argument(
        "--deploy",
        action="store_true",
        help="Deploy instantiated persona to HuggingFace Space + Convex (requires --instantiate)",
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.subject and not args.soul_anchor:
        parser.error("Either --subject or --soul-anchor must be provided")

    if args.full:
        args.export = True
        args.graph = True
        args.instantiate = True
        args.deploy = False  # Don't auto-deploy; prompt user interactively
        args.verbose = True

    if args.verbose or args.full:
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
    log_file_handler = None

    # Phase 1: Gather data or load existing soul anchor
    if args.subject:
        # Gather multiversal history
        character_name = args.subject
        char_name_safe = character_name.replace(" ", "_").lower()

        logger.info("=" * 80)
        logger.info("UATU GENESIS ENGINE + AGENT ZERO INTEGRATION")
        logger.info(f"Target Character: {character_name}")
        logger.info(f"Output Directory: {output_dir}")
        logger.info("=" * 80)

        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)

        if args.full:
            log_path = output_dir / "full_run.log"
            file_handler = logging.FileHandler(log_path, encoding="utf-8")
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
            )
            logging.getLogger().addHandler(file_handler)
            log_file_handler = file_handler

        # Initialize orchestrator
        orchestrator = MultiversalSwarmOrchestrator()

        # Gather multiversal history
        print("\n🔍 Phase 1: Gathering multiversal history...")
        profile = await orchestrator.gather_multiversal_history(character_name)

        # Display summary
        print("\n" + "=" * 80)
        print(f"📊 SUMMARY FOR {profile.primary_name}")
        print("=" * 80)
        print(
            f"Aliases: {', '.join(profile.aliases) if profile.aliases else 'None found'}"
        )
        print(f"Multiversal Identities: {len(profile.multiversal_identities)}")
        print(f"Knowledge Domains: {len(profile.knowledge_domains)}")
        print(f"Economic Events: {len(profile.economic_history)}")

        if profile.total_wealth_estimate:
            print(
                f"Estimated Wealth (Earth-1218 USD): ${profile.total_wealth_estimate:,.2f}"
            )
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

        # ===== NEW: COMPILE GRAPHMERT =====
        print("\n" + "=" * 80)
        print("🧠 Phase 1.5: Compiling GraphMERT (Neurosymbolic Knowledge Graph)")
        print("=" * 80)

        from uatu_genesis_engine.graphmert import GraphMERTCompiler
        from uatu_genesis_engine.utils.convex_seeder import ConvexSeeder

        # Compile the knowledge graph
        compiler = GraphMERTCompiler()
        graphmert_data = compiler.compile(profile)

        print("\n✅ GraphMERT compiled:")
        print(f"   Nodes: {graphmert_data.node_count}")
        print(f"   Facts: {graphmert_data.edge_count}")
        print(f"   Root Invariants: {len(graphmert_data.root_invariants)}")

        # Save GraphMERT to local file
        graphmert_path = output_dir / f"{char_name_safe}_graphmert.json"
        with open(graphmert_path, "w", encoding="utf-8") as f:
            import json

            json.dump(graphmert_data.to_dict(), f, indent=2)
        print(f"   Saved to: {graphmert_path}")

        # Seed to Convex (mock mode for now)
        print("\n🌐 Seeding GraphMERT to Convex...")
        seeder = ConvexSeeder(
            mock_mode=True
        )  # Use mock mode unless Convex URL provided
        seed_result = await seeder.seed_mind(graphmert_data)

        if seed_result.get("mock_mode"):
            print(f"   [MOCK MODE] Saved backup to: {seed_result.get('backup_file')}")
        else:
            print("✅ Seeded to Convex successfully")

        print("=" * 80)
        # ===== END GRAPHMERT COMPILATION =====

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

    # Phase 1.5: Model Selection
    model_config = None
    if args.instantiate and soul_anchor_file:
        print("\n" + "=" * 80)
        print("🧠 Model Selection: Choose the LLM backbone for this digital person")
        print("=" * 80)
        print("\nAvailable model tiers (via OpenRouter):")
        print()
        print("  [1] Budget Tier (~$0.10-0.50/M tokens)")
        print("      • google/gemma-2-9b-it")
        print("      • meta-llama/llama-3.1-8b-instruct")
        print("      • qwen/qwen-2.5-7b-instruct")
        print()
        print("  [2] Balanced Tier (~$0.50-2.00/M tokens) [RECOMMENDED]")
        print("      • anthropic/claude-3-haiku")
        print("      • google/gemini-2.0-flash-001")
        print("      • deepseek/deepseek-chat-v3-0324")
        print()
        print("  [3] Premium Tier (~$3.00-15.00/M tokens)")
        print("      • anthropic/claude-sonnet-4")
        print("      • openai/gpt-4o")
        print("      • google/gemini-2.5-pro-preview")
        print()
        print("  [4] GitHub Copilot (if you have Pro/Pro+)")
        print("      • Uses your existing Copilot subscription")
        print()
        print("  [5] Custom - Enter your own OpenRouter model ID")
        print()

        tier_choice = input("Select tier [1-5] (default: 2): ").strip() or "2"

        # Model options by tier
        tier_models = {
            "1": [
                ("google/gemma-2-9b-it", "Gemma 2 9B - Google's efficient open model"),
                ("meta-llama/llama-3.1-8b-instruct", "Llama 3.1 8B - Meta's workhorse"),
                (
                    "qwen/qwen-2.5-7b-instruct",
                    "Qwen 2.5 7B - Alibaba's strong performer",
                ),
            ],
            "2": [
                (
                    "anthropic/claude-3-haiku",
                    "Claude 3 Haiku - Fast, smart, affordable",
                ),
                (
                    "google/gemini-2.0-flash-001",
                    "Gemini 2.0 Flash - Google's speed demon",
                ),
                ("deepseek/deepseek-chat-v3-0324", "DeepSeek V3 - Incredible value"),
            ],
            "3": [
                ("anthropic/claude-sonnet-4", "Claude Sonnet 4 - Top-tier reasoning"),
                ("openai/gpt-4o", "GPT-4o - OpenAI's flagship"),
                ("google/gemini-2.5-pro-preview", "Gemini 2.5 Pro - Google's best"),
            ],
        }

        if tier_choice == "4":
            # GitHub Copilot
            model_config = {
                "provider": "github_copilot",
                "model": "gpt-4o",  # Copilot uses GPT-4o under the hood
                "display_name": "GitHub Copilot (GPT-4o)",
            }
            print(f"\n✅ Selected: GitHub Copilot")
        elif tier_choice == "5":
            # Custom model
            custom_model = input(
                "Enter OpenRouter model ID (e.g., 'anthropic/claude-3-opus'): "
            ).strip()
            if custom_model:
                model_config = {
                    "provider": "openrouter",
                    "model": custom_model,
                    "display_name": f"Custom: {custom_model}",
                }
                print(f"\n✅ Selected: {custom_model}")
            else:
                print("⚠️  No model entered, using default (Claude 3 Haiku)")
                model_config = {
                    "provider": "openrouter",
                    "model": "anthropic/claude-3-haiku",
                    "display_name": "Claude 3 Haiku",
                }
        elif tier_choice in tier_models:
            # Show models in selected tier
            models = tier_models[tier_choice]
            print(f"\nModels in this tier:")
            for i, (model_id, desc) in enumerate(models, 1):
                print(f"  [{i}] {desc}")
                print(f"      {model_id}")
            print()

            model_choice = (
                input(f"Select model [1-{len(models)}] (default: 1): ").strip() or "1"
            )
            try:
                idx = int(model_choice) - 1
                if 0 <= idx < len(models):
                    selected = models[idx]
                else:
                    selected = models[0]
            except ValueError:
                selected = models[0]

            model_config = {
                "provider": "openrouter",
                "model": selected[0],
                "display_name": selected[1].split(" - ")[0],
            }
            print(f"\n✅ Selected: {selected[0]}")
        else:
            # Default to balanced tier, first option
            model_config = {
                "provider": "openrouter",
                "model": "anthropic/claude-3-haiku",
                "display_name": "Claude 3 Haiku",
            }
            print(f"\n✅ Using default: anthropic/claude-3-haiku")

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
            result = instantiator.instantiate(transformer, model_config=model_config)

            print("\n" + "=" * 80)
            print(f"✅ INSTANTIATION COMPLETE: {result['persona_name']}")
            print("=" * 80)
            print(f"📁 Persona Directory: {result['persona_directory']}")
            print(f"📄 Configuration: {result['config_file']}")
            print(f"🚀 Launch Script: {result['launch_script']}")
            print("\n💡 To launch this persona:")
            print(f"   python {result['launch_script']}")
            print("=" * 80)

            # Phase 3: Cloud Deployment (interactive prompt)
            print("\n" + "=" * 80)
            print("☁️  Phase 3: Deployment Options")
            print("=" * 80)
            print("\nWhere would you like this digital person to live?")
            print("  [1] Local only (Workshop) - Run from this machine")
            print("  [2] HuggingFace Space - Container in the cloud")
            print("  [3] Google Cloud (coming soon)")
            print("  [4] Skip deployment for now")
            print()

            deploy_choice = input("Enter choice [1-4] (default: 1): ").strip() or "1"

            if deploy_choice == "2":
                print("\n☁️  Deploying to HuggingFace Space...")
                from uatu_genesis_engine.deployment.cloud_deployer import CloudDeployer
                import os

                hf_token = os.environ.get("HF_TOKEN")
                if not hf_token:
                    print(
                        "❌ HF_TOKEN not found in environment. Cannot deploy to HuggingFace."
                    )
                    print("   Set HF_TOKEN in your .env file and try again.")
                else:
                    try:
                        deployer = CloudDeployer(hf_token=hf_token)

                        # Deploy to HuggingFace Space (also creates Convex project)
                        space_url = deployer.deploy_persona(
                            persona_path=result["persona_directory"]
                        )

                        print("\n" + "=" * 80)
                        print(f"✅ CLOUD DEPLOYMENT COMPLETE")
                        print("=" * 80)
                        print(f"🌐 HuggingFace Space: {space_url}")
                        print("=" * 80)

                    except Exception as deploy_err:
                        logger.error(
                            f"Cloud deployment failed: {deploy_err}",
                            exc_info=args.verbose,
                        )
                        print(f"\n❌ Cloud deployment failed: {deploy_err}")
                        if args.verbose:
                            import traceback

                            traceback.print_exc()

            elif deploy_choice == "3":
                print("\n⏳ Google Cloud deployment is not yet implemented.")
                print("   This feature is coming soon!")

            elif deploy_choice == "4":
                print("\n⏭️  Skipping deployment. Your persona is ready locally.")

            else:
                # Default to local (choice 1 or invalid input)
                print("\n✅ Persona configured for local operation.")
                print(f"   Launch with: python {result['launch_script']}")

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

    if log_file_handler:
        logging.getLogger().removeHandler(log_file_handler)
        log_file_handler.close()


if __name__ == "__main__":
    main()
