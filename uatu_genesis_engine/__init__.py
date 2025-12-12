"""
Uatu Genesis Engine - Main package initialization.
"""
from .orchestrator import MultiversalSwarmOrchestrator
from .models import (
    CharacterProfile,
    MultiversalIdentity,
    KnowledgeDomain,
    EconomicEvent,
    DomainCategory,
    TimeSeriesEvent,
)
from .graph import MultiversalGraphGenerator

# Provide a forward-looking alias to reinforce the new engine identity
UatuGenesisEngine = MultiversalSwarmOrchestrator

__version__ = "1.0.0"
__all__ = [
    "MultiversalSwarmOrchestrator",
    "UatuGenesisEngine",
    "CharacterProfile",
    "MultiversalIdentity",
    "KnowledgeDomain",
    "EconomicEvent",
    "TimeSeriesEvent",
    "DomainCategory",
    "MultiversalGraphGenerator",
]
