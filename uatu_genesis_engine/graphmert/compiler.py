"""
GraphMERT Compiler - Neurosymbolic Knowledge Graph Constructor

Converts CharacterProfile narrative data into structured fact triples
for the Digital Person's Active Mind knowledge graph.

Example:
    "Lucius Fox is the CEO of Wayne Enterprises"
    -> (Lucius Fox) -> [ROLE: CEO] -> (Wayne Enterprises)
"""
import logging
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

from ..models import (
    CharacterProfile,
    EconomicEvent
)

logger = logging.getLogger(__name__)


@dataclass
class FactTriple:
    """
    Represents a knowledge graph triple: (Subject) -> [Predicate] -> (Object)
    
    This is the atomic unit of knowledge in GraphMERT.
    """
    subject: str
    predicate: str
    object: str
    predicate_type: str  # e.g., "ROLE", "SKILL", "EVENT", "RELATION", "PROPERTY"
    confidence: float = 1.0  # 0.0-1.0 confidence in this fact
    source: str = "orchestrator"  # Where this fact came from
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "subject": self.subject,
            "predicate": self.predicate,
            "object": self.object,
            "predicate_type": self.predicate_type,
            "confidence": self.confidence,
            "source": self.source,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }


@dataclass
class GraphMERTData:
    """
    Complete compiled knowledge graph for a Digital Person.
    
    This is the "Active Mind" that gets stored in Convex.
    """
    person_name: str
    root_invariants: List[str]  # Soul Anchor constants - immutable root nodes
    fact_triples: List[FactTriple]
    node_count: int
    edge_count: int
    compiled_at: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "person_name": self.person_name,
            "root_invariants": self.root_invariants,
            "fact_triples": [triple.to_dict() for triple in self.fact_triples],
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "compiled_at": self.compiled_at,
            "metadata": self.metadata
        }


class GraphMERTCompiler:
    """
    Compiles CharacterProfile into a neurosymbolic knowledge graph.
    
    This is "Building the Brain" - extracting structured knowledge from
    narrative data and organizing it into a queryable graph structure.
    """
    
    def __init__(self):
        """Initialize the compiler."""
        self.fact_triples: List[FactTriple] = []
        self.nodes: set = set()
        logger.info("GraphMERTCompiler initialized")
    
    def compile(self, profile: CharacterProfile) -> GraphMERTData:
        """
        Compile a CharacterProfile into a GraphMERT knowledge graph.
        
        Args:
            profile: The CharacterProfile from the orchestrator
            
        Returns:
            GraphMERTData containing the compiled knowledge graph
        """
        logger.info("=" * 80)
        logger.info(f"COMPILING GRAPHMERT FOR: {profile.primary_name}")
        logger.info("=" * 80)
        
        # Reset state
        self.fact_triples = []
        self.nodes = set()
        
        # Add person as root node
        self.nodes.add(profile.primary_name)
        
        # Extract root invariants (Soul Anchor constants)
        root_invariants = profile.constants if profile.constants else []
        
        # Compile different data sources
        self._compile_identity_facts(profile)
        self._compile_knowledge_domains(profile)
        self._compile_economic_history(profile)
        self._compile_multiversal_identities(profile)
        self._compile_relationships(profile)
        
        # Create compiled graph
        graph_data = GraphMERTData(
            person_name=profile.primary_name,
            root_invariants=root_invariants,
            fact_triples=self.fact_triples,
            node_count=len(self.nodes),
            edge_count=len(self.fact_triples),
            metadata={
                "aliases": profile.aliases,
                "total_wealth": profile.total_wealth_estimate,
                "completeness_score": profile.completeness_score,
                "data_sources": profile.data_sources
            }
        )
        
        logger.info("Compilation complete:")
        logger.info(f"  Nodes: {graph_data.node_count}")
        logger.info(f"  Edges (Facts): {graph_data.edge_count}")
        logger.info(f"  Root Invariants: {len(root_invariants)}")
        logger.info("=" * 80)
        
        return graph_data
    
    def _compile_identity_facts(self, profile: CharacterProfile):
        """Extract identity-related facts."""
        person = profile.primary_name
        
        # Aliases
        for alias in profile.aliases:
            triple = FactTriple(
                subject=person,
                predicate="ALSO_KNOWN_AS",
                object=alias,
                predicate_type="IDENTITY",
                confidence=1.0,
                source="character_info"
            )
            self.fact_triples.append(triple)
            self.nodes.add(alias)
        
        # Constants (Soul Anchor invariants)
        for constant in profile.constants:
            triple = FactTriple(
                subject=person,
                predicate="CORE_TRAIT",
                object=constant,
                predicate_type="PROPERTY",
                confidence=1.0,
                source="soul_anchor",
                metadata={"immutable": True}
            )
            self.fact_triples.append(triple)
            self.nodes.add(constant)
        
        logger.debug(f"Extracted {len(profile.aliases)} aliases and {len(profile.constants)} core traits")
    
    def _compile_knowledge_domains(self, profile: CharacterProfile):
        """Extract knowledge domain facts."""
        person = profile.primary_name
        
        for domain in profile.knowledge_domains:
            # Main skill fact
            triple = FactTriple(
                subject=person,
                predicate=f"HAS_SKILL_{domain.proficiency_level.upper()}",
                object=domain.earth_1218_equivalent,
                predicate_type="SKILL",
                confidence=self._proficiency_to_confidence(domain.proficiency_level),
                source="knowledge_domain",
                metadata={
                    "category": str(domain.category),
                    "original_context": domain.original_context,
                    "description": domain.description
                }
            )
            self.fact_triples.append(triple)
            self.nodes.add(domain.earth_1218_equivalent)
            
            # Category relationship
            category_node = f"DOMAIN_{str(domain.category).upper()}"
            category_triple = FactTriple(
                subject=domain.earth_1218_equivalent,
                predicate="IN_CATEGORY",
                object=category_node,
                predicate_type="RELATION",
                confidence=1.0,
                source="knowledge_domain"
            )
            self.fact_triples.append(category_triple)
            self.nodes.add(category_node)
        
        logger.debug(f"Extracted {len(profile.knowledge_domains)} knowledge domains")
    
    def _compile_economic_history(self, profile: CharacterProfile):
        """
        Extract economic event facts.
        
        Example: "Acquired Wayne Enterprises in 2025"
        -> (Lucius Fox) -> [ACQUIRED: 2025] -> (Wayne Enterprises)
        """
        person = profile.primary_name
        
        for event in profile.economic_history:
            # Extract entities from description using pattern matching
            triple = self._extract_economic_triple(person, event)
            if triple:
                self.fact_triples.append(triple)
        
        logger.debug(f"Extracted {len(profile.economic_history)} economic events")
    
    def _extract_economic_triple(self, person: str, event: EconomicEvent) -> Optional[FactTriple]:
        """
        Extract a fact triple from an economic event description.
        
        Example:
            Description: "Acquired Wayne Enterprises in 2025"
            Returns: (Lucius Fox) -> [ACQUIRED: 2025] -> (Wayne Enterprises)
        """
        description = event.description
        
        # Pattern: "Acquired X"
        if match := re.search(r'(?i)acquired\s+([A-Z][A-Za-z\s]+)', description):
            entity = match.group(1).strip()
            triple = FactTriple(
                subject=person,
                predicate=f"ACQUIRED_{event.timestamp}",
                object=entity,
                predicate_type="EVENT",
                confidence=0.9,
                source="economic_history",
                metadata={
                    "event_type": event.event_type,
                    "amount": event.amount,
                    "currency": event.currency,
                    "source_universe": event.source_universe,
                    "full_description": description
                }
            )
            self.nodes.add(entity)
            return triple
        
        # Pattern: "CEO of X"
        if match := re.search(r'(?i)(CEO|CTO|CFO|President|Director|Manager)\s+of\s+([A-Z][A-Za-z\s]+)', description):
            role = match.group(1)
            entity = match.group(2).strip()
            triple = FactTriple(
                subject=person,
                predicate=f"ROLE_{role.upper()}",
                object=entity,
                predicate_type="ROLE",
                confidence=0.9,
                source="economic_history",
                metadata={
                    "timestamp": event.timestamp,
                    "full_description": description
                }
            )
            self.nodes.add(entity)
            return triple
        
        # Pattern: "Founded X"
        if match := re.search(r'(?i)founded\s+([A-Z][A-Za-z\s]+)', description):
            entity = match.group(1).strip()
            triple = FactTriple(
                subject=person,
                predicate=f"FOUNDED_{event.timestamp}",
                object=entity,
                predicate_type="EVENT",
                confidence=0.9,
                source="economic_history",
                metadata={
                    "amount": event.amount,
                    "full_description": description
                }
            )
            self.nodes.add(entity)
            return triple
        
        # Pattern: "Invested in X"
        if match := re.search(r'(?i)invested\s+in\s+([A-Z][A-Za-z\s]+)', description):
            entity = match.group(1).strip()
            triple = FactTriple(
                subject=person,
                predicate=f"INVESTED_{event.timestamp}",
                object=entity,
                predicate_type="EVENT",
                confidence=0.8,
                source="economic_history",
                metadata={
                    "amount": event.amount,
                    "currency": event.currency,
                    "full_description": description
                }
            )
            self.nodes.add(entity)
            return triple
        
        # Generic economic event (fallback)
        triple = FactTriple(
            subject=person,
            predicate=f"EVENT_{event.event_type.upper()}",
            object=event.timestamp,
            predicate_type="EVENT",
            confidence=0.7,
            source="economic_history",
            metadata={
                "amount": event.amount,
                "currency": event.currency,
                "description": description
            }
        )
        self.nodes.add(event.timestamp)
        return triple
    
    def _compile_multiversal_identities(self, profile: CharacterProfile):
        """Extract multiversal identity facts."""
        person = profile.primary_name
        
        for identity in profile.multiversal_identities:
            # Universe relationship
            triple = FactTriple(
                subject=person,
                predicate="EXISTS_IN",
                object=identity.universe_designation,
                predicate_type="RELATION",
                confidence=1.0,
                source="character_info",
                metadata={
                    "character_name": identity.character_name,
                    "occupation": identity.occupation,
                    "first_appearance": identity.first_appearance
                }
            )
            self.fact_triples.append(triple)
            self.nodes.add(identity.universe_designation)
            
            # Occupation in that universe
            if identity.occupation:
                occ_triple = FactTriple(
                    subject=person,
                    predicate=f"OCCUPATION_IN_{identity.universe_designation}",
                    object=identity.occupation,
                    predicate_type="ROLE",
                    confidence=0.9,
                    source="character_info"
                )
                self.fact_triples.append(occ_triple)
                self.nodes.add(identity.occupation)
        
        logger.debug(f"Extracted {len(profile.multiversal_identities)} multiversal identities")
    
    def _compile_relationships(self, profile: CharacterProfile):
        """Extract relationship facts from various sources."""
        person = profile.primary_name
        
        # Extract relationships from variables (contextual)
        for variable in profile.variables:
            # Pattern: "Works with X"
            if match := re.search(r'(?i)works\s+with\s+([A-Z][A-Za-z\s]+)', variable):
                entity = match.group(1).strip()
                triple = FactTriple(
                    subject=person,
                    predicate="WORKS_WITH",
                    object=entity,
                    predicate_type="RELATION",
                    confidence=0.8,
                    source="character_info",
                    metadata={"context": variable}
                )
                self.fact_triples.append(triple)
                self.nodes.add(entity)
            
            # Pattern: "Partner of X" / "Friend of X"
            if match := re.search(r'(?i)(partner|friend|ally|colleague)\s+of\s+([A-Z][A-Za-z\s]+)', variable):
                relation_type = match.group(1).upper()
                entity = match.group(2).strip()
                triple = FactTriple(
                    subject=person,
                    predicate=f"{relation_type}_OF",
                    object=entity,
                    predicate_type="RELATION",
                    confidence=0.8,
                    source="character_info",
                    metadata={"context": variable}
                )
                self.fact_triples.append(triple)
                self.nodes.add(entity)
        
        logger.debug(f"Extracted relationships from {len(profile.variables)} contextual variables")
    
    def _proficiency_to_confidence(self, proficiency: str) -> float:
        """Convert proficiency level to confidence score."""
        proficiency_map = {
            "expert": 1.0,
            "advanced": 0.9,
            "intermediate": 0.7,
            "beginner": 0.5
        }
        return proficiency_map.get(proficiency.lower(), 0.7)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get compilation statistics."""
        predicate_types: Dict[str, int] = {}
        for triple in self.fact_triples:
            predicate_types[triple.predicate_type] = predicate_types.get(triple.predicate_type, 0) + 1
        
        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.fact_triples),
            "predicate_type_distribution": predicate_types,
            "average_confidence": sum(t.confidence for t in self.fact_triples) / len(self.fact_triples) if self.fact_triples else 0
        }
