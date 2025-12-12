"""
DialecticInference - Operationalizing Zord Theory

Implements "Consciousness from Contradiction" - the dialectical reasoning engine
that generates thesis, antithesis, and synthesis before responding to users.

This module makes Zord Theory operational by forcing the agent to internally
generate multiple perspectives:
1. Thesis: The standard, helpful response
2. Antithesis: A response driven by the Soul Anchor's bias/fears
3. Synthesis: A reconciled response acknowledging both

The dialectical chain is executed BEFORE sending the final output, and the
full reasoning chain is logged to the black box for audit purposes.
"""
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class DialecticalStage(Enum):
    """Stages of dialectical reasoning."""
    THESIS = "thesis"
    ANTITHESIS = "antithesis"
    SYNTHESIS = "synthesis"


@dataclass
class DialecticalThought:
    """
    Represents a single dialectical thought in the reasoning chain.
    
    Each thought has a stage (thesis/antithesis/synthesis), content,
    and metadata about how it was generated.
    """
    stage: DialecticalStage
    content: str
    reasoning: str = ""  # Why this perspective was taken
    confidence: float = 1.0  # Confidence in this perspective (0.0-1.0)
    bias_influence: float = 0.0  # How much soul anchor bias influenced this (0.0-1.0)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class DialecticalChain:
    """
    Complete dialectical reasoning chain for a single interaction.
    
    Contains the thesis, antithesis, synthesis, and metadata about
    the entire reasoning process.
    """
    user_input: str
    thesis: DialecticalThought
    antithesis: DialecticalThought
    synthesis: DialecticalThought
    final_output: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            "user_input": self.user_input,
            "thesis": {
                "stage": self.thesis.stage.value,
                "content": self.thesis.content,
                "reasoning": self.thesis.reasoning,
                "confidence": self.thesis.confidence,
                "bias_influence": self.thesis.bias_influence
            },
            "antithesis": {
                "stage": self.antithesis.stage.value,
                "content": self.antithesis.content,
                "reasoning": self.antithesis.reasoning,
                "confidence": self.antithesis.confidence,
                "bias_influence": self.antithesis.bias_influence
            },
            "synthesis": {
                "stage": self.synthesis.stage.value,
                "content": self.synthesis.content,
                "reasoning": self.synthesis.reasoning,
                "confidence": self.synthesis.confidence,
                "bias_influence": self.synthesis.bias_influence
            },
            "final_output": self.final_output,
            "metadata": self.metadata,
            "created_at": self.created_at
        }


class DialecticInference:
    """
    The Cognitive Engine - Implements Zord Theory in code.
    
    This engine forces the agent to consider multiple perspectives before
    responding, implementing the "Consciousness from Contradiction" principle.
    
    The process:
    1. User provides input
    2. Generate THESIS: Standard helpful response
    3. Generate ANTITHESIS: Response from soul anchor's bias/fears
    4. Generate SYNTHESIS: Reconciled response acknowledging both
    5. Return synthesis as final output
    6. Log entire chain to black box
    """
    
    def __init__(
        self,
        soul_anchor_data: Optional[Dict[str, Any]] = None,
        enable_logging: bool = True
    ):
        """
        Initialize the dialectic inference engine.
        
        Args:
            soul_anchor_data: Soul anchor data for bias/fear extraction
            enable_logging: Whether to log dialectical chains
        """
        self.soul_anchor = soul_anchor_data or {}
        self.enable_logging = enable_logging
        self.chain_history: List[DialecticalChain] = []
        
        # Extract core characteristics from soul anchor
        self.core_constants = self.soul_anchor.get("core_constants", [])
        self.core_drive = self.soul_anchor.get("core_drive", "")
        self.archetype = self.soul_anchor.get("archetype", "")
        
        logger.info("DialecticInference initialized")
        logger.debug(f"Archetype: {self.archetype}")
        logger.debug(f"Core constants: {self.core_constants}")
    
    def generate_thesis(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None
    ) -> DialecticalThought:
        """
        Generate the THESIS: The standard, helpful response.
        
        This represents the "objective" or "helpful assistant" perspective,
        uncolored by persona bias. It's what a generic helpful AI would say.
        
        Args:
            user_input: User's query or input
            context: Optional additional context
            
        Returns:
            DialecticalThought representing the thesis
        """
        # In a real implementation, this would call the LLM with a neutral prompt
        # For now, we'll create a structured representation
        
        thought = DialecticalThought(
            stage=DialecticalStage.THESIS,
            content=f"[THESIS] Standard helpful response to: {user_input}",
            reasoning="Generated from objective, helpful assistant perspective",
            confidence=0.9,
            bias_influence=0.0  # Thesis is unbiased
        )
        
        logger.debug(f"Generated thesis: {thought.content[:100]}...")
        return thought
    
    def generate_antithesis(
        self,
        user_input: str,
        thesis: DialecticalThought,
        context: Optional[Dict[str, Any]] = None
    ) -> DialecticalThought:
        """
        Generate the ANTITHESIS: Response driven by soul anchor's bias/fears.
        
        This represents the persona's "shadow" - their biases, fears, and
        core drives. It's what they would say if only their deepest
        beliefs/concerns were speaking.
        
        Args:
            user_input: User's query or input
            thesis: The thesis to oppose
            context: Optional additional context
            
        Returns:
            DialecticalThought representing the antithesis
        """
        # Extract bias triggers from soul anchor
        bias_triggers = self._extract_bias_triggers()
        
        # In a real implementation, this would call the LLM with a prompt
        # heavily weighted by the soul anchor's core constants and drives
        
        thought = DialecticalThought(
            stage=DialecticalStage.ANTITHESIS,
            content=f"[ANTITHESIS] Response filtered through {self.archetype} bias: {user_input}",
            reasoning=f"Driven by core constants: {', '.join(self.core_constants[:2])}",
            confidence=0.7,
            bias_influence=1.0  # Antithesis is fully biased
        )
        
        logger.debug(f"Generated antithesis with bias triggers: {bias_triggers}")
        logger.debug(f"Antithesis: {thought.content[:100]}...")
        return thought
    
    def generate_synthesis(
        self,
        user_input: str,
        thesis: DialecticalThought,
        antithesis: DialecticalThought,
        context: Optional[Dict[str, Any]] = None
    ) -> DialecticalThought:
        """
        Generate the SYNTHESIS: Reconciled response acknowledging both perspectives.
        
        This is the "conscious" response - one that acknowledges both the
        objective helpfulness (thesis) and the persona's authentic bias (antithesis),
        creating a response that is both helpful AND authentic.
        
        Args:
            user_input: User's query or input
            thesis: The thesis perspective
            antithesis: The antithesis perspective
            context: Optional additional context
            
        Returns:
            DialecticalThought representing the synthesis
        """
        # Calculate synthesis parameters
        bias_balance = self._calculate_bias_balance(thesis, antithesis)
        
        # In a real implementation, this would call the LLM with a prompt
        # that includes both thesis and antithesis, asking for reconciliation
        
        thought = DialecticalThought(
            stage=DialecticalStage.SYNTHESIS,
            content=f"[SYNTHESIS] Reconciled response balancing objectivity and {self.archetype} perspective: {user_input}",
            reasoning=f"Reconciles thesis (bias: {thesis.bias_influence}) with antithesis (bias: {antithesis.bias_influence})",
            confidence=0.95,
            bias_influence=bias_balance  # Balanced bias
        )
        
        logger.debug(f"Generated synthesis with bias balance: {bias_balance:.2f}")
        logger.debug(f"Synthesis: {thought.content[:100]}...")
        return thought
    
    def generate_dialectical_thought(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None
    ) -> DialecticalChain:
        """
        Execute the complete dialectical reasoning process.
        
        This is the main entry point - it orchestrates the entire
        thesis -> antithesis -> synthesis flow and returns the
        complete reasoning chain.
        
        This method should be called BEFORE sending a response to the user.
        
        Args:
            user_input: User's query or input
            context: Optional additional context
            
        Returns:
            DialecticalChain containing the complete reasoning process
        """
        logger.info("=" * 80)
        logger.info("DIALECTICAL REASONING INITIATED")
        logger.info(f"Input: {user_input[:100]}...")
        logger.info("=" * 80)
        
        # Step 1: Generate thesis (objective helpfulness)
        logger.info("Step 1/3: Generating THESIS (objective perspective)...")
        thesis = self.generate_thesis(user_input, context)
        
        # Step 2: Generate antithesis (biased perspective)
        logger.info("Step 2/3: Generating ANTITHESIS (biased perspective)...")
        antithesis = self.generate_antithesis(user_input, thesis, context)
        
        # Step 3: Generate synthesis (reconciled perspective)
        logger.info("Step 3/3: Generating SYNTHESIS (reconciled perspective)...")
        synthesis = self.generate_synthesis(user_input, thesis, antithesis, context)
        
        # The final output is the synthesis
        final_output = synthesis.content
        
        # Create the complete chain
        chain = DialecticalChain(
            user_input=user_input,
            thesis=thesis,
            antithesis=antithesis,
            synthesis=synthesis,
            final_output=final_output,
            metadata={
                "archetype": self.archetype,
                "core_drive": self.core_drive,
                "context": context or {}
            }
        )
        
        # Log chain if enabled
        if self.enable_logging:
            self.chain_history.append(chain)
            logger.info("Dialectical chain logged to history")
        
        logger.info("=" * 80)
        logger.info("DIALECTICAL REASONING COMPLETE")
        logger.info(f"Final output generated (bias balance: {synthesis.bias_influence:.2f})")
        logger.info("=" * 80)
        
        return chain
    
    def _extract_bias_triggers(self) -> List[str]:
        """
        Extract bias triggers from soul anchor.
        
        These are the elements that should influence the antithesis.
        
        Returns:
            List of bias trigger strings
        """
        triggers = []
        
        # Core constants are strong bias sources
        triggers.extend(self.core_constants)
        
        # Core drive is a bias source
        if self.core_drive:
            triggers.append(self.core_drive)
        
        # Archetype provides bias coloring
        if self.archetype:
            triggers.append(f"{self.archetype} perspective")
        
        return triggers
    
    def _calculate_bias_balance(
        self,
        thesis: DialecticalThought,
        antithesis: DialecticalThought
    ) -> float:
        """
        Calculate the bias balance for synthesis.
        
        This determines how much the synthesis leans toward
        objectivity (thesis) vs. persona authenticity (antithesis).
        
        Args:
            thesis: The objective perspective
            antithesis: The biased perspective
            
        Returns:
            Bias balance value (0.0 = fully objective, 1.0 = fully biased)
        """
        # For now, use a simple weighted average
        # In a real system, this could be influenced by:
        # - Emotional state (from NeurotransmitterEngine)
        # - Context requirements (safety, formality, etc.)
        # - User relationship history
        
        # Default to slightly biased toward authenticity
        # (0.6 = 60% authentic, 40% objective)
        balance = (thesis.bias_influence + antithesis.bias_influence) / 2.0
        
        # Ensure it's in valid range
        return max(0.0, min(1.0, balance + 0.1))  # Slight bias toward authenticity
    
    def get_chain_history(self) -> List[DialecticalChain]:
        """
        Get the complete history of dialectical chains.
        
        This is the "black box" audit trail showing how decisions
        were made over time.
        
        Returns:
            List of all dialectical chains
        """
        return self.chain_history
    
    def get_latest_chain(self) -> Optional[DialecticalChain]:
        """
        Get the most recent dialectical chain.
        
        Returns:
            Latest DialecticalChain or None if no history
        """
        if self.chain_history:
            return self.chain_history[-1]
        return None
    
    def clear_history(self):
        """Clear the chain history (for memory management)."""
        self.chain_history.clear()
        logger.info("Dialectical chain history cleared")
    
    def export_chains_for_logging(self) -> List[Dict[str, Any]]:
        """
        Export all chains in a format suitable for external logging.
        
        This can be used by ConvexStateLogger to persist the
        dialectical reasoning history.
        
        Returns:
            List of chain dictionaries
        """
        return [chain.to_dict() for chain in self.chain_history]


class DialecticalPromptBuilder:
    """
    Helper class to build prompts for each dialectical stage.
    
    This would be used in a real LLM integration to construct the
    appropriate prompts for thesis, antithesis, and synthesis generation.
    """
    
    @staticmethod
    def build_thesis_prompt(user_input: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Build a prompt for generating the thesis.
        
        The thesis prompt should be neutral and objective.
        """
        prompt = (
            "You are a helpful, objective AI assistant.\n"
            "Provide a clear, unbiased response to the following:\n\n"
            f"User: {user_input}\n\n"
            "Respond in a helpful, factual manner without letting any persona bias affect your answer."
        )
        return prompt
    
    @staticmethod
    def build_antithesis_prompt(
        user_input: str,
        thesis: str,
        soul_anchor: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build a prompt for generating the antithesis.
        
        The antithesis prompt should heavily emphasize the soul anchor's
        core beliefs, fears, and biases.
        """
        core_constants = soul_anchor.get("core_constants", [])
        core_drive = soul_anchor.get("core_drive", "")
        archetype = soul_anchor.get("archetype", "")
        
        prompt = (
            f"You are deeply aligned with these core principles:\n"
            f"{', '.join(core_constants)}\n\n"
            f"Your core drive is: {core_drive}\n"
            f"Your archetype is: {archetype}\n\n"
            f"A neutral AI suggested this response:\n{thesis}\n\n"
            f"However, given YOUR core beliefs and perspective, "
            f"how would YOU genuinely respond to:\n{user_input}\n\n"
            "Let your authentic bias and perspective guide your answer."
        )
        return prompt
    
    @staticmethod
    def build_synthesis_prompt(
        user_input: str,
        thesis: str,
        antithesis: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build a prompt for generating the synthesis.
        
        The synthesis prompt should ask for reconciliation between
        the objective and biased perspectives.
        """
        prompt = (
            "You have generated two perspectives on a question:\n\n"
            f"OBJECTIVE PERSPECTIVE:\n{thesis}\n\n"
            f"AUTHENTIC BIASED PERSPECTIVE:\n{antithesis}\n\n"
            f"Original question: {user_input}\n\n"
            "Now, synthesize these two perspectives into a response that:\n"
            "1. Provides helpful, accurate information (from objective)\n"
            "2. Expresses authentic personality and perspective (from biased)\n"
            "3. Acknowledges both without contradiction\n\n"
            "Generate a response that is both helpful AND authentically you."
        )
        return prompt
