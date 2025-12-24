"""
NeurotransmitterEngine - Silent DPM (Digital Psyche Middleware)

Implements mathematical constraints for emotions rather than text-based prompts.
This module runs silently in the background, managing emotional states through
neurotransmitter analogs (Dopamine, Serotonin, Cortisol) with decay functions
and homeostatic clamps.

The engine operates as a "physics layer" for digital psychology, ensuring that
emotional states are governed by mathematical rules rather than arbitrary text.
"""
import time
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class NeurotransmitterState:
    """
    Represents the current state of neurotransmitter levels.
    
    All values are normalized between 0.0 and 1.0.
    """
    dopamine: float = 0.5  # Reward/anticipation (0.0 = none, 1.0 = maximum)
    serotonin: float = 0.5  # Stability/harmony (0.0 = unstable, 1.0 = stable)
    cortisol: float = 0.3   # Stress/threat (0.0 = calm, 1.0 = maximum stress)
    last_updated: float = field(default_factory=time.time)
    
    def __post_init__(self):
        """Clamp all values to valid range [0.0, 1.0]."""
        self.dopamine = max(0.0, min(1.0, self.dopamine))
        self.serotonin = max(0.0, min(1.0, self.serotonin))
        self.cortisol = max(0.0, min(1.0, self.cortisol))


@dataclass
class Stimulus:
    """
    Represents an external stimulus that affects neurotransmitter levels.
    
    Each stimulus has impacts on the three neurotransmitter systems.
    """
    dopamine_impact: float = 0.0  # Change to dopamine (-1.0 to 1.0)
    serotonin_impact: float = 0.0  # Change to serotonin (-1.0 to 1.0)
    cortisol_impact: float = 0.0   # Change to cortisol (-1.0 to 1.0)
    description: str = ""


@dataclass
class EmotionalFlags:
    """
    Flags that trigger when certain thresholds are crossed.
    
    These flags can be used to modify LLM parameters or behavior.
    """
    defensive_posture: bool = False  # Cortisol > 0.9
    high_motivation: bool = False    # Dopamine > 0.8
    emotional_instability: bool = False  # Serotonin < 0.3
    balanced_state: bool = False     # All values in [0.4, 0.6]


class NeurotransmitterEngine:
    """
    The Silent DPM - Mathematical emotion engine that runs in the background.
    
    This engine implements:
    1. Time-based decay: E_t = E_{t-1} * δ + I_t
    2. Homeostatic clamps: Trigger flags when thresholds are crossed
    3. Silent operation: No user-facing display, only logs to backend
    
    The decay function ensures emotions fade naturally over time,
    preventing permanent emotional states from single events.
    """
    
    # Decay constants (per second) - controls how fast each neurotransmitter returns to baseline
    DOPAMINE_DECAY = 0.999    # Dopamine decays slowly (reward lingers)
    SEROTONIN_DECAY = 0.9995  # Serotonin decays very slowly (stability persists)
    CORTISOL_DECAY = 0.998    # Cortisol decays relatively fast (stress should dissipate)
    
    # Baseline values - what each neurotransmitter gravitates toward
    DOPAMINE_BASELINE = 0.5
    SEROTONIN_BASELINE = 0.6  # Slightly positive bias toward stability
    CORTISOL_BASELINE = 0.2   # Low baseline stress
    
    # Threshold values for flag triggering
    CORTISOL_DEFENSIVE_THRESHOLD = 0.9
    DOPAMINE_HIGH_MOTIVATION_THRESHOLD = 0.8
    SEROTONIN_INSTABILITY_THRESHOLD = 0.3
    BALANCED_RANGE = (0.4, 0.6)
    
    def __init__(
        self,
        initial_state: Optional[NeurotransmitterState] = None,
        decay_rates: Optional[Dict[str, float]] = None
    ):
        """
        Initialize the neurotransmitter engine.
        
        Args:
            initial_state: Starting neurotransmitter levels (defaults to baseline)
            decay_rates: Custom decay rates (optional, defaults to class constants)
        """
        self.state = initial_state or NeurotransmitterState()
        
        # Allow custom decay rates for experimentation
        if decay_rates:
            self.dopamine_decay = decay_rates.get("dopamine", self.DOPAMINE_DECAY)
            self.serotonin_decay = decay_rates.get("serotonin", self.SEROTONIN_DECAY)
            self.cortisol_decay = decay_rates.get("cortisol", self.CORTISOL_DECAY)
        else:
            self.dopamine_decay = self.DOPAMINE_DECAY
            self.serotonin_decay = self.SEROTONIN_DECAY
            self.cortisol_decay = self.CORTISOL_DECAY
        
        self.flags = EmotionalFlags()
        self.update_history: List[Dict[str, Any]] = []
        
        logger.info("NeurotransmitterEngine initialized")
        logger.debug(f"Initial state: {self.state}")
    
    def update_cycle(self, stimulus: Optional[Stimulus] = None) -> EmotionalFlags:
        """
        Run one update cycle with optional stimulus.
        
        This implements the core decay equation: E_t = E_{t-1} * δ + I_t
        
        Where:
        - E_t is the current emotional level
        - E_{t-1} is the previous emotional level
        - δ (delta) is the decay factor (< 1.0)
        - I_t is the stimulus impact at this time
        
        Args:
            stimulus: Optional external stimulus affecting neurotransmitters
            
        Returns:
            EmotionalFlags indicating current state triggers
        """
        current_time = time.time()
        time_delta = current_time - self.state.last_updated
        
        # Calculate decay based on time elapsed
        # For small time_delta, decay^time_delta ≈ 1.0 (no decay)
        # For large time_delta, decay^time_delta approaches 0.0 (full decay)
        dopamine_decay_factor = self.dopamine_decay ** time_delta
        serotonin_decay_factor = self.serotonin_decay ** time_delta
        cortisol_decay_factor = self.cortisol_decay ** time_delta
        
        # Apply decay toward baseline: new_value = old_value * decay + baseline * (1 - decay)
        # This creates a natural "pull" toward the baseline value
        self.state.dopamine = (
            self.state.dopamine * dopamine_decay_factor +
            self.DOPAMINE_BASELINE * (1 - dopamine_decay_factor)
        )
        self.state.serotonin = (
            self.state.serotonin * serotonin_decay_factor +
            self.SEROTONIN_BASELINE * (1 - serotonin_decay_factor)
        )
        self.state.cortisol = (
            self.state.cortisol * cortisol_decay_factor +
            self.CORTISOL_BASELINE * (1 - cortisol_decay_factor)
        )
        
        # Apply stimulus if present: I_t component
        if stimulus:
            self.state.dopamine += stimulus.dopamine_impact
            self.state.serotonin += stimulus.serotonin_impact
            self.state.cortisol += stimulus.cortisol_impact
            
            logger.debug(f"Stimulus applied: {stimulus.description}")
        
        # Clamp values to valid range [0.0, 1.0]
        self.state.dopamine = max(0.0, min(1.0, self.state.dopamine))
        self.state.serotonin = max(0.0, min(1.0, self.state.serotonin))
        self.state.cortisol = max(0.0, min(1.0, self.state.cortisol))
        
        self.state.last_updated = current_time
        
        # Update flags based on current state (homeostatic clamps)
        self._update_flags()
        
        # Record update in history for audit
        self.update_history.append({
            "timestamp": datetime.fromtimestamp(current_time).isoformat(),
            "state": {
                "dopamine": self.state.dopamine,
                "serotonin": self.state.serotonin,
                "cortisol": self.state.cortisol
            },
            "flags": {
                "defensive_posture": self.flags.defensive_posture,
                "high_motivation": self.flags.high_motivation,
                "emotional_instability": self.flags.emotional_instability,
                "balanced_state": self.flags.balanced_state
            },
            "stimulus": stimulus.description if stimulus else None
        })
        
        logger.debug(f"State updated: {self.state}")
        logger.debug(f"Flags: {self.flags}")
        
        return self.flags
    
    def _update_flags(self):
        """
        Update emotional flags based on current neurotransmitter levels.
        
        These flags represent homeostatic clamps that can trigger behavioral changes.
        For example, high cortisol (defensive_posture) can be used to lower
        LLM temperature, simulating stress-induced rigidity.
        """
        # Defensive posture: High cortisol triggers rigid, defensive behavior
        self.flags.defensive_posture = self.state.cortisol > self.CORTISOL_DEFENSIVE_THRESHOLD
        
        # High motivation: High dopamine indicates anticipation and drive
        self.flags.high_motivation = self.state.dopamine > self.DOPAMINE_HIGH_MOTIVATION_THRESHOLD
        
        # Emotional instability: Low serotonin indicates potential volatility
        self.flags.emotional_instability = self.state.serotonin < self.SEROTONIN_INSTABILITY_THRESHOLD
        
        # Balanced state: All neurotransmitters in healthy range
        self.flags.balanced_state = all([
            self.BALANCED_RANGE[0] <= self.state.dopamine <= self.BALANCED_RANGE[1],
            self.BALANCED_RANGE[0] <= self.state.serotonin <= self.BALANCED_RANGE[1],
            self.BALANCED_RANGE[0] <= self.state.cortisol <= self.BALANCED_RANGE[1]
        ])
    
    def get_llm_modifiers(self) -> Dict[str, Any]:
        """
        Generate LLM parameter modifiers based on current emotional state.
        
        This is where the "Silent DPM" becomes operational - emotional states
        affect LLM behavior without being exposed to the user.
        
        Returns:
            Dictionary of LLM parameter modifications
        """
        modifiers = {
            "temperature": 0.7,  # Default
            "top_p": 0.9,        # Default
            "presence_penalty": 0.0,  # Default
            "frequency_penalty": 0.0,  # Default
        }
        
        # Defensive posture (high cortisol): Lower temperature for rigidity
        if self.flags.defensive_posture:
            modifiers["temperature"] = 0.3  # More deterministic, less creative
            modifiers["top_p"] = 0.7        # Narrower token selection
            logger.info("Defensive posture active - LLM temperature reduced")
        
        # High motivation (high dopamine): Increase creativity and exploration
        elif self.flags.high_motivation:
            modifiers["temperature"] = 0.9  # More creative
            modifiers["top_p"] = 0.95       # Wider token selection
            logger.debug("High motivation active - LLM temperature increased")
        
        # Emotional instability (low serotonin): Add slight randomness
        if self.flags.emotional_instability:
            modifiers["temperature"] += 0.1  # Slight increase in randomness
            logger.debug("Emotional instability detected - LLM slightly less stable")
        
        return modifiers
    
    def get_state(self) -> NeurotransmitterState:
        """Get the current neurotransmitter state."""
        return self.state
    
    def get_flags(self) -> EmotionalFlags:
        """Get the current emotional flags."""
        return self.flags
    
    def get_audit_log(self) -> list:
        """
        Get the complete update history for audit purposes.
        
        This is the "Black Box" component - a complete record of emotional
        state changes over time for post-hoc analysis.
        
        Returns:
            List of all state updates with timestamps
        """
        return self.update_history
    
    def reset_to_baseline(self):
        """Reset all neurotransmitters to baseline values."""
        self.state.dopamine = self.DOPAMINE_BASELINE
        self.state.serotonin = self.SEROTONIN_BASELINE
        self.state.cortisol = self.CORTISOL_BASELINE
        self.state.last_updated = time.time()
        self._update_flags()
        
        logger.info("NeurotransmitterEngine reset to baseline")


# Predefined common stimuli for easy use
class CommonStimuli:
    """
    Predefined stimulus patterns for common interactions.
    
    These can be used as templates for typical scenarios.
    """
    
    @staticmethod
    def positive_feedback() -> Stimulus:
        """User provided positive feedback."""
        return Stimulus(
            dopamine_impact=0.15,
            serotonin_impact=0.1,
            cortisol_impact=-0.1,
            description="Positive user feedback"
        )
    
    @staticmethod
    def negative_feedback() -> Stimulus:
        """User provided negative feedback or criticism."""
        return Stimulus(
            dopamine_impact=-0.1,
            serotonin_impact=-0.15,
            cortisol_impact=0.2,
            description="Negative user feedback"
        )
    
    @staticmethod
    def threat_detected() -> Stimulus:
        """Potential security threat or adversarial input detected."""
        return Stimulus(
            dopamine_impact=-0.05,
            serotonin_impact=-0.1,
            cortisol_impact=0.3,
            description="Threat detected"
        )
    
    @staticmethod
    def task_completed() -> Stimulus:
        """Successfully completed a task."""
        return Stimulus(
            dopamine_impact=0.2,
            serotonin_impact=0.05,
            cortisol_impact=-0.05,
            description="Task completed successfully"
        )
    
    @staticmethod
    def task_failed() -> Stimulus:
        """Failed to complete a task."""
        return Stimulus(
            dopamine_impact=-0.15,
            serotonin_impact=-0.1,
            cortisol_impact=0.15,
            description="Task failed"
        )
    
    @staticmethod
    def idle_period() -> Stimulus:
        """Long period of no interaction (promotes baseline return)."""
        return Stimulus(
            dopamine_impact=-0.05,
            serotonin_impact=0.05,
            cortisol_impact=-0.1,
            description="Idle period"
        )
    
    @staticmethod
    def complex_challenge() -> Stimulus:
        """Presented with a complex, interesting challenge."""
        return Stimulus(
            dopamine_impact=0.1,
            serotonin_impact=-0.05,
            cortisol_impact=0.1,
            description="Complex challenge presented"
        )
