"""
Lucius Fox Swarm Framework - Main package initialization.
"""
from .orchestrator import MultiversalSwarmOrchestrator
from .models import (
    CharacterProfile,
    MultiversalIdentity,
    KnowledgeDomain,
    EconomicEvent,
    DomainCategory
)
from .graph import MultiversalGraphGenerator

__version__ = "1.0.0"
__all__ = [
    "MultiversalSwarmOrchestrator",
    "CharacterProfile",
    "MultiversalIdentity",
    "KnowledgeDomain",
    "EconomicEvent",
    "DomainCategory",
    "MultiversalGraphGenerator",
]
