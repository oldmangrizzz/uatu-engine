"""
Unit tests for NeurotransmitterEngine

Tests the mathematical emotion modeling system including decay functions,
homeostatic clamps, and LLM modifier generation.
"""
import time
import pytest
from uatu_genesis_engine.agent_zero_integration.neurotransmitter_engine import (
    NeurotransmitterEngine,
    NeurotransmitterState,
    Stimulus,
    CommonStimuli
)


class TestNeurotransmitterState:
    """Test the NeurotransmitterState dataclass."""
    
    def test_initialization_default(self):
        """Test default initialization."""
        state = NeurotransmitterState()
        assert state.dopamine == 0.5
        assert state.serotonin == 0.5
        assert state.cortisol == 0.3
        assert state.last_updated > 0
    
    def test_initialization_custom(self):
        """Test custom initialization."""
        state = NeurotransmitterState(
            dopamine=0.7,
            serotonin=0.8,
            cortisol=0.4
        )
        assert state.dopamine == 0.7
        assert state.serotonin == 0.8
        assert state.cortisol == 0.4
    
    def test_clamping_high_values(self):
        """Test that values above 1.0 are clamped."""
        state = NeurotransmitterState(
            dopamine=1.5,
            serotonin=2.0,
            cortisol=1.2
        )
        assert state.dopamine == 1.0
        assert state.serotonin == 1.0
        assert state.cortisol == 1.0
    
    def test_clamping_low_values(self):
        """Test that values below 0.0 are clamped."""
        state = NeurotransmitterState(
            dopamine=-0.5,
            serotonin=-1.0,
            cortisol=-0.2
        )
        assert state.dopamine == 0.0
        assert state.serotonin == 0.0
        assert state.cortisol == 0.0


class TestStimulus:
    """Test the Stimulus dataclass."""
    
    def test_initialization(self):
        """Test stimulus initialization."""
        stim = Stimulus(
            dopamine_impact=0.1,
            serotonin_impact=-0.2,
            cortisol_impact=0.3,
            description="Test stimulus"
        )
        assert stim.dopamine_impact == 0.1
        assert stim.serotonin_impact == -0.2
        assert stim.cortisol_impact == 0.3
        assert stim.description == "Test stimulus"


class TestNeurotransmitterEngine:
    """Test the NeurotransmitterEngine class."""
    
    def test_initialization_default(self):
        """Test default engine initialization."""
        engine = NeurotransmitterEngine()
        state = engine.get_state()
        
        assert state.dopamine == 0.5
        assert state.serotonin == 0.5
        assert state.cortisol == 0.3
    
    def test_initialization_custom_state(self):
        """Test engine initialization with custom state."""
        initial_state = NeurotransmitterState(
            dopamine=0.7,
            serotonin=0.6,
            cortisol=0.5
        )
        engine = NeurotransmitterEngine(initial_state=initial_state)
        state = engine.get_state()
        
        assert state.dopamine == 0.7
        assert state.serotonin == 0.6
        assert state.cortisol == 0.5
    
    def test_update_cycle_no_stimulus(self):
        """Test update cycle with no stimulus (pure decay)."""
        engine = NeurotransmitterEngine()
        
        # Set high initial values
        engine.state.dopamine = 1.0
        engine.state.serotonin = 1.0
        engine.state.cortisol = 1.0
        engine.state.last_updated = time.time()
        
        # Wait a moment and update
        time.sleep(0.1)
        flags = engine.update_cycle()
        
        # Values should decay toward baseline
        assert engine.state.dopamine < 1.0
        assert engine.state.serotonin < 1.0
        assert engine.state.cortisol < 1.0
    
    def test_update_cycle_with_stimulus(self):
        """Test update cycle with a stimulus."""
        engine = NeurotransmitterEngine()
        initial_dopamine = engine.state.dopamine
        
        stimulus = Stimulus(
            dopamine_impact=0.2,
            serotonin_impact=0.1,
            cortisol_impact=-0.1,
            description="Test stimulus"
        )
        
        engine.update_cycle(stimulus)
        
        # Dopamine should increase (even after decay)
        # Since we apply stimulus after decay, it should be higher
        assert engine.state.dopamine > initial_dopamine
    
    def test_decay_toward_baseline(self):
        """Test that values decay toward baseline over time."""
        engine = NeurotransmitterEngine()
        
        # Set values away from baseline
        engine.state.dopamine = 1.0
        engine.state.serotonin = 0.1
        engine.state.cortisol = 0.9
        engine.state.last_updated = time.time() - 10  # Simulate 10 seconds ago
        
        engine.update_cycle()
        
        # Values should move toward baseline
        assert engine.state.dopamine < 1.0  # Moving down from 1.0
        assert engine.state.serotonin > 0.1  # Moving up from 0.1
        assert engine.state.cortisol < 0.9   # Moving down from 0.9
    
    def test_clamping_after_stimulus(self):
        """Test that values are clamped after applying stimulus."""
        engine = NeurotransmitterEngine()
        
        # Set state near maximum
        engine.state.dopamine = 0.95
        engine.state.serotonin = 0.95
        engine.state.cortisol = 0.95
        
        # Apply large positive stimulus
        large_stimulus = Stimulus(
            dopamine_impact=0.5,
            serotonin_impact=0.5,
            cortisol_impact=0.5,
            description="Large stimulus"
        )
        
        engine.update_cycle(large_stimulus)
        
        # Values should be clamped at 1.0
        assert engine.state.dopamine <= 1.0
        assert engine.state.serotonin <= 1.0
        assert engine.state.cortisol <= 1.0
    
    def test_defensive_posture_flag(self):
        """Test defensive posture flag triggers at cortisol > 0.9."""
        engine = NeurotransmitterEngine()
        
        # Set cortisol below threshold
        engine.state.cortisol = 0.85
        engine.update_cycle()
        assert not engine.flags.defensive_posture
        
        # Set cortisol above threshold
        engine.state.cortisol = 0.95
        engine.update_cycle()
        assert engine.flags.defensive_posture
    
    def test_high_motivation_flag(self):
        """Test high motivation flag triggers at dopamine > 0.8."""
        engine = NeurotransmitterEngine()
        
        # Set dopamine below threshold
        engine.state.dopamine = 0.75
        engine.update_cycle()
        assert not engine.flags.high_motivation
        
        # Set dopamine above threshold
        engine.state.dopamine = 0.85
        engine.update_cycle()
        assert engine.flags.high_motivation
    
    def test_emotional_instability_flag(self):
        """Test emotional instability flag triggers at serotonin < 0.3."""
        engine = NeurotransmitterEngine()
        
        # Set serotonin above threshold
        engine.state.serotonin = 0.35
        engine.update_cycle()
        assert not engine.flags.emotional_instability
        
        # Set serotonin below threshold
        engine.state.serotonin = 0.25
        engine.update_cycle()
        assert engine.flags.emotional_instability
    
    def test_balanced_state_flag(self):
        """Test balanced state flag when all values in [0.4, 0.6]."""
        engine = NeurotransmitterEngine()
        
        # Set all values in balanced range
        engine.state.dopamine = 0.5
        engine.state.serotonin = 0.5
        engine.state.cortisol = 0.5
        engine.update_cycle()
        assert engine.flags.balanced_state
        
        # Set one value outside range
        engine.state.cortisol = 0.7
        engine.update_cycle()
        assert not engine.flags.balanced_state
    
    def test_llm_modifiers_defensive_posture(self):
        """Test LLM modifiers during defensive posture (high cortisol)."""
        engine = NeurotransmitterEngine()
        
        # Trigger defensive posture
        engine.state.cortisol = 0.95
        engine.update_cycle()
        
        modifiers = engine.get_llm_modifiers()
        
        # Temperature should be lowered for rigidity
        assert modifiers["temperature"] == 0.3
        assert modifiers["top_p"] == 0.7
    
    def test_llm_modifiers_high_motivation(self):
        """Test LLM modifiers during high motivation (high dopamine)."""
        engine = NeurotransmitterEngine()
        
        # Trigger high motivation
        engine.state.dopamine = 0.85
        engine.state.cortisol = 0.2  # Keep cortisol low so defensive posture doesn't trigger
        engine.update_cycle()
        
        modifiers = engine.get_llm_modifiers()
        
        # Temperature should be increased for creativity
        assert modifiers["temperature"] == 0.9
        assert modifiers["top_p"] == 0.95
    
    def test_llm_modifiers_instability(self):
        """Test LLM modifiers during emotional instability (low serotonin)."""
        engine = NeurotransmitterEngine()
        
        # Trigger emotional instability
        engine.state.serotonin = 0.25
        engine.state.dopamine = 0.5  # Keep dopamine neutral
        engine.state.cortisol = 0.3  # Keep cortisol low
        engine.update_cycle()
        
        modifiers = engine.get_llm_modifiers()
        
        # Temperature should be slightly increased
        assert modifiers["temperature"] > 0.7
    
    def test_audit_log_recording(self):
        """Test that updates are recorded in audit log."""
        engine = NeurotransmitterEngine()
        
        # Perform a few updates
        engine.update_cycle()
        time.sleep(0.05)
        engine.update_cycle(CommonStimuli.positive_feedback())
        time.sleep(0.05)
        engine.update_cycle(CommonStimuli.threat_detected())
        
        audit_log = engine.get_audit_log()
        
        # Should have 3 entries
        assert len(audit_log) == 3
        
        # Each entry should have required fields
        for entry in audit_log:
            assert "timestamp" in entry
            assert "state" in entry
            assert "flags" in entry
            assert "stimulus" in entry
            
            # State should have neurotransmitter values
            assert "dopamine" in entry["state"]
            assert "serotonin" in entry["state"]
            assert "cortisol" in entry["state"]
    
    def test_reset_to_baseline(self):
        """Test resetting engine to baseline."""
        engine = NeurotransmitterEngine()
        
        # Set extreme values
        engine.state.dopamine = 1.0
        engine.state.serotonin = 0.0
        engine.state.cortisol = 1.0
        
        # Reset
        engine.reset_to_baseline()
        
        # Should be at baseline
        assert engine.state.dopamine == engine.DOPAMINE_BASELINE
        assert engine.state.serotonin == engine.SEROTONIN_BASELINE
        assert engine.state.cortisol == engine.CORTISOL_BASELINE


class TestCommonStimuli:
    """Test predefined common stimuli."""
    
    def test_positive_feedback(self):
        """Test positive feedback stimulus."""
        stim = CommonStimuli.positive_feedback()
        assert stim.dopamine_impact > 0
        assert stim.serotonin_impact > 0
        assert stim.cortisol_impact < 0
    
    def test_negative_feedback(self):
        """Test negative feedback stimulus."""
        stim = CommonStimuli.negative_feedback()
        assert stim.dopamine_impact < 0
        assert stim.serotonin_impact < 0
        assert stim.cortisol_impact > 0
    
    def test_threat_detected(self):
        """Test threat detection stimulus."""
        stim = CommonStimuli.threat_detected()
        assert stim.cortisol_impact > 0
        assert "threat" in stim.description.lower()
    
    def test_task_completed(self):
        """Test task completion stimulus."""
        stim = CommonStimuli.task_completed()
        assert stim.dopamine_impact > 0
        assert stim.cortisol_impact < 0
    
    def test_task_failed(self):
        """Test task failure stimulus."""
        stim = CommonStimuli.task_failed()
        assert stim.dopamine_impact < 0
        assert stim.cortisol_impact > 0


class TestIntegrationScenarios:
    """Integration tests for realistic scenarios."""
    
    def test_stress_buildup_and_decay(self):
        """Test stress building up and then decaying over time."""
        engine = NeurotransmitterEngine()
        
        # Apply multiple stress stimuli
        for _ in range(3):
            engine.update_cycle(CommonStimuli.threat_detected())
            time.sleep(0.01)
        
        # Cortisol should be elevated
        high_cortisol = engine.state.cortisol
        assert high_cortisol > 0.5
        
        # Let it decay over time
        for _ in range(5):
            time.sleep(0.1)
            engine.update_cycle()
        
        # Cortisol should decay toward baseline
        assert engine.state.cortisol < high_cortisol
    
    def test_reward_response_cycle(self):
        """Test positive feedback loop."""
        engine = NeurotransmitterEngine()
        initial_dopamine = engine.state.dopamine
        
        # Apply multiple positive feedbacks
        for _ in range(3):
            engine.update_cycle(CommonStimuli.task_completed())
            time.sleep(0.01)
        
        # Dopamine should be elevated
        assert engine.state.dopamine > initial_dopamine
        
        # Should trigger high motivation
        if engine.state.dopamine > 0.8:
            assert engine.flags.high_motivation
    
    def test_defensive_posture_affects_llm(self):
        """Test that high stress triggers defensive posture and affects LLM."""
        engine = NeurotransmitterEngine()
        
        # Build up stress
        for _ in range(5):
            engine.update_cycle(CommonStimuli.threat_detected())
        
        # Should trigger defensive posture
        assert engine.flags.defensive_posture
        
        # LLM temperature should be reduced
        modifiers = engine.get_llm_modifiers()
        assert modifiers["temperature"] < 0.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
