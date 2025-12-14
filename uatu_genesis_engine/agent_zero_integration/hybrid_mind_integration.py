"""
Agent Loop Integration - The Neural Bridge

This module provides the integration layer that wires all subsystems
(GraphMERT, NeurotransmitterEngine, DialecticInference, ConvexStateLogger)
into the main Agent Zero runtime loop.

The integration follows the "Grand Unification" flow:
1. Input: Receive User Text
2. Filter: Pass to GraphMERT -> Get Triples
3. Feel: Update NeurotransmitterEngine based on input toxicity/urgency
4. Think: Run DialecticInference (Thesis -> Antithesis -> Synthesis)
5. Act: Generate Output using the Synthesis and Triples
6. Record: Push all of the above to ConvexStateLogger

This is the final piece that brings the "Hybrid Mind" online.
"""
import asyncio
import logging
import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime

from ..utils.graphmert_client import GraphMERTClient, GraphMERTResponse
from ..utils.hybrid_config import get_config
from .neurotransmitter_engine import (
    NeurotransmitterEngine,
    Stimulus,
    NeurotransmitterState,
    EmotionalFlags
)
from .dialectic_inference import DialecticInference, DialecticalChain
from .convex_state_logger import ConvexStateLogger

logger = logging.getLogger(__name__)


@dataclass
class HybridMindState:
    """
    Complete state snapshot for a single interaction.
    
    This captures the state of all subsystems at a point in time,
    which is logged to Convex for the "Black Box" audit trail.
    """
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Input
    raw_user_input: str = ""
    graphmert_response: Optional[Dict[str, Any]] = None
    
    # Emotional state
    neurotransmitter_state: Optional[Dict[str, Any]] = None
    emotional_flags: Optional[Dict[str, Any]] = None
    stimulus_applied: Optional[Dict[str, Any]] = None
    
    # Reasoning
    dialectical_chain: Optional[Dict[str, Any]] = None
    
    # Output
    final_response: str = ""
    
    # Metadata
    processing_time_ms: float = 0.0
    subsystems_enabled: Dict[str, bool] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            "timestamp": self.timestamp,
            "raw_user_input": self.raw_user_input,
            "graphmert_response": self.graphmert_response,
            "neurotransmitter_state": self.neurotransmitter_state,
            "emotional_flags": self.emotional_flags,
            "stimulus_applied": self.stimulus_applied,
            "dialectical_chain": self.dialectical_chain,
            "final_response": self.final_response,
            "processing_time_ms": self.processing_time_ms,
            "subsystems_enabled": self.subsystems_enabled
        }


class HybridMindIntegration:
    """
    The Neural Bridge - Integrates all subsystems into Agent Zero.
    
    This class manages the complete flow from user input to agent response,
    orchestrating GraphMERT, NeurotransmitterEngine, DialecticInference,
    and ConvexStateLogger.
    
    It acts as middleware that sits between the user and the LLM, ensuring
    that all input is processed through the "Hybrid Mind" architecture.
    """
    
    def __init__(
        self,
        config_path: Optional[str] = None,
        soul_anchor_data: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the Hybrid Mind Integration.
        
        Args:
            config_path: Path to hybrid_settings.yaml
            soul_anchor_data: Soul anchor data for dialectic inference
        """
        # Load configuration
        self.config = get_config(config_path)
        
        # Get subsystem configs
        self.agent_loop_config = self.config.get_agent_loop_config()
        self.graphmert_config = self.config.get_graphmert_config()
        self.neurotransmitter_config = self.config.get_neurotransmitter_config()
        self.dialectic_config = self.config.get_dialectic_config()
        self.convex_config = self.config.get_convex_config()
        
        # Initialize subsystems
        self.graphmert_client = None
        self.neurotransmitter_engine = None
        self.dialectic_inference = None
        self.convex_logger = None
        
        # Initialize enabled subsystems
        if self.agent_loop_config['enable_graphmert_filter']:
            self.graphmert_client = GraphMERTClient(
                endpoint_url=self.graphmert_config['url'],
                api_key=self.graphmert_config['api_key'],
                enable_mock=self.graphmert_config['enable_mock'],
                confidence_threshold=self.graphmert_config['confidence_threshold']
            )
            logger.info("GraphMERT client initialized")
        
        if self.agent_loop_config['enable_neurotransmitter_updates']:
            # Get initial state from config
            initial_state = NeurotransmitterState(
                dopamine=self.neurotransmitter_config['initial_state'].get('dopamine', 0.5),
                serotonin=self.neurotransmitter_config['initial_state'].get('serotonin', 0.5),
                cortisol=self.neurotransmitter_config['initial_state'].get('cortisol', 0.3)
            )
            
            # Get decay rates from config
            decay_rates = self.neurotransmitter_config.get('decay_rates', {})
            
            self.neurotransmitter_engine = NeurotransmitterEngine(
                initial_state=initial_state,
                decay_rates=decay_rates if decay_rates else None
            )
            logger.info("NeurotransmitterEngine initialized")
        
        if self.agent_loop_config['enable_dialectic_reasoning']:
            self.dialectic_inference = DialecticInference(
                soul_anchor_data=soul_anchor_data,
                enable_logging=self.dialectic_config['enable_logging']
            )
            logger.info("DialecticInference initialized")
        
        if self.agent_loop_config['enable_convex_logging']:
            self.convex_logger = ConvexStateLogger(
                convex_url=self.convex_config['url'],
                api_key=self.convex_config['api_key'],
                batch_size=self.convex_config['batch_size'],
                flush_interval=self.convex_config['flush_interval'],
                enable_local_backup=self.convex_config['enable_local_backup'],
                local_backup_path=self.convex_config['local_backup_path']
            )
            logger.info("ConvexStateLogger initialized")
        
        # Statistics
        self.total_interactions = 0
        self.started = False
        
        logger.info("=" * 80)
        logger.info("HYBRID MIND INTEGRATION INITIALIZED")
        logger.info(f"GraphMERT: {'ENABLED' if self.graphmert_client else 'DISABLED'}")
        logger.info(f"Neurotransmitter: {'ENABLED' if self.neurotransmitter_engine else 'DISABLED'}")
        logger.info(f"Dialectic: {'ENABLED' if self.dialectic_inference else 'DISABLED'}")
        logger.info(f"Convex: {'ENABLED' if self.convex_logger else 'DISABLED'}")
        logger.info("=" * 80)
    
    async def start(self):
        """Start asynchronous subsystems (ConvexStateLogger)."""
        if self.convex_logger and not self.started:
            await self.convex_logger.start()
            self.started = True
            logger.info("Asynchronous subsystems started")
    
    async def stop(self):
        """Stop asynchronous subsystems."""
        if self.convex_logger and self.started:
            await self.convex_logger.stop()
            self.started = False
            logger.info("Asynchronous subsystems stopped")
    
    async def process_user_input(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None
    ) -> HybridMindState:
        """
        Process user input through the complete Hybrid Mind pipeline.
        
        This is the main entry point that orchestrates all subsystems.
        
        Flow:
        1. Input: Receive User Text
        2. Filter: Pass to GraphMERT -> Get Triples
        3. Feel: Update NeurotransmitterEngine
        4. Think: Run DialecticInference
        5. Act: Generate Output (synthesis)
        6. Record: Log to Convex
        
        Args:
            user_input: Raw text from user
            context: Optional context (conversation history, etc.)
            
        Returns:
            HybridMindState with complete state snapshot
        """
        start_time = time.time()
        
        self.total_interactions += 1
        
        logger.info("=" * 80)
        logger.info(f"PROCESSING INTERACTION #{self.total_interactions}")
        logger.info(f"Input: {user_input[:100]}...")
        logger.info("=" * 80)
        
        state = HybridMindState(
            raw_user_input=user_input,
            subsystems_enabled={
                'graphmert': self.graphmert_client is not None,
                'neurotransmitter': self.neurotransmitter_engine is not None,
                'dialectic': self.dialectic_inference is not None,
                'convex': self.convex_logger is not None
            }
        )
        
        # Step 1: Filter through GraphMERT
        graphmert_response = None
        if self.graphmert_client:
            logger.info("Step 1/5: GraphMERT Truth Filter")
            graphmert_response = await self.graphmert_client.extract_triples(user_input, context)
            state.graphmert_response = graphmert_response.to_dict()
            logger.info(f"  ✓ Extracted {len(graphmert_response.fact_triples)} triples")
        else:
            logger.info("Step 1/5: GraphMERT SKIPPED (disabled)")
        
        # Step 2: Feel - Update Neurotransmitter Engine
        stimulus = None
        if self.neurotransmitter_engine and graphmert_response:
            logger.info("Step 2/5: Neurotransmitter Update")
            
            # Create stimulus based on GraphMERT analysis
            stimulus = Stimulus(
                dopamine_impact=0.05 if graphmert_response.urgency_score > 0.7 else 0.0,
                serotonin_impact=-0.05 if graphmert_response.toxicity_score > 0.5 else 0.05,
                cortisol_impact=graphmert_response.toxicity_score * 0.3,
                description=f"User input (toxicity: {graphmert_response.toxicity_score:.2f}, urgency: {graphmert_response.urgency_score:.2f})"
            )
            
            # Update cycle
            flags = self.neurotransmitter_engine.update_cycle(stimulus)
            
            nt_state = self.neurotransmitter_engine.get_state()
            state.neurotransmitter_state = {
                "dopamine": nt_state.dopamine,
                "serotonin": nt_state.serotonin,
                "cortisol": nt_state.cortisol
            }
            state.emotional_flags = {
                "defensive_posture": flags.defensive_posture,
                "high_motivation": flags.high_motivation,
                "emotional_instability": flags.emotional_instability,
                "balanced_state": flags.balanced_state
            }
            state.stimulus_applied = {
                "dopamine_impact": stimulus.dopamine_impact,
                "serotonin_impact": stimulus.serotonin_impact,
                "cortisol_impact": stimulus.cortisol_impact,
                "description": stimulus.description
            }
            
            logger.info(f"  ✓ Emotional state updated (D: {nt_state.dopamine:.2f}, S: {nt_state.serotonin:.2f}, C: {nt_state.cortisol:.2f})")
        else:
            logger.info("Step 2/5: Neurotransmitter SKIPPED (disabled)")
        
        # Step 3: Think - Dialectic Reasoning
        dialectical_chain = None
        if self.dialectic_inference:
            logger.info("Step 3/5: Dialectic Reasoning")
            dialectical_chain = self.dialectic_inference.generate_dialectical_thought(
                user_input, context
            )
            state.dialectical_chain = dialectical_chain.to_dict()
            logger.info(f"  ✓ Dialectical chain generated")
        else:
            logger.info("Step 3/5: Dialectic SKIPPED (disabled)")
        
        # Step 4: Act - Generate final response
        logger.info("Step 4/5: Generate Response")
        if dialectical_chain and self.dialectic_config['use_synthesis_output']:
            # Use synthesis as final output
            state.final_response = dialectical_chain.synthesis.content
            logger.info(f"  ✓ Using dialectical synthesis")
        else:
            # Fallback: Use triples or raw input
            if graphmert_response and self.agent_loop_config['reason_on_triples']:
                # Format triples as context for response
                triple_context = "\n".join([
                    f"  - {triple}" 
                    for triple in graphmert_response.fact_triples
                ])
                state.final_response = f"[RESPONSE BASED ON TRIPLES]\n{triple_context}"
                logger.info(f"  ✓ Using triples for reasoning")
            else:
                state.final_response = f"[RESPONSE TO: {user_input}]"
                logger.info(f"  ✓ Using raw input")
        
        # Step 5: Record - Log to Convex
        if self.convex_logger:
            logger.info("Step 5/5: Log to Convex")
            
            # Log interaction
            await self.convex_logger.log_interaction(
                user_input=user_input,
                agent_output=state.final_response,
                metadata={
                    "interaction_number": self.total_interactions,
                    "graphmert_enabled": self.graphmert_client is not None,
                    "neurotransmitter_enabled": self.neurotransmitter_engine is not None,
                    "dialectic_enabled": self.dialectic_inference is not None
                }
            )
            
            # Log neurotransmitter state if available
            if state.neurotransmitter_state:
                await self.convex_logger.log_neurotransmitter_state(
                    state=state.neurotransmitter_state,
                    metadata={"flags": state.emotional_flags}
                )
            
            # Log dialectical chain if available
            if state.dialectical_chain:
                await self.convex_logger.log_dialectical_chain(
                    chain=state.dialectical_chain
                )
            
            # Log emotional event if stimulus was applied
            if stimulus:
                await self.convex_logger.log_emotional_event(
                    event_type="user_interaction",
                    description=stimulus.description,
                    emotional_impact={
                        "dopamine": stimulus.dopamine_impact,
                        "serotonin": stimulus.serotonin_impact,
                        "cortisol": stimulus.cortisol_impact
                    }
                )
            
            logger.info(f"  ✓ State logged to Convex")
        else:
            logger.info("Step 5/5: Convex SKIPPED (disabled)")
        
        # Calculate processing time
        state.processing_time_ms = (time.time() - start_time) * 1000
        
        logger.info("=" * 80)
        logger.info(f"INTERACTION #{self.total_interactions} COMPLETE ({state.processing_time_ms:.2f}ms)")
        logger.info("=" * 80)
        
        return state
    
    def get_llm_modifiers(self) -> Dict[str, Any]:
        """
        Get LLM parameter modifiers based on current emotional state.
        
        This allows the neurotransmitter engine to affect LLM behavior
        without exposing emotional state to the user.
        
        Returns:
            Dictionary of LLM parameter modifications
        """
        if self.neurotransmitter_engine:
            return self.neurotransmitter_engine.get_llm_modifiers()
        else:
            # Return defaults if neurotransmitter engine is disabled
            return {
                "temperature": 0.7,
                "top_p": 0.9,
                "presence_penalty": 0.0,
                "frequency_penalty": 0.0
            }
    
    def get_triples_context(self, state: HybridMindState) -> Optional[str]:
        """
        Get formatted triples context for LLM prompt.
        
        This allows reasoning on structured facts rather than raw text.
        
        Args:
            state: Current hybrid mind state
            
        Returns:
            Formatted triples context or None
        """
        if not state.graphmert_response or not self.agent_loop_config['reason_on_triples']:
            return None
        
        triples = state.graphmert_response.get('fact_triples', [])
        if not triples:
            return None
        
        # Format triples as structured context
        context_lines = ["VERIFIED FACTS (from GraphMERT):"]
        for triple in triples:
            subject = triple['subject']
            predicate = triple['predicate']
            obj = triple['object']
            confidence = triple['confidence']
            context_lines.append(f"  - ({subject}) -> [{predicate}] -> ({obj}) [confidence: {confidence:.2f}]")
        
        return "\n".join(context_lines)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get integration statistics.
        
        Returns:
            Dictionary with statistics
        """
        stats = {
            "total_interactions": self.total_interactions,
            "subsystems_enabled": {
                "graphmert": self.graphmert_client is not None,
                "neurotransmitter": self.neurotransmitter_engine is not None,
                "dialectic": self.dialectic_inference is not None,
                "convex": self.convex_logger is not None
            }
        }
        
        # Add subsystem-specific stats
        if self.graphmert_client:
            stats["graphmert_stats"] = self.graphmert_client.get_stats()
        
        if self.convex_logger:
            stats["convex_stats"] = self.convex_logger.get_stats()
        
        return stats


# Context manager for easy usage
class HybridMindContext:
    """
    Context manager for HybridMindIntegration.
    
    Usage:
        async with HybridMindContext() as mind:
            state = await mind.process_user_input("Hello, world!")
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize with same args as HybridMindIntegration."""
        self.mind = HybridMindIntegration(*args, **kwargs)
    
    async def __aenter__(self):
        """Start integration on context entry."""
        await self.mind.start()
        return self.mind
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Stop integration on context exit."""
        await self.mind.stop()
