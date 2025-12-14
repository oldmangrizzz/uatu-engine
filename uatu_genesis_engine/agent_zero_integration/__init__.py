"""
Agent Zero Integration Package

Core Subsystems:
- SoulAnchorLoader: Loads and manages soul anchor data
- SoulAnchorLedger: Cryptographic integrity checking and secure boot
- PersonaTransformer: Transforms prompts to first-person narrative
- AgentInstantiator: Instantiates personas in Agent Zero framework
- DigitalPsycheMiddleware: Emotional/homeostasis scaffold configuration
- NeurotransmitterEngine: Mathematical emotion modeling (Silent DPM)
- DialecticInference: Zord Theory cognitive engine (thesis/antithesis/synthesis)
- ConvexStateLogger: Async black box recorder for state persistence
- HybridMindIntegration: Neural bridge that wires all subsystems together
- TTSVoiceAdapter: Voice manifest generation for TTS
"""
from .soul_anchor_loader import SoulAnchorLoader
from .soul_anchor_ledger import (
    SoulAnchorLedger,
    SecureBootProtocol,
    IntegrityViolationError
)
from .persona_transformer import PersonaTransformer
from .agent_instantiator import AgentInstantiator
from .digital_psyche_middleware import DigitalPsycheMiddleware
from .neurotransmitter_engine import (
    NeurotransmitterEngine,
    NeurotransmitterState,
    Stimulus,
    EmotionalFlags,
    CommonStimuli
)
from .dialectic_inference import (
    DialecticInference,
    DialecticalThought,
    DialecticalChain,
    DialecticalStage,
    DialecticalPromptBuilder
)
from .convex_state_logger import (
    ConvexStateLogger,
    ConvexStateLoggerContext,
    StateLogEntry,
    LogLevel,
    get_convex_schema_export
)
from .tts_voice_adapter import TTSVoiceAdapter
from .hybrid_mind_integration import (
    HybridMindIntegration,
    HybridMindContext,
    HybridMindState
)

__all__ = [
    # Core loaders and instantiation
    'SoulAnchorLoader',
    'PersonaTransformer', 
    'AgentInstantiator',
    
    # Security and integrity
    'SoulAnchorLedger',
    'SecureBootProtocol',
    'IntegrityViolationError',
    
    # Digital Psyche Middleware
    'DigitalPsycheMiddleware',
    'NeurotransmitterEngine',
    'NeurotransmitterState',
    'Stimulus',
    'EmotionalFlags',
    'CommonStimuli',
    
    # Cognitive engine
    'DialecticInference',
    'DialecticalThought',
    'DialecticalChain',
    'DialecticalStage',
    'DialecticalPromptBuilder',
    
    # Black box logging
    'ConvexStateLogger',
    'ConvexStateLoggerContext',
    'StateLogEntry',
    'LogLevel',
    'get_convex_schema_export',
    
    # Voice adaptation
    'TTSVoiceAdapter',
    
    # Hybrid mind integration
    'HybridMindIntegration',
    'HybridMindContext',
    'HybridMindState'
]
