"""
Data models for the Multiversal History Framework.
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum


class DomainCategory(str, Enum):
    """Categories of knowledge domains."""
    COMPUTER_SCIENCE = "computer_science"
    SECURITY = "security"
    MEDICINE = "medicine"
    ENGINEERING = "engineering"
    BUSINESS = "business"
    SCIENCE = "science"
    ARTS = "arts"
    COMBAT = "combat"
    MAGIC = "magic"
    TECHNOLOGY = "technology"
    OTHER = "other"


class KnowledgeDomain(BaseModel):
    """Represents a knowledge domain with cross-dimensional mapping."""
    category: DomainCategory
    original_context: str = Field(description="How the skill exists in their universe")
    earth_1218_equivalent: str = Field(description="How the skill translates to our reality")
    proficiency_level: str = Field(description="Expert, Advanced, Intermediate, Beginner")
    description: str


class EconomicEvent(BaseModel):
    """Represents an economic event in character's history."""
    timestamp: str = Field(description="When the event occurred")
    event_type: str = Field(description="Type of economic event: income, expense, investment, etc.")
    amount: Optional[float] = Field(default=None, description="Monetary value if applicable")
    currency: Optional[str] = Field(default=None, description="Currency type")
    description: str
    source_universe: str = Field(description="Which universe/dimension this occurred in")
    earth_1218_equivalent_value: Optional[float] = Field(default=None, description="USD equivalent")


class MultiversalIdentity(BaseModel):
    """Represents the character across different universes/realities."""
    universe_designation: str = Field(description="e.g., Earth-616, Earth-1, Prime Earth")
    character_name: str
    occupation: Optional[str] = None
    first_appearance: Optional[str] = None
    key_characteristics: List[str] = Field(default_factory=list)


class CharacterProfile(BaseModel):
    """Complete profile of a fictional character across the multiverse."""
    primary_name: str
    aliases: List[str] = Field(default_factory=list)
    multiversal_identities: List[MultiversalIdentity] = Field(default_factory=list)
    knowledge_domains: List[KnowledgeDomain] = Field(default_factory=list)
    economic_history: List[EconomicEvent] = Field(default_factory=list)
    total_wealth_estimate: Optional[float] = Field(default=None, description="Earth-1218 USD equivalent")
    data_sources: List[str] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.now)
    completeness_score: float = Field(default=0.0, description="0-100% data completeness")


class SwarmTaskResult(BaseModel):
    """Result from a swarm agent task."""
    agent_id: str
    task_type: str
    success: bool
    data: Dict
    error_message: Optional[str] = None
    sources: List[str] = Field(default_factory=list)
