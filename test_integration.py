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

import pytest
import textwrap

from uatu_genesis_engine.agent_zero_integration import (
    SoulAnchorLoader,
    PersonaTransformer,
    AgentInstantiator
)


@pytest.fixture
def anchor_data():
    return {
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


@pytest.fixture
def loader(anchor_data):
    l = SoulAnchorLoader()
    l.load_from_dict(anchor_data)
    return l


@pytest.fixture
def transformer(anchor_data):
    return PersonaTransformer(anchor_data)


def test_soul_anchor_loader(loader):
    """Test loading a soul anchor."""
    assert loader.get_primary_name() == "Lucius Fox"
    assert loader.get_archetype() == "technology"
    assert len(loader.get_core_constants()) == 3
    assert len(loader.get_knowledge_domains()) == 2


def test_persona_transformer(transformer):
    """Test persona transformation."""
    original_prompt = textwrap.dedent(
        """\
        agent zero autonomous json ai agent
        solve superior tasks using tools and subordinates
        follow behavioral rules instructions
        execute code actions yourself not instruct superior"""
    )
    
    transformed = transformer.transform_role_prompt(original_prompt)
    assert transformer.primary_name in transformed


def test_agent_instantiator(anchor_data, transformer, tmp_path):
    """Test agent instantiation (dry run)."""
    instantiator = AgentInstantiator(anchor_data, agent_zero_path=str(tmp_path / "az"))
    instantiator.agent_zero_path.mkdir(parents=True, exist_ok=True)
    (instantiator.agent_zero_path / "prompts").mkdir(parents=True, exist_ok=True)
    for name in ["agent.system.main.role.md", "agent.system.main.md", "agent.system.main.communication.md", "agent.system.behaviour.md"]:
        (instantiator.agent_zero_path / "prompts" / name).write_text("agent zero will act", encoding="utf-8")

    config_file = instantiator.create_persona_config()
    with open(config_file, 'r') as f:
        config_data = yaml.safe_load(f)
    assert "digital_psyche_middleware" in config_data
    assert "tts_voice_manifest" in config_data


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
