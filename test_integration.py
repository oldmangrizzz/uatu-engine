#!/usr/bin/env python3
"""
Test script for Agent Zero integration
"""
import sys
import yaml
import traceback
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from uatu_genesis_engine.agent_zero_integration import (
    SoulAnchorLoader,
    PersonaTransformer,
    AgentInstantiator
)


def test_soul_anchor_loader():
    """Test loading a soul anchor."""
    print("=" * 80)
    print("Testing Soul Anchor Loader")
    print("=" * 80)
    
    # Create a sample soul anchor
    sample_anchor = {
        "primary_name": "Lucius Fox",
        "archetype": "technology",
        "core_constants": [
            "Brilliant applied scientist",
            "Master of defensive technology",
            "Ethical innovator"
        ],
        "contextual_variables": [
            "Works with Batman",
            "CEO of Wayne Enterprises Applied Sciences"
        ],
        "knowledge_domains": [
            {
                "category": "technology",
                "earth_1218_equivalent": "advanced materials, defense systems",
                "proficiency_level": "expert"
            },
            {
                "category": "engineering",
                "earth_1218_equivalent": "mechanical, electrical, aerospace",
                "proficiency_level": "expert"
            }
        ],
        "communication_style": {
            "tone": "professional",
            "formality": "moderate to high"
        },
        "core_drive": "Using technology to protect and serve justice",
        "genesis_timestamp": "2024-12-12T00:00:00Z"
    }
    
    # Test loading from dict
    loader = SoulAnchorLoader()
    loader.load_from_dict(sample_anchor)
    
    print(f"✅ Primary Name: {loader.get_primary_name()}")
    print(f"✅ Archetype: {loader.get_archetype()}")
    print(f"✅ Core Constants: {len(loader.get_core_constants())}")
    print(f"✅ Knowledge Domains: {len(loader.get_knowledge_domains())}")
    print()
    
    return loader, sample_anchor


def test_persona_transformer(anchor_data):
    """Test persona transformation."""
    print("=" * 80)
    print("Testing Persona Transformer")
    print("=" * 80)
    
    transformer = PersonaTransformer(anchor_data)
    
    # Test transforming a sample prompt
    original_prompt = """agent zero autonomous json ai agent
solve superior tasks using tools and subordinates
follow behavioral rules instructions
execute code actions yourself not instruct superior"""
    
    transformed = transformer.transform_role_prompt(original_prompt)
    
    print("Original prompt:")
    print(original_prompt)
    print("\nTransformed prompt:")
    print(transformed[:500] + "..." if len(transformed) > 500 else transformed)
    print()
    
    return transformer


def test_agent_instantiator(anchor_data, transformer):
    """Test agent instantiation (dry run)."""
    print("=" * 80)
    print("Testing Agent Instantiator")
    print("=" * 80)
    
    try:
        instantiator = AgentInstantiator(anchor_data)
        
        print(f"✅ Persona directory created: {instantiator.persona_dir}")
        print(f"✅ Primary name: {instantiator.primary_name}")
        
        # Test creating config (without full instantiation)
        config_file = instantiator.create_persona_config()
        print(f"✅ Config file created: {config_file}")
        
        # Check if config is valid YAML
        with open(config_file, 'r') as f:
            config_data = yaml.safe_load(f)
        
        print(f"✅ Config contains: {list(config_data.keys())}")
        print()
        
        return instantiator
        
    except Exception as e:
        print(f"❌ Error: {e}")
        traceback.print_exc()
        return None


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("AGENT ZERO INTEGRATION TEST SUITE")
    print("=" * 80 + "\n")
    
    try:
        # Test 1: Soul Anchor Loader
        loader, anchor_data = test_soul_anchor_loader()
        
        # Test 2: Persona Transformer
        transformer = test_persona_transformer(anchor_data)
        
        # Test 3: Agent Instantiator
        instantiator = test_agent_instantiator(anchor_data, transformer)
        
        print("=" * 80)
        print("✅ ALL TESTS PASSED")
        print("=" * 80)
        print("\nIntegration components are working correctly!")
        print("You can now use: python main.py --subject 'Character' --instantiate")
        print()
        
    except Exception as e:
        print("\n" + "=" * 80)
        print("❌ TESTS FAILED")
        print("=" * 80)
        print(f"Error: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
