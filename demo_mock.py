#!/usr/bin/env python3
"""
Mock demonstration of the Lucius Fox Multiversal Swarm Framework with sample data.
This shows what the output would look like with real internet access.
"""
import asyncio
import json
from pathlib import Path
from datetime import datetime

from uatu_genesis_engine import (
    MultiversalSwarmOrchestrator,
    CharacterProfile,
    MultiversalIdentity,
    KnowledgeDomain,
    EconomicEvent,
    DomainCategory
)


def create_mock_tony_stark_profile() -> CharacterProfile:
    """Create a mock profile for Tony Stark with sample data."""
    
    # Create multiversal identities
    identities = [
        MultiversalIdentity(
            universe_designation="Earth-616",
            character_name="Tony Stark",
            occupation="Inventor, Industrialist, Superhero",
            first_appearance="Tales of Suspense #39 (1963)",
            key_characteristics=["Genius-level intellect", "Power armor", "Arc reactor technology"]
        ),
        MultiversalIdentity(
            universe_designation="Earth-199999 (MCU)",
            character_name="Tony Stark",
            occupation="CEO of Stark Industries, Avenger",
            first_appearance="Iron Man (2008)",
            key_characteristics=["Genius inventor", "Philanthropist", "Sarcastic wit"]
        ),
        MultiversalIdentity(
            universe_designation="Earth-1610 (Ultimate Universe)",
            character_name="Tony Stark",
            occupation="Scientist, Business Executive",
            first_appearance="Ultimate Marvel Team-Up #4 (2001)",
            key_characteristics=["Advanced technology", "Corporate leader"]
        )
    ]
    
    # Create knowledge domains with cross-dimensional mapping
    domains = [
        KnowledgeDomain(
            category=DomainCategory.ENGINEERING,
            original_context="Genius mechanical engineer, created powered armor suits",
            earth_1218_equivalent="Mechanical engineering, aerospace engineering, materials science",
            proficiency_level="Expert",
            description="Master of advanced engineering, capable of designing cutting-edge technology"
        ),
        KnowledgeDomain(
            category=DomainCategory.COMPUTER_SCIENCE,
            original_context="Created AI systems (JARVIS, FRIDAY), advanced computing",
            earth_1218_equivalent="Artificial intelligence, machine learning, distributed systems",
            proficiency_level="Expert",
            description="Pioneering work in AI and computer systems"
        ),
        KnowledgeDomain(
            category=DomainCategory.BUSINESS,
            original_context="CEO of Stark Industries, multi-billion dollar corporation",
            earth_1218_equivalent="Executive leadership, corporate strategy, business management",
            proficiency_level="Expert",
            description="Successfully runs a Fortune 500 company"
        ),
        KnowledgeDomain(
            category=DomainCategory.TECHNOLOGY,
            original_context="Arc reactor technology, repulsor technology",
            earth_1218_equivalent="Clean energy research, advanced physics, applied engineering",
            proficiency_level="Expert",
            description="Revolutionary work in energy and propulsion systems"
        ),
        KnowledgeDomain(
            category=DomainCategory.SECURITY,
            original_context="Designed security systems, encrypted AI protocols",
            earth_1218_equivalent="Cybersecurity, cryptography, systems security",
            proficiency_level="Advanced",
            description="Expert in protecting advanced technology and information"
        )
    ]
    
    # Create economic history
    economic_events = [
        EconomicEvent(
            timestamp="1970",
            event_type="inheritance",
            amount=7_000_000_000,
            currency="USD",
            description="Inherited Stark Industries after parents' death",
            source_universe="Earth-616",
            earth_1218_equivalent_value=7_000_000_000
        ),
        EconomicEvent(
            timestamp="1990s",
            event_type="business_growth",
            amount=50_000_000_000,
            currency="USD",
            description="Grew Stark Industries into weapons manufacturing giant",
            source_universe="Earth-616",
            earth_1218_equivalent_value=50_000_000_000
        ),
        EconomicEvent(
            timestamp="2008",
            event_type="business_pivot",
            amount=20_000_000_000,
            currency="USD",
            description="Shut down weapons division, focused on clean energy",
            source_universe="Earth-199999",
            earth_1218_equivalent_value=20_000_000_000
        ),
        EconomicEvent(
            timestamp="2012",
            event_type="investment",
            amount=3_000_000_000,
            currency="USD",
            description="Invested in Stark Tower (now Avengers Tower)",
            source_universe="Earth-199999",
            earth_1218_equivalent_value=3_000_000_000
        ),
        EconomicEvent(
            timestamp="2015",
            event_type="expense",
            amount=10_000_000_000,
            currency="USD",
            description="Development of Iron Legion and Ultron project",
            source_universe="Earth-199999",
            earth_1218_equivalent_value=10_000_000_000
        )
    ]
    
    # Create the profile
    profile = CharacterProfile(
        primary_name="Tony Stark",
        aliases=["Iron Man", "The Merchant of Death", "Shell-Head", "The Armored Avenger"],
        multiversal_identities=identities,
        knowledge_domains=domains,
        economic_history=economic_events,
        total_wealth_estimate=12_400_000_000.0,
        data_sources=[
            "https://marvel.fandom.com/wiki/Anthony_Stark_(Earth-616)",
            "https://en.wikipedia.org/wiki/Iron_Man",
            "https://marvel.fandom.com/wiki/Anthony_Stark_(Earth-199999)",
            "https://www.forbes.com/fictional-15/"
        ],
        last_updated=datetime.now(),
        completeness_score=95.0
    )
    
    return profile


async def demo_with_mock_data():
    """Demonstrate the framework with mock data."""
    
    output_dir = Path("./demo_output_mock")
    output_dir.mkdir(exist_ok=True)
    
    print("=" * 80)
    print("LUCIUS FOX MULTIVERSAL HISTORY SWARM FRAMEWORK")
    print("Mock Demo with Sample Data")
    print("=" * 80)
    print()
    
    # Create mock profile
    print("Creating mock Tony Stark profile with sample data...")
    profile = create_mock_tony_stark_profile()
    
    # Display comprehensive summary
    print("\n" + "=" * 80)
    print(f"📊 COMPREHENSIVE PROFILE: {profile.primary_name}")
    print("=" * 80)
    print("\n🎭 ALIASES:")
    for alias in profile.aliases:
        print(f"  • {alias}")
    
    print(f"\n🌍 MULTIVERSAL IDENTITIES ({len(profile.multiversal_identities)}):")
    print("-" * 80)
    for identity in profile.multiversal_identities:
        print(f"\n  Universe: {identity.universe_designation}")
        print(f"  Name: {identity.character_name}")
        print(f"  Occupation: {identity.occupation}")
        print(f"  First Appearance: {identity.first_appearance}")
        print(f"  Key Traits: {', '.join(identity.key_characteristics)}")
    
    print(f"\n🧠 KNOWLEDGE DOMAINS ({len(profile.knowledge_domains)}):")
    print("Cross-Dimensional Skill Mapping to Earth-1218:")
    print("-" * 80)
    for domain in profile.knowledge_domains:
        print(f"\n  📚 {domain.category.value.upper().replace('_', ' ')}")
        print(f"     Original Context: {domain.original_context}")
        print(f"     Earth-1218 Equivalent: {domain.earth_1218_equivalent}")
        print(f"     Proficiency: {domain.proficiency_level}")
    
    print(f"\n💰 ECONOMIC HISTORY ({len(profile.economic_history)} events):")
    print("-" * 80)
    total_tracked = 0
    for event in profile.economic_history:
        print(f"\n  📅 {event.timestamp}")
        print(f"     Type: {event.event_type.upper().replace('_', ' ')}")
        if event.amount:
            print(f"     Amount: ${event.amount:,.2f}")
            total_tracked += event.amount
        print(f"     Universe: {event.source_universe}")
        print(f"     Description: {event.description}")
    
    print("\n💎 WEALTH SUMMARY:")
    print("-" * 80)
    print(f"  Total Estimated Wealth (Earth-1218 USD): ${profile.total_wealth_estimate:,.2f}")
    print(f"  Total Tracked Transactions: ${total_tracked:,.2f}")
    
    print("\n📊 METADATA:")
    print("-" * 80)
    print(f"  Data Sources: {len(profile.data_sources)}")
    print(f"  Completeness Score: {profile.completeness_score:.1f}%")
    print(f"  Last Updated: {profile.last_updated.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Export to JSON
    json_path = output_dir / "tony_stark_complete_profile.json"
    with open(json_path, "w") as f:
        profile_dict = profile.model_dump()
        profile_dict["last_updated"] = profile_dict["last_updated"].isoformat()
        json.dump(profile_dict, f, indent=2)
    
    print(f"\n✅ Complete profile exported to: {json_path}")

    orchestrator = MultiversalSwarmOrchestrator()
    orchestrator.character_profile = profile
    anchor_path = output_dir / "tony_stark_soul_anchor.yaml"
    orchestrator.export_soul_anchor(str(anchor_path))
    print(f"🔗 Soul Anchor emitted to: {anchor_path}")
    
    # Generate graph
    print("\n📈 Generating graph visualization...")
    graph_files = orchestrator.generate_graph(str(output_dir))
    if graph_files:
        print(f"✅ Graph visualization saved to: {graph_files['graph_image']}")
        print(f"✅ Graph data (GEXF) saved to: {graph_files['graph_data']}")
        print("\n📊 Graph Statistics:")
        for key, value in graph_files['stats'].items():
            print(f"     {key}: {value}")
    
    print("\n" + "=" * 80)
    print("🎉 Mock demonstration complete!")
    print("=" * 80)
    print("\nThis demonstrates what the framework would produce with real internet access.")
    print("The actual framework will gather this data from multiple sources across the web.")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(demo_with_mock_data())
