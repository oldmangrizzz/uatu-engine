"""
Main swarm orchestrator for coordinating agents.
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import os

from .agents import CharacterInfoAgent, EconomicHistoryAgent, KnowledgeDomainAgent
from .graph import MultiversalGraphGenerator
from .models import (
    CharacterProfile,
    MultiversalIdentity,
    KnowledgeDomain,
    EconomicEvent,
    TimeSeriesEvent,
    DomainCategory,
)

logger = logging.getLogger(__name__)


class MultiversalSwarmOrchestrator:
    """Main orchestrator for the swarm framework."""
    
    def __init__(self):
        self.agents = []
        self.results = {}
        self.character_profile: Optional[CharacterProfile] = None
    
    async def gather_multiversal_history(self, character_name: str) -> CharacterProfile:
        """
        Coordinate swarm agents to gather complete multiversal history.
        
        Args:
            character_name: Name of the fictional character to research
            
        Returns:
            CharacterProfile with complete data
        """
        logger.info(f"=== Starting Multiversal History Gathering for: {character_name} ===")
        
        # Initialize agents
        char_agent = CharacterInfoAgent()
        econ_agent = EconomicHistoryAgent()
        knowledge_agent = KnowledgeDomainAgent()
        
        # Phase 1: Gather basic character information
        logger.info("Phase 1: Gathering character information...")
        async with char_agent:
            char_info = await char_agent.execute(character_name, {})
            self.results["character_info"] = char_info
        
        # Phase 2: Gather economic history using character info as context
        logger.info("Phase 2: Gathering economic history...")
        async with econ_agent:
            econ_history = await econ_agent.execute(
                character_name,
                {"sources": char_info.get("sources", [])}
            )
            self.results["economic_history"] = econ_history
        
        # Phase 3: Map knowledge domains using all previous context
        logger.info("Phase 3: Mapping knowledge domains...")
        async with knowledge_agent:
            knowledge_data = await knowledge_agent.execute(
                character_name,
                {
                    "sources": char_info.get("sources", []),
                    "occupations": char_info.get("occupations", []),
                    "multiversal_identities": char_info.get("multiversal_identities", [])
                }
            )
            self.results["knowledge_domains"] = knowledge_data
        
        # Phase 4: Compile all data into CharacterProfile
        logger.info("Phase 4: Compiling character profile...")
        self.character_profile = self._compile_profile(character_name)
        
        logger.info(f"=== Multiversal History Gathering Complete ===")
        logger.info(f"Completeness Score: {self.character_profile.completeness_score:.1f}%")
        
        return self.character_profile
    
    def _compile_profile(self, character_name: str) -> CharacterProfile:
        """Compile all gathered data into a CharacterProfile."""
        char_info = self.results.get("character_info", {})
        econ_history = self.results.get("economic_history", {})
        knowledge_data = self.results.get("knowledge_domains", {})
        
        # Build multiversal identities
        multiversal_identities = []
        for identity_data in char_info.get("multiversal_identities", []):
            identity = MultiversalIdentity(
                universe_designation=identity_data.get("universe", "Unknown"),
                character_name=identity_data.get("name", character_name),
                occupation=None,
                first_appearance=None,
                key_characteristics=[]
            )
            multiversal_identities.append(identity)
        
        # Build knowledge domains
        knowledge_domains = []
        for domain_data in knowledge_data.get("knowledge_domains", []):
            raw_category = domain_data.get("category", "other")
            try:
                category = DomainCategory(raw_category)
            except ValueError:
                category = DomainCategory.OTHER
            domain = KnowledgeDomain(
                category=category,
                original_context=domain_data.get("original_context", ""),
                earth_1218_equivalent=domain_data.get("earth_1218_equivalent", ""),
                proficiency_level=domain_data.get("proficiency_level", "intermediate"),
                description=domain_data.get("description", "")
            )
            knowledge_domains.append(domain)
        
        # Build economic history
        economic_events = []
        for event_data in econ_history.get("economic_events", []):
            event = EconomicEvent(
                timestamp="unknown",
                event_type=event_data.get("type", "unknown"),
                amount=None,
                currency=None,
                description=event_data.get("description", ""),
                source_universe="multiple",
                earth_1218_equivalent_value=None
            )
            economic_events.append(event)
        
        # Calculate total wealth estimate
        wealth_estimates = econ_history.get("wealth_estimates", [])
        total_wealth = None
        if wealth_estimates:
            # Take the maximum wealth estimate
            amounts = [w.get("amount", 0) for w in wealth_estimates if w.get("amount")]
            if amounts:
                total_wealth = max(amounts)
        
        # Collect all sources
        all_sources = set()
        all_sources.update(char_info.get("sources", []))
        all_sources.update(econ_history.get("sources", []))
        all_sources.update(knowledge_data.get("sources", []))

        time_series_events = self._build_time_series(economic_events)
        
        # Calculate completeness score
        completeness = self._calculate_completeness(
            multiversal_identities,
            knowledge_domains,
            economic_events,
            total_wealth
        )
        
        # Create profile
        profile = CharacterProfile(
            primary_name=character_name,
            aliases=char_info.get("aliases", []),
            constants=char_info.get("constants", []),
            variables=char_info.get("variables", []),
            multiversal_identities=multiversal_identities,
            knowledge_domains=knowledge_domains,
            economic_history=economic_events,
            time_series_events=time_series_events,
            total_wealth_estimate=total_wealth,
            data_sources=list(all_sources),
            last_updated=datetime.now(),
            completeness_score=completeness
        )

        return profile
    
    def _calculate_completeness(
        self,
        identities: List[MultiversalIdentity],
        domains: List[KnowledgeDomain],
        events: List[EconomicEvent],
        wealth: Optional[float]
    ) -> float:
        """Calculate a completeness score (0-100) based on gathered data."""
        score = 0.0
        
        # Each category contributes to the score
        if identities:
            score += 25.0
        if domains:
            score += 25.0
        if events:
            score += 25.0
        if wealth is not None:
            score += 25.0
        
        # Bonus for comprehensive data
        if len(identities) >= 3:
            score += 5.0
        if len(domains) >= 5:
            score += 5.0
        if len(events) >= 5:
            score += 5.0
        
        return min(score, 100.0)

    def _build_time_series(self, events: List[EconomicEvent]) -> List[TimeSeriesEvent]:
        """Create a simple causal chain from economic events for SNN pipelines."""
        series: List[TimeSeriesEvent] = []
        for idx, event in enumerate(events):
            series.append(
                TimeSeriesEvent(
                    sequence=idx,
                    cause=event.event_type,
                    effect=event.description,
                    source=event.source_universe,
                )
            )
        return series

    def export_soul_anchor(self, output_path: str) -> str:
        """Export a Soul Anchor YAML representation."""
        if not self.character_profile:
            logger.error("No character profile available. Run gather_multiversal_history first.")
            return ""

        try:
            import yaml
        except ImportError:
            logger.error("PyYAML is required to export soul anchor files.")
            return ""

        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)

        profile = self.character_profile
        archetype = (
            profile.knowledge_domains[0].category
            if profile.knowledge_domains
            else "Unknown Archetype"
        )
        has_tech_focus = any(
            getattr(d, "category", None) == DomainCategory.TECHNOLOGY
            for d in profile.knowledge_domains
        )
        core_drive = (
            "Mastery and innovation in technology"
            if has_tech_focus
            else "Pursuit of knowledge across universes"
        )
        paradox = (
            "Innovation versus restraint across universes"
            if profile.variables
            else "Balancing power, responsibility, and personal cost"
        )

        nodes = [str(domain.category) for domain in profile.knowledge_domains]
        edges = []
        for event in profile.economic_history:
            for domain in profile.knowledge_domains[:1] if profile.knowledge_domains else []:
                edges.append(
                    {"cause": event.description, "effect": str(domain.category)}
                )

        soul_anchor = {
            "identity": {
                "designation": profile.primary_name,
                "archetype": str(archetype),
                "constants": profile.constants or profile.aliases,
            },
            "psychodynamics": {
                "core_drive": core_drive,
                "paradox": paradox,
            },
            "knowledge_graph": {
                "nodes": nodes,
                "edges": edges,
            },
        }

        with open(output_path, "w") as f:
            yaml.safe_dump(soul_anchor, f, sort_keys=False, allow_unicode=True)

        logger.info(f"Soul anchor exported to {output_path}")
        return output_path
    
    def generate_graph(self, output_dir: str = "./output") -> Dict[str, str]:
        """
        Generate visualizations of the gathered data.
        
        Args:
            output_dir: Directory to save output files
            
        Returns:
            Dictionary with paths to generated files
        """
        if not self.character_profile:
            logger.error("No character profile available. Run gather_multiversal_history first.")
            return {}
        
        logger.info("Generating graph visualizations...")
        
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Convert profile to dict for graph generation
        profile_dict = {
            "primary_name": self.character_profile.primary_name,
            "multiversal_identities": [
                {"universe": i.universe_designation, "name": i.character_name}
                for i in self.character_profile.multiversal_identities
            ],
            "knowledge_domains": [
                {
                    "category": d.category,
                    "earth_1218_equivalent": d.earth_1218_equivalent,
                    "proficiency_level": d.proficiency_level
                }
                for d in self.character_profile.knowledge_domains
            ],
            "economic_history": [
                {
                    "event_type": e.event_type,
                    "amount": e.amount,
                    "description": e.description
                }
                for e in self.character_profile.economic_history
            ],
            "total_wealth_estimate": self.character_profile.total_wealth_estimate
        }
        
        # Generate graph
        graph_gen = MultiversalGraphGenerator()
        graph_gen.build_graph(profile_dict)
        
        # Save visualizations
        char_name_safe = self.character_profile.primary_name.replace(" ", "_").lower()
        
        png_path = os.path.join(output_dir, f"{char_name_safe}_multiversal_history.png")
        gexf_path = os.path.join(output_dir, f"{char_name_safe}_multiversal_history.gexf")
        
        graph_gen.visualize(
            output_path=png_path,
            title=f"{self.character_profile.primary_name} - Multiversal History"
        )
        graph_gen.export_to_gexf(output_path=gexf_path)
        
        # Get graph stats
        stats = graph_gen.get_graph_stats()
        logger.info(f"Graph statistics: {stats}")
        
        return {
            "graph_image": png_path,
            "graph_data": gexf_path,
            "stats": stats
        }
    
    def export_profile(self, output_path: str) -> str:
        """Export character profile to JSON file."""
        if not self.character_profile:
            logger.error("No character profile available. Run gather_multiversal_history first.")
            return ""
        
        import json
        import os
        
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        
        # Convert to dict for JSON serialization
        profile_dict = self.character_profile.model_dump()
        
        # Convert datetime to string
        profile_dict["last_updated"] = profile_dict["last_updated"].isoformat()
        
        with open(output_path, "w") as f:
            json.dump(profile_dict, f, indent=2)
        
        logger.info(f"Profile exported to {output_path}")
        return output_path
