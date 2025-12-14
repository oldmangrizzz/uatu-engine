"""
GraphMERTClient - Neurosymbolic Truth Filter

This module implements the "Truth Layer" that intercepts user input before
it hits the LLM or Vector DB. It converts raw text into structured fact triples
using a neurosymbolic reasoning endpoint.

The purpose is to prevent the agent from "hallucinating" on raw text by forcing
all input to pass through a verification/extraction phase that produces
structured knowledge triples.

Example:
    Input: "Lucius, I need help with the Wayne Enterprises hack."
    Output: [
        (User) -> [REQUEST] -> (Help),
        (Object: Wayne Enterprises) -> [STATUS] -> (Compromised)
    ]
"""
import logging
import re
import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class FactTriple:
    """
    Represents a knowledge graph triple: (Subject) -> [Predicate] -> (Object)
    
    This is the atomic unit of verified knowledge extracted from user input.
    """
    subject: str
    predicate: str
    object: str
    predicate_type: str  # e.g., "REQUEST", "STATUS", "RELATION", "PROPERTY", "EVENT"
    confidence: float = 1.0  # 0.0-1.0 confidence in this fact
    source: str = "user_input"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage/logging."""
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
    
    def __str__(self) -> str:
        """Human-readable representation."""
        return f"({self.subject}) -> [{self.predicate}] -> ({self.object})"


@dataclass
class GraphMERTResponse:
    """
    Complete response from GraphMERT neurosymbolic endpoint.
    
    Contains extracted triples, analysis metadata, and original input.
    """
    original_input: str
    fact_triples: List[FactTriple]
    entities_detected: List[str]
    intent_detected: Optional[str] = None
    toxicity_score: float = 0.0  # 0.0-1.0, used for neurotransmitter updates
    urgency_score: float = 0.5   # 0.0-1.0, used for neurotransmitter updates
    processing_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage/logging."""
        return {
            "original_input": self.original_input,
            "fact_triples": [triple.to_dict() for triple in self.fact_triples],
            "entities_detected": self.entities_detected,
            "intent_detected": self.intent_detected,
            "toxicity_score": self.toxicity_score,
            "urgency_score": self.urgency_score,
            "processing_time_ms": self.processing_time_ms,
            "metadata": self.metadata
        }


class GraphMERTClient:
    """
    Client for GraphMERT neurosymbolic reasoning endpoint.
    
    This client intercepts user input and extracts structured fact triples
    before the text reaches the LLM. It acts as a "firewall" against
    hallucination by forcing reasoning on verified facts rather than raw text.
    
    Current implementation uses a mock neurosymbolic endpoint with pattern-based
    extraction. In production, this would call an actual GraphMERT service.
    """
    
    # Toxicity detection word lists
    TOXIC_WORDS = ['hack', 'breach', 'attack', 'emergency', 'urgent', 'critical', 'danger']
    AGGRESSIVE_WORDS = ['damn', 'hell', 'stupid', 'idiot', 'useless']
    
    # Urgency detection word lists
    URGENT_WORDS = ['urgent', 'emergency', 'asap', 'immediately', 'now', 'critical']
    
    # Scoring weights
    TOXIC_WORD_WEIGHT = 0.15
    AGGRESSIVE_WORD_WEIGHT = 0.2
    URGENT_WORD_WEIGHT = 0.15
    EXCLAMATION_WEIGHT = 0.05
    CAPS_URGENCY_WEIGHT = 0.2
    
    def __init__(
        self,
        endpoint_url: Optional[str] = None,
        api_key: Optional[str] = None,
        enable_mock: bool = True,
        confidence_threshold: float = 0.6
    ):
        """
        Initialize the GraphMERT client.
        
        Args:
            endpoint_url: URL of the GraphMERT neurosymbolic endpoint
            api_key: API key for authentication
            enable_mock: Use mock extraction if True (default for MVP)
            confidence_threshold: Minimum confidence for fact extraction
        """
        self.endpoint_url = endpoint_url
        self.api_key = api_key
        self.enable_mock = enable_mock
        self.confidence_threshold = confidence_threshold
        
        # Statistics
        self.total_requests = 0
        self.total_triples_extracted = 0
        
        if self.enable_mock:
            logger.warning("GraphMERTClient initialized in MOCK MODE")
        else:
            logger.info(f"GraphMERTClient initialized with endpoint: {endpoint_url}")
    
    async def extract_triples(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None
    ) -> GraphMERTResponse:
        """
        Extract fact triples from user input.
        
        This is the main entry point for the Truth Filter. It takes raw user
        text and returns structured fact triples that can be reasoned upon.
        
        Args:
            user_input: Raw text from the user
            context: Optional context (e.g., conversation history, user profile)
            
        Returns:
            GraphMERTResponse with extracted triples and metadata
        """
        import time
        start_time = time.time()
        
        self.total_requests += 1
        logger.info(f"Processing input: {user_input[:100]}...")
        
        if self.enable_mock:
            response = await self._mock_extract_triples(user_input, context)
        else:
            response = await self._real_extract_triples(user_input, context)
        
        # Calculate processing time
        response.processing_time_ms = (time.time() - start_time) * 1000
        
        # Update statistics
        self.total_triples_extracted += len(response.fact_triples)
        
        logger.info(
            f"Extracted {len(response.fact_triples)} triples "
            f"(toxicity: {response.toxicity_score:.2f}, urgency: {response.urgency_score:.2f})"
        )
        
        return response
    
    async def _mock_extract_triples(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None
    ) -> GraphMERTResponse:
        """
        Mock triple extraction using pattern matching.
        
        This simulates a neurosymbolic endpoint by using heuristics to extract
        likely triples from the input text. Useful for MVP and testing.
        
        Args:
            user_input: Raw text from user
            context: Optional context
            
        Returns:
            GraphMERTResponse with extracted triples
        """
        triples = []
        entities = []
        
        # Extract entities (proper nouns, capitalized words)
        entity_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        detected_entities = re.findall(entity_pattern, user_input)
        entities.extend(detected_entities)
        
        # Pattern 1: Extract REQUEST patterns
        # "I need help with X", "Help me with X", "Can you assist with X"
        request_patterns = [
            (r'(?:I\s+)?need\s+help\s+(?:with|on)\s+([^.!?]+)', 'REQUEST'),
            (r'(?:help|assist)\s+(?:me\s+)?(?:with|on)\s+([^.!?]+)', 'REQUEST'),
            (r'can\s+you\s+(?:help|assist)\s+(?:me\s+)?(?:with|on)\s+([^.!?]+)', 'REQUEST'),
        ]
        
        for pattern, pred_type in request_patterns:
            matches = re.finditer(pattern, user_input, re.IGNORECASE)
            for match in matches:
                obj = match.group(1).strip()
                triples.append(FactTriple(
                    subject="User",
                    predicate="REQUEST",
                    object=obj,
                    predicate_type=pred_type,
                    confidence=0.9
                ))
        
        # Pattern 2: Extract STATUS patterns
        # "X is compromised", "X was hacked", "X is broken"
        status_patterns = [
            (r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:is|was)\s+(compromised|hacked|broken|damaged|down)', 'STATUS'),
            (r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:has\s+been)\s+(compromised|hacked|broken|damaged)', 'STATUS'),
        ]
        
        for pattern, pred_type in status_patterns:
            matches = re.finditer(pattern, user_input, re.IGNORECASE)
            for match in matches:
                subject = match.group(1).strip()
                status = match.group(2).strip().capitalize()
                triples.append(FactTriple(
                    subject=f"Object: {subject}",
                    predicate="STATUS",
                    object=status,
                    predicate_type=pred_type,
                    confidence=0.85
                ))
        
        # Pattern 3: Extract PROPERTY patterns
        # "X is Y", where Y is not a status word
        property_patterns = [
            (r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+is\s+(?:a|an)\s+([a-z]+(?:\s+[a-z]+)*)', 'PROPERTY'),
        ]
        
        for pattern, pred_type in property_patterns:
            matches = re.finditer(pattern, user_input, re.IGNORECASE)
            for match in matches:
                subject = match.group(1).strip()
                prop = match.group(2).strip()
                triples.append(FactTriple(
                    subject=subject,
                    predicate="IS_A",
                    object=prop,
                    predicate_type=pred_type,
                    confidence=0.75
                ))
        
        # Pattern 4: Extract RELATION patterns
        # "X works with Y", "X belongs to Y"
        relation_patterns = [
            (r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+works?\s+(?:with|for)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', 'WORKS_WITH'),
            (r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+belongs?\s+to\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', 'BELONGS_TO'),
        ]
        
        for pattern, pred_name in relation_patterns:
            matches = re.finditer(pattern, user_input, re.IGNORECASE)
            for match in matches:
                subject = match.group(1).strip()
                obj = match.group(2).strip()
                triples.append(FactTriple(
                    subject=subject,
                    predicate=pred_name,
                    object=obj,
                    predicate_type="RELATION",
                    confidence=0.8
                ))
        
        # Detect intent from input
        intent = self._detect_intent(user_input)
        
        # Calculate toxicity and urgency scores
        toxicity_score = self._calculate_toxicity(user_input)
        urgency_score = self._calculate_urgency(user_input)
        
        # If no triples extracted, create a generic conversation triple
        if not triples:
            triples.append(FactTriple(
                subject="User",
                predicate="STATEMENT",
                object=user_input[:100],  # Truncate long inputs
                predicate_type="CONVERSATION",
                confidence=0.6
            ))
        
        return GraphMERTResponse(
            original_input=user_input,
            fact_triples=triples,
            entities_detected=list(set(entities)),  # Remove duplicates
            intent_detected=intent,
            toxicity_score=toxicity_score,
            urgency_score=urgency_score,
            metadata={
                "extraction_mode": "mock",
                "patterns_used": len(request_patterns) + len(status_patterns) + len(property_patterns) + len(relation_patterns)
            }
        )
    
    async def _real_extract_triples(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None
    ) -> GraphMERTResponse:
        """
        Real triple extraction using GraphMERT neurosymbolic endpoint.
        
        This would make HTTP requests to the actual GraphMERT service.
        
        Args:
            user_input: Raw text from user
            context: Optional context
            
        Returns:
            GraphMERTResponse with extracted triples
        """
        # TODO: Implement actual API call to GraphMERT endpoint
        # For now, fall back to mock
        logger.warning("Real GraphMERT endpoint not implemented, falling back to mock")
        return await self._mock_extract_triples(user_input, context)
    
    def _detect_intent(self, user_input: str) -> Optional[str]:
        """
        Detect user intent from input.
        
        Args:
            user_input: Raw text from user
            
        Returns:
            Detected intent or None
        """
        input_lower = user_input.lower()
        
        # Intent patterns
        if any(word in input_lower for word in ['help', 'assist', 'support']):
            return "request_help"
        elif any(word in input_lower for word in ['hack', 'breach', 'compromise', 'attack']):
            return "security_incident"
        elif any(word in input_lower for word in ['how', 'what', 'why', 'when', 'where']):
            return "information_query"
        elif any(word in input_lower for word in ['please', 'can you', 'could you']):
            return "polite_request"
        else:
            return "general_conversation"
    
    def _calculate_toxicity(self, user_input: str) -> float:
        """
        Calculate toxicity score from input.
        
        Used to update neurotransmitter engine (high toxicity = stress).
        
        Args:
            user_input: Raw text from user
            
        Returns:
            Toxicity score (0.0-1.0)
        """
        input_lower = user_input.lower()
        toxicity = 0.0
        
        # Toxic indicators
        for word in self.TOXIC_WORDS:
            if word in input_lower:
                toxicity += self.TOXIC_WORD_WEIGHT
        
        # Aggressive indicators
        for word in self.AGGRESSIVE_WORDS:
            if word in input_lower:
                toxicity += self.AGGRESSIVE_WORD_WEIGHT
        
        # Cap at 1.0
        return min(1.0, toxicity)
    
    def _calculate_urgency(self, user_input: str) -> float:
        """
        Calculate urgency score from input.
        
        Used to update neurotransmitter engine (high urgency = increased dopamine).
        
        Args:
            user_input: Raw text from user
            
        Returns:
            Urgency score (0.0-1.0)
        """
        input_lower = user_input.lower()
        urgency = 0.5  # Default medium urgency
        
        # High urgency indicators
        for word in self.URGENT_WORDS:
            if word in input_lower:
                urgency += self.URGENT_WORD_WEIGHT
        
        # Multiple exclamation marks
        exclamation_count = user_input.count('!')
        urgency += min(0.2, exclamation_count * self.EXCLAMATION_WEIGHT)
        
        # All caps (screaming)
        if user_input.isupper() and len(user_input) > 10:
            urgency += self.CAPS_URGENCY_WEIGHT
        
        # Cap at 1.0
        return min(1.0, urgency)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get client statistics.
        
        Returns:
            Dictionary with statistics
        """
        return {
            "total_requests": self.total_requests,
            "total_triples_extracted": self.total_triples_extracted,
            "average_triples_per_request": (
                self.total_triples_extracted / self.total_requests
                if self.total_requests > 0 else 0
            ),
            "mode": "mock" if self.enable_mock else "real"
        }
