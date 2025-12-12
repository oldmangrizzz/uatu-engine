"""
Convex Seeder - Seeds compiled GraphMERT data to Convex database

This module uploads the neurosymbolic knowledge graph (the "Active Mind")
to Convex, ensuring Soul Anchor invariants are locked as root nodes.
"""
import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime

try:
    import aiohttp
except ImportError:
    aiohttp = None

from ..graphmert.compiler import GraphMERTData, FactTriple

logger = logging.getLogger(__name__)


class ConvexSeeder:
    """
    Seeds GraphMERT knowledge graphs to Convex database.
    
    This creates the "Active Mind" storage for each Digital Person,
    ensuring their knowledge graph is queryable and persistent.
    """
    
    def __init__(
        self,
        convex_url: Optional[str] = None,
        api_key: Optional[str] = None,
        mock_mode: bool = True
    ):
        """
        Initialize the Convex seeder.
        
        Args:
            convex_url: Convex deployment URL
            api_key: API key for authentication
            mock_mode: If True, simulate seeding without actual backend
        """
        self.convex_url = convex_url
        self.api_key = api_key
        self.mock_mode = mock_mode or convex_url is None
        
        if self.mock_mode:
            logger.warning("ConvexSeeder initialized in MOCK MODE (no Convex URL provided)")
        else:
            logger.info(f"ConvexSeeder initialized with URL: {convex_url}")
    
    async def seed_mind(
        self,
        graphmert_data: GraphMERTData,
        validate_invariants: bool = True
    ) -> Dict[str, Any]:
        """
        Seed a compiled GraphMERT knowledge graph to Convex.
        
        This uploads the "Active Mind" for a Digital Person, ensuring:
        1. Soul Anchor invariants are locked as root nodes
        2. All fact triples are stored with metadata
        3. The graph is queryable by the agent
        
        Args:
            graphmert_data: The compiled knowledge graph
            validate_invariants: If True, verify Soul Anchor invariants are present
            
        Returns:
            Dictionary with seeding results and statistics
        """
        logger.info("=" * 80)
        logger.info(f"SEEDING GRAPHMERT FOR: {graphmert_data.person_name}")
        logger.info("=" * 80)
        
        # Validate invariants if requested
        if validate_invariants:
            self._validate_root_invariants(graphmert_data)
        
        # Prepare payload
        payload = self._prepare_payload(graphmert_data)
        
        # Upload to Convex
        if self.mock_mode:
            result = await self._mock_seed(payload)
        else:
            result = await self._real_seed(payload)
        
        logger.info(f"Seeding complete:")
        logger.info(f"  Person: {result['person_name']}")
        logger.info(f"  Nodes seeded: {result['nodes_seeded']}")
        logger.info(f"  Facts seeded: {result['facts_seeded']}")
        logger.info(f"  Root invariants: {result['root_invariants_count']}")
        logger.info("=" * 80)
        
        return result
    
    def _validate_root_invariants(self, graphmert_data: GraphMERTData):
        """
        Validate that Soul Anchor invariants are present as root nodes.
        
        These are the immutable core traits that define the person's identity.
        """
        if not graphmert_data.root_invariants:
            logger.warning("No root invariants found in GraphMERT data")
            return
        
        # Check that invariants exist in fact triples
        invariant_facts = [
            triple for triple in graphmert_data.fact_triples
            if triple.predicate == "CORE_TRAIT" and triple.metadata.get("immutable") is True
        ]
        
        if len(invariant_facts) != len(graphmert_data.root_invariants):
            logger.warning(
                f"Mismatch in root invariants: "
                f"{len(graphmert_data.root_invariants)} declared, "
                f"{len(invariant_facts)} found in triples"
            )
        
        logger.info(f"✅ Validated {len(invariant_facts)} root invariants as immutable")
    
    def _prepare_payload(self, graphmert_data: GraphMERTData) -> Dict[str, Any]:
        """Prepare the payload for Convex upload."""
        return {
            "person_name": graphmert_data.person_name,
            "root_invariants": graphmert_data.root_invariants,
            "fact_triples": [triple.to_dict() for triple in graphmert_data.fact_triples],
            "node_count": graphmert_data.node_count,
            "edge_count": graphmert_data.edge_count,
            "compiled_at": graphmert_data.compiled_at,
            "seeded_at": datetime.now().isoformat(),
            "metadata": graphmert_data.metadata
        }
    
    async def _real_seed(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Seed to actual Convex backend.
        
        Makes HTTP POST request to Convex API.
        """
        if aiohttp is None:
            raise ImportError(
                "aiohttp is required for Convex integration. "
                "Install it with: pip install aiohttp"
            )
        
        headers = {
            "Content-Type": "application/json"
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.convex_url}/api/seed_mind",
                json=payload,
                headers=headers
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Convex API error {response.status}: {error_text}")
                
                result = await response.json()
                
                logger.info("Successfully seeded to Convex")
                
                return {
                    "person_name": payload["person_name"],
                    "nodes_seeded": payload["node_count"],
                    "facts_seeded": payload["edge_count"],
                    "root_invariants_count": len(payload["root_invariants"]),
                    "convex_response": result,
                    "seeded_at": payload["seeded_at"]
                }
    
    async def _mock_seed(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mock seeding for testing/development.
        
        Simulates seeding without actual backend connection.
        """
        logger.debug(f"[MOCK] Would seed GraphMERT for {payload['person_name']}")
        logger.debug(f"[MOCK] Payload size: {len(json.dumps(payload))} bytes")
        
        # Save to local file for inspection
        import os
        from pathlib import Path
        
        backup_dir = Path("./logs/graphmert_seeds")
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        person_safe = payload['person_name'].replace(" ", "_").lower()
        backup_file = backup_dir / f"graphmert_{person_safe}_{timestamp}.json"
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(payload, f, indent=2)
        
        logger.debug(f"[MOCK] Saved to: {backup_file}")
        
        return {
            "person_name": payload["person_name"],
            "nodes_seeded": payload["node_count"],
            "facts_seeded": payload["edge_count"],
            "root_invariants_count": len(payload["root_invariants"]),
            "mock_mode": True,
            "backup_file": str(backup_file),
            "seeded_at": payload["seeded_at"]
        }
    
    async def verify_seed(self, person_name: str) -> Dict[str, Any]:
        """
        Verify that a GraphMERT was successfully seeded to Convex.
        
        Args:
            person_name: Name of the person to verify
            
        Returns:
            Dictionary with verification results
        """
        if self.mock_mode:
            logger.warning("[MOCK] Cannot verify seed in mock mode")
            return {
                "verified": False,
                "mock_mode": True,
                "message": "Verification requires actual Convex connection"
            }
        
        if aiohttp is None:
            raise ImportError("aiohttp is required for Convex integration")
        
        headers = {
            "Content-Type": "application/json"
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.convex_url}/api/get_mind/{person_name}",
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "verified": True,
                        "person_name": person_name,
                        "node_count": data.get("node_count"),
                        "fact_count": data.get("edge_count"),
                        "seeded_at": data.get("seeded_at")
                    }
                else:
                    return {
                        "verified": False,
                        "person_name": person_name,
                        "error": f"HTTP {response.status}"
                    }


# Convex Schema for GraphMERT storage
CONVEX_GRAPHMERT_SCHEMA = {
    "minds": {
        "description": "Knowledge graphs for Digital Persons",
        "fields": {
            "person_name": "string",
            "root_invariants": "array",  # Soul Anchor constants (immutable)
            "node_count": "number",
            "edge_count": "number",
            "compiled_at": "string",
            "seeded_at": "string",
            "metadata": "object"
        },
        "indexes": ["person_name", "seeded_at"]
    },
    
    "fact_triples": {
        "description": "Individual knowledge facts",
        "fields": {
            "mind_id": "id",  # Reference to minds table
            "person_name": "string",
            "subject": "string",
            "predicate": "string",
            "object": "string",
            "predicate_type": "string",  # IDENTITY, SKILL, EVENT, ROLE, RELATION, PROPERTY
            "confidence": "number",
            "source": "string",
            "timestamp": "string",
            "metadata": "object",
            "immutable": "boolean"  # True for Soul Anchor invariants
        },
        "indexes": ["mind_id", "person_name", "subject", "predicate_type"]
    }
}


def get_convex_graphmert_schema() -> str:
    """
    Export Convex schema for GraphMERT tables.
    
    Returns:
        JSON string of schema definition
    """
    return json.dumps(CONVEX_GRAPHMERT_SCHEMA, indent=2)
