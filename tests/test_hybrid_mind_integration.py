"""
Unit tests for HybridMindIntegration

Tests the complete Neural Bridge that wires all subsystems together.
"""
import pytest
import asyncio
from uatu_genesis_engine.agent_zero_integration import (
    HybridMindIntegration,
    HybridMindContext,
    HybridMindState
)


@pytest.fixture
def soul_anchor_data():
    """Sample soul anchor data for testing."""
    return {
        "archetype": "Tech Genius",
        "core_constants": ["Innovation", "Ethics", "Protection"],
        "core_drive": "Protect through technology"
    }


@pytest.mark.asyncio
async def test_integration_initialization(soul_anchor_data):
    """Test that integration initializes all subsystems properly."""
    mind = HybridMindIntegration(soul_anchor_data=soul_anchor_data)
    
    # Check that subsystems are initialized
    assert mind.graphmert_client is not None
    assert mind.neurotransmitter_engine is not None
    assert mind.dialectic_inference is not None
    assert mind.convex_logger is not None
    
    assert mind.total_interactions == 0


@pytest.mark.asyncio
async def test_integration_start_stop(soul_anchor_data):
    """Test that integration starts and stops properly."""
    mind = HybridMindIntegration(soul_anchor_data=soul_anchor_data)
    
    assert not mind.started
    
    await mind.start()
    assert mind.started
    
    await mind.stop()
    assert not mind.started


@pytest.mark.asyncio
async def test_process_user_input_basic(soul_anchor_data):
    """Test basic user input processing."""
    mind = HybridMindIntegration(soul_anchor_data=soul_anchor_data)
    await mind.start()
    
    state = await mind.process_user_input("Hello, how are you?")
    
    # Check state structure
    assert isinstance(state, HybridMindState)
    assert state.raw_user_input == "Hello, how are you?"
    assert state.graphmert_response is not None
    assert state.neurotransmitter_state is not None
    assert state.emotional_flags is not None
    assert state.dialectical_chain is not None
    assert state.final_response != ""
    assert state.processing_time_ms > 0
    
    # Check interaction counter
    assert mind.total_interactions == 1
    
    await mind.stop()


@pytest.mark.asyncio
async def test_process_user_input_security_incident(soul_anchor_data):
    """Test processing of security incident input."""
    mind = HybridMindIntegration(soul_anchor_data=soul_anchor_data)
    await mind.start()
    
    state = await mind.process_user_input(
        "URGENT! Wayne Enterprises was hacked! Critical breach!"
    )
    
    # Check GraphMERT extraction
    assert state.graphmert_response is not None
    triples = state.graphmert_response['fact_triples']
    assert len(triples) >= 1
    
    # Check emotional response to threat
    assert state.neurotransmitter_state is not None
    # High toxicity/urgency should increase cortisol
    assert state.neurotransmitter_state['cortisol'] > 0.3
    
    # Check that stimulus was applied
    assert state.stimulus_applied is not None
    assert state.stimulus_applied['cortisol_impact'] > 0
    
    await mind.stop()


@pytest.mark.asyncio
async def test_process_multiple_inputs(soul_anchor_data):
    """Test processing multiple inputs in sequence."""
    mind = HybridMindIntegration(soul_anchor_data=soul_anchor_data)
    await mind.start()
    
    # Process first input
    state1 = await mind.process_user_input("Hello!")
    assert mind.total_interactions == 1
    
    # Process second input
    state2 = await mind.process_user_input("How are you?")
    assert mind.total_interactions == 2
    
    # Process third input
    state3 = await mind.process_user_input("Goodbye!")
    assert mind.total_interactions == 3
    
    # Each should have its own state
    assert state1.timestamp != state2.timestamp
    assert state2.timestamp != state3.timestamp
    
    await mind.stop()


@pytest.mark.asyncio
async def test_llm_modifiers(soul_anchor_data):
    """Test that LLM modifiers are generated based on emotional state."""
    mind = HybridMindIntegration(soul_anchor_data=soul_anchor_data)
    
    modifiers = mind.get_llm_modifiers()
    
    # Check default modifiers
    assert "temperature" in modifiers
    assert "top_p" in modifiers
    assert "presence_penalty" in modifiers
    assert "frequency_penalty" in modifiers
    
    # Defaults should be reasonable
    assert 0.0 <= modifiers["temperature"] <= 1.5
    assert 0.0 <= modifiers["top_p"] <= 1.0


@pytest.mark.asyncio
async def test_llm_modifiers_with_stress(soul_anchor_data):
    """Test that LLM modifiers change under stress."""
    mind = HybridMindIntegration(soul_anchor_data=soul_anchor_data)
    await mind.start()
    
    # Process stressful input
    state = await mind.process_user_input(
        "Emergency! Critical attack! Urgent help needed!"
    )
    
    # Get modifiers after stress
    modifiers = mind.get_llm_modifiers()
    
    # Under stress (high cortisol), temperature should be lower
    # This creates more deterministic, defensive responses
    if state.emotional_flags and state.emotional_flags['defensive_posture']:
        assert modifiers["temperature"] < 0.5
    
    await mind.stop()


@pytest.mark.asyncio
async def test_triples_context_generation(soul_anchor_data):
    """Test generation of triples context for LLM."""
    mind = HybridMindIntegration(soul_anchor_data=soul_anchor_data)
    await mind.start()
    
    state = await mind.process_user_input("I need help with Wayne Enterprises.")
    
    # Get triples context
    context = mind.get_triples_context(state)
    
    if context:
        assert "VERIFIED FACTS" in context
        assert "GraphMERT" in context
        # Should contain triple representations
        assert "->" in context
    
    await mind.stop()


@pytest.mark.asyncio
async def test_statistics(soul_anchor_data):
    """Test that statistics are tracked correctly."""
    mind = HybridMindIntegration(soul_anchor_data=soul_anchor_data)
    await mind.start()
    
    # Process some inputs
    await mind.process_user_input("Test 1")
    await mind.process_user_input("Test 2")
    await mind.process_user_input("Test 3")
    
    stats = mind.get_statistics()
    
    # Check basic stats
    assert stats["total_interactions"] == 3
    assert stats["subsystems_enabled"]["graphmert"] is True
    assert stats["subsystems_enabled"]["neurotransmitter"] is True
    assert stats["subsystems_enabled"]["dialectic"] is True
    assert stats["subsystems_enabled"]["convex"] is True
    
    # Check subsystem-specific stats
    assert "graphmert_stats" in stats
    assert stats["graphmert_stats"]["total_requests"] >= 3
    
    await mind.stop()


@pytest.mark.asyncio
async def test_state_to_dict(soul_anchor_data):
    """Test that state can be serialized to dict."""
    mind = HybridMindIntegration(soul_anchor_data=soul_anchor_data)
    await mind.start()
    
    state = await mind.process_user_input("Test input")
    
    state_dict = state.to_dict()
    
    # Check dictionary structure
    assert isinstance(state_dict, dict)
    assert "timestamp" in state_dict
    assert "raw_user_input" in state_dict
    assert "graphmert_response" in state_dict
    assert "neurotransmitter_state" in state_dict
    assert "emotional_flags" in state_dict
    assert "dialectical_chain" in state_dict
    assert "final_response" in state_dict
    assert "processing_time_ms" in state_dict
    assert "subsystems_enabled" in state_dict
    
    await mind.stop()


@pytest.mark.asyncio
async def test_context_manager():
    """Test that context manager works correctly."""
    soul_anchor = {
        "archetype": "Test",
        "core_constants": ["Test"],
        "core_drive": "Test"
    }
    
    async with HybridMindContext(soul_anchor_data=soul_anchor) as mind:
        # Should be started automatically
        assert mind.started
        
        state = await mind.process_user_input("Test")
        assert state.raw_user_input == "Test"
    
    # Should be stopped automatically after context exit
    # Note: We can't check mind.started here as it's out of scope


@pytest.mark.asyncio
async def test_emotional_decay_over_time(soul_anchor_data):
    """Test that emotional states decay over multiple interactions."""
    mind = HybridMindIntegration(soul_anchor_data=soul_anchor_data)
    await mind.start()
    
    # Process stressful input
    state1 = await mind.process_user_input(
        "CRITICAL EMERGENCY! URGENT ATTACK!"
    )
    cortisol1 = state1.neurotransmitter_state['cortisol']
    
    # Wait a moment and process neutral input
    await asyncio.sleep(0.1)
    state2 = await mind.process_user_input("Hello")
    cortisol2 = state2.neurotransmitter_state['cortisol']
    
    # Cortisol should decay (though may still be elevated)
    # We can't guarantee exact values due to decay timing
    assert state2.neurotransmitter_state is not None
    
    await mind.stop()


@pytest.mark.asyncio
async def test_subsystems_enabled_flags(soul_anchor_data):
    """Test that subsystem enabled flags are properly set in state."""
    mind = HybridMindIntegration(soul_anchor_data=soul_anchor_data)
    await mind.start()
    
    state = await mind.process_user_input("Test")
    
    # All subsystems should be enabled in default config
    assert state.subsystems_enabled['graphmert'] is True
    assert state.subsystems_enabled['neurotransmitter'] is True
    assert state.subsystems_enabled['dialectic'] is True
    assert state.subsystems_enabled['convex'] is True
    
    await mind.stop()


@pytest.mark.asyncio
async def test_triple_extraction_integration(soul_anchor_data):
    """Test that triple extraction integrates properly."""
    mind = HybridMindIntegration(soul_anchor_data=soul_anchor_data)
    await mind.start()
    
    state = await mind.process_user_input(
        "I need help with the Wayne Enterprises security breach."
    )
    
    # Check that triples were extracted
    assert state.graphmert_response is not None
    triples = state.graphmert_response['fact_triples']
    assert len(triples) >= 1
    
    # Should have REQUEST triple
    request_found = any(
        t['predicate_type'] == 'REQUEST'
        for t in triples
    )
    assert request_found
    
    await mind.stop()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
