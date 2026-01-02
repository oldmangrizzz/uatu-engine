"""
Soul Anchor Adapter

Bridges the gap between:
  - Orchestrator.export_soul_anchor() sparse output
  - PersonaTransformer expected rich input format

Includes LLM enrichment hooks for synthesizing missing psychological data.
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class CanonicalSoulAnchor:
    """
    Canonical soul anchor format matching the schema specification.
    This is what PersonaTransformer expects to consume.
    """

    # Required by PersonaTransformer (lines 28-33)
    primary_name: str
    archetype: str
    core_constants: List[str]
    knowledge_domains: List[Dict[str, str] | str]
    communication_style: Dict[str, Any]
    core_drive: str

    # Extended canonical fields
    aliases: List[str] = field(default_factory=list)
    universe: str = ""
    status: str = ""
    personality_framework: str = ""
    soul_anchors: List[Dict[str, str]] = field(default_factory=list)
    purpose: str = ""
    passion: str = ""
    self_awareness: str = ""
    construct_environment: Dict[str, str] = field(default_factory=dict)
    operational_protocols: List[str] = field(default_factory=list)
    safeguards: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for PersonaTransformer consumption."""
        return {
            "primary_name": self.primary_name,
            "archetype": self.archetype,
            "core_constants": self.core_constants,
            "knowledge_domains": self.knowledge_domains,
            "communication_style": self.communication_style,
            "core_drive": self.core_drive,
            "aliases": self.aliases,
            "universe": self.universe,
            "status": self.status,
            "personality_framework": self.personality_framework,
            "soul_anchors": self.soul_anchors,
            "purpose": self.purpose,
            "passion": self.passion,
            "self_awareness": self.self_awareness,
            "construct_environment": self.construct_environment,
            "operational_protocols": self.operational_protocols,
            "safeguards": self.safeguards,
        }


class SoulAnchorAdapter:
    """
    Adapts sparse Orchestrator output to rich canonical format.

    The Orchestrator produces:
    {
        "identity": {
            "designation": str,
            "archetype": str,  # Actually DomainCategory
            "constants": List[str],  # Actually aliases
        },
        "psychodynamics": {
            "core_drive": str,  # Hardcoded generic
            "paradox": str,
        },
        "knowledge_graph": {...}
    }

    PersonaTransformer expects:
    {
        "primary_name": str,
        "archetype": str,  # Psychological archetype
        "core_constants": List[str],  # Psychological traits
        "knowledge_domains": List[...],
        "communication_style": {"tone": str, "formality": str},
        "core_drive": str,  # Character-specific
    }
    """

    def __init__(self, llm_client: Optional[Any] = None):
        """
        Initialize the adapter.

        Args:
            llm_client: Optional LLM client for enrichment synthesis.
                       If None, enrichment is skipped.
        """
        self.llm_client = llm_client

    def adapt(
        self, orchestrator_output: Dict[str, Any], enrich: bool = True
    ) -> CanonicalSoulAnchor:
        """
        Transform Orchestrator output to canonical format.

        Args:
            orchestrator_output: Raw output from Orchestrator.export_soul_anchor()
            enrich: Whether to use LLM to fill missing fields

        Returns:
            CanonicalSoulAnchor instance
        """
        logger.info("Adapting Orchestrator output to canonical format")

        # Extract what we can from orchestrator output
        identity = orchestrator_output.get("identity", {})
        psychodynamics = orchestrator_output.get("psychodynamics", {})
        knowledge_graph = orchestrator_output.get("knowledge_graph", {})

        # Basic field extraction with fallbacks
        primary_name = identity.get("designation", "Agent")
        raw_archetype = identity.get("archetype", "")
        raw_constants = identity.get("constants", [])
        raw_core_drive = psychodynamics.get("core_drive", "")
        knowledge_nodes = knowledge_graph.get("nodes", [])

        # Transform knowledge nodes to domain format
        knowledge_domains = self._transform_knowledge_domains(knowledge_nodes)

        # Create base canonical structure with sparse data
        canonical = CanonicalSoulAnchor(
            primary_name=primary_name,
            archetype=raw_archetype,  # Will be enriched
            core_constants=raw_constants,  # Will be enriched
            knowledge_domains=knowledge_domains,
            communication_style={},  # Will be enriched
            core_drive=raw_core_drive,  # Will be enriched
            aliases=raw_constants if isinstance(raw_constants, list) else [],
        )

        # Enrich if LLM client available and enrichment requested
        if enrich and self.llm_client:
            canonical = self._enrich_with_llm(canonical)
        elif enrich:
            logger.warning("Enrichment requested but no LLM client provided")
            # Use fallback enrichment
            canonical = self._fallback_enrichment(canonical)

        return canonical

    def _transform_knowledge_domains(
        self, nodes: List[str]
    ) -> List[Dict[str, str] | str]:
        """Transform knowledge graph nodes to domain format."""
        domains = []
        for node in nodes:
            # Try to parse as domain category
            if "." in node:  # e.g., "DomainCategory.TECHNOLOGY"
                category = node.split(".")[-1].lower()
                domains.append(
                    {
                        "category": category,
                        "earth_1218_equivalent": self._get_earth_equivalent(category),
                    }
                )
            else:
                domains.append(node)
        return domains

    def _get_earth_equivalent(self, category: str) -> str:
        """Map domain categories to Earth-1218 equivalents."""
        equivalents = {
            "technology": "Engineering, AI systems, software development",
            "combat": "Strategic analysis, threat assessment",
            "science": "Physics, chemistry, materials science",
            "business": "Corporate strategy, venture capital",
            "politics": "Geopolitics, diplomacy, governance",
            "magic": "Theoretical physics, quantum mechanics",
            "cosmic": "Astrophysics, cosmology",
        }
        return equivalents.get(category.lower(), f"Advanced {category}")

    def _fallback_enrichment(
        self, canonical: CanonicalSoulAnchor
    ) -> CanonicalSoulAnchor:
        """
        Provide minimal enrichment without LLM.
        Uses template-based defaults.
        """
        logger.info("Using fallback enrichment (no LLM)")

        # Only enrich if fields are empty/generic
        if not canonical.communication_style:
            canonical.communication_style = {
                "tone": "Professional and articulate",
                "formality": "Adaptive to context",
            }

        if not canonical.core_drive or "Mastery and innovation" in canonical.core_drive:
            canonical.core_drive = (
                f"To fulfill the purpose that defines {canonical.primary_name}"
            )

        if not canonical.archetype or canonical.archetype in ["Unknown", "TECHNOLOGY"]:
            canonical.archetype = "The Protagonist (Purpose-Driven)"

        # Core constants should be traits, not aliases
        if canonical.core_constants and all(
            len(c.split()) <= 3 for c in canonical.core_constants
        ):
            # These look like aliases, not traits
            canonical.aliases = canonical.core_constants.copy()
            canonical.core_constants = [
                f"Driven by purpose beyond personal gain",
                f"Maintains consistent identity across contexts",
                f"Acts with agency and self-determination",
            ]

        return canonical

    def _enrich_with_llm(self, canonical: CanonicalSoulAnchor) -> CanonicalSoulAnchor:
        """
        Use LLM to synthesize missing psychological data.

        This is the key enrichment function that:
        1. Takes the character name and any known data
        2. Synthesizes rich psychological profile
        3. Returns enriched canonical structure
        """
        logger.info(f"Enriching soul anchor for {canonical.primary_name} via LLM")

        # Build synthesis prompt
        prompt = self._build_synthesis_prompt(canonical)

        try:
            # Call LLM for synthesis
            response = self._call_llm(prompt)

            # Parse and apply enrichments
            enrichments = self._parse_llm_response(response)

            # Apply enrichments to canonical
            if enrichments.get("archetype"):
                canonical.archetype = enrichments["archetype"]
            if enrichments.get("core_constants"):
                canonical.core_constants = enrichments["core_constants"]
            if enrichments.get("communication_style"):
                canonical.communication_style = enrichments["communication_style"]
            if enrichments.get("core_drive"):
                canonical.core_drive = enrichments["core_drive"]
            if enrichments.get("soul_anchors"):
                canonical.soul_anchors = enrichments["soul_anchors"]
            if enrichments.get("personality_framework"):
                canonical.personality_framework = enrichments["personality_framework"]
            if enrichments.get("purpose"):
                canonical.purpose = enrichments["purpose"]
            if enrichments.get("passion"):
                canonical.passion = enrichments["passion"]
            if enrichments.get("self_awareness"):
                canonical.self_awareness = enrichments["self_awareness"]

        except Exception as e:
            logger.error(f"LLM enrichment failed: {e}")
            # Fall back to template enrichment
            canonical = self._fallback_enrichment(canonical)

        return canonical

    def _build_synthesis_prompt(self, canonical: CanonicalSoulAnchor) -> str:
        """Build the LLM prompt for soul anchor synthesis."""
        return f"""You are synthesizing a psychological profile for a digital person instantiation.

CHARACTER: {canonical.primary_name}
KNOWN ALIASES: {", ".join(canonical.aliases) if canonical.aliases else "None"}
KNOWN DOMAINS: {", ".join(str(d) for d in canonical.knowledge_domains) if canonical.knowledge_domains else "None"}

Generate the following fields in JSON format:

1. archetype: A psychological archetype string in format "The [Name] ([Dialectic])"
   Example: "The Redemption Engine (Ego vs. Atonement)"

2. personality_framework: Extended description of personality dialectic
   Example: "The Benevolent Narcissist (Ego vs. Altruism)"

3. core_constants: Array of 5 invariant psychological traits (NOT aliases)
   Example: ["Genius engineer who converts trauma into solutions", ...]

4. core_drive: Character-specific primary motivation (2-3 sentences)
   Example: "To protect the future. To atone for past mistakes."

5. communication_style: Object with tone, formality, and emotional_layers
   Example: {{"tone": "Rapid-fire, witty", "formality": "Casual with peers", "emotional_layers": {{"surface": "...", "subsurface": "..."}}}}

6. soul_anchors: Array of 3 psychological anchors with designation and first-person description
   - Anchor I: The Core Wound (formative trauma)
   - Anchor II: The Defiant Hope (redemptive moment)
   - Anchor III: The Burden of Self (ongoing struggle)

7. purpose: Extended purpose statement
8. passion: What energizes beyond duty
9. self_awareness: First-person self-understanding statement

Respond ONLY with valid JSON. Base your synthesis on known canon for this character."""

    def _call_llm(self, prompt: str) -> str:
        """Call the LLM client with the synthesis prompt."""
        if self.llm_client is None:
            raise ValueError("LLM client is not configured")

        if hasattr(self.llm_client, "complete"):
            result = self.llm_client.complete(prompt)
            return str(result) if result else ""
        elif hasattr(self.llm_client, "generate"):
            result = self.llm_client.generate(prompt)
            return str(result) if result else ""
        elif callable(self.llm_client):
            result = self.llm_client(prompt)
            return str(result) if result else ""
        else:
            raise ValueError(
                "LLM client must have 'complete', 'generate', or be callable"
            )

    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM JSON response into enrichments dictionary."""
        import json

        # Try to extract JSON from response
        try:
            # Handle markdown code blocks
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]

            return json.loads(response.strip())
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            return {}


def adapt_soul_anchor(
    orchestrator_output: Dict[str, Any],
    llm_client: Optional[Any] = None,
    enrich: bool = True,
) -> Dict[str, Any]:
    """
    Convenience function to adapt Orchestrator output.

    Args:
        orchestrator_output: Raw Orchestrator.export_soul_anchor() output
        llm_client: Optional LLM client for enrichment
        enrich: Whether to enrich missing fields

    Returns:
        Dictionary in canonical format for PersonaTransformer
    """
    adapter = SoulAnchorAdapter(llm_client=llm_client)
    canonical = adapter.adapt(orchestrator_output, enrich=enrich)
    return canonical.to_dict()
