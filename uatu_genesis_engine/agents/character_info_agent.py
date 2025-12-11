"""
Agent for gathering character information from various wikis and databases.
"""
import logging
from typing import Dict, Any, List
import asyncio
import re
from bs4 import BeautifulSoup
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class CharacterInfoAgent(BaseAgent):
    """Agent specialized in gathering basic character information."""
    
    def __init__(self):
        super().__init__("character_info_agent")
        # Common wiki sources for fictional characters
        self.sources = [
            "https://en.wikipedia.org/wiki/",
            "https://marvel.fandom.com/wiki/",
            "https://dc.fandom.com/wiki/",
            "https://harrypotter.fandom.com/wiki/",
            "https://starwars.fandom.com/wiki/",
            "https://lotr.fandom.com/wiki/",
        ]
    
    async def execute(self, character_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Gather basic character information."""
        logger.info(f"Character Info Agent gathering data for: {character_name}")
        
        results = {
            "character_name": character_name,
            "aliases": [],
            "multiversal_identities": [],
            "occupations": [],
            "first_appearances": [],
            "sources": [],
            "constants": [],
            "variables": []
        }
        trait_sets: List[set] = []
        
        # Search across multiple wiki sources
        tasks = []
        for source_base in self.sources:
            # Format character name for URL
            formatted_name = character_name.replace(" ", "_")
            url = f"{source_base}{formatted_name}"
            tasks.append(self._search_source(url, source_base))
        
        search_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Aggregate results
        for result in search_results:
            if isinstance(result, dict) and result.get("found"):
                traits_for_source = set()
                if result.get("aliases"):
                    results["aliases"].extend(result["aliases"])
                    traits_for_source.update(result["aliases"])
                if result.get("occupation"):
                    results["occupations"].append(result["occupation"])
                    traits_for_source.add(result["occupation"])
                if result.get("first_appearance"):
                    results["first_appearances"].append(result["first_appearance"])
                    traits_for_source.add(result["first_appearance"])
                if result.get("universe"):
                    results["multiversal_identities"].append({
                        "universe": result["universe"],
                        "name": result.get("name", character_name),
                        "source": result.get("source")
                    })
                    traits_for_source.add(result["universe"])
                results["sources"].append(result.get("source"))
                if traits_for_source:
                    trait_sets.append(traits_for_source)
        
        # Deduplicate
        results["aliases"] = list(set(results["aliases"]))
        results["occupations"] = list(set(results["occupations"]))
        results["constants"], results["variables"] = self._classify_traits(trait_sets)
        
        logger.info(f"Found {len(results['sources'])} sources for {character_name}")
        return results
    
    async def _search_source(self, url: str, source_base: str) -> Dict[str, Any]:
        """Search a specific source for character information."""
        html = await self.fetch_url(url)
        if not html:
            return {"found": False, "source": url}
        
        soup = self.parse_html(html)
        result = {
            "found": True,
            "source": url,
            "name": "",
            "aliases": [],
            "occupation": "",
            "first_appearance": "",
            "universe": self._extract_universe(source_base, soup)
        }
        
        # Extract information based on common wiki patterns
        # This is a simplified extraction - real implementation would be more sophisticated
        
        # Look for infoboxes (common in wikis)
        infobox = soup.find("table", class_=re.compile("infobox", re.I))
        if infobox:
            rows = infobox.find_all("tr")
            for row in rows:
                header = row.find("th")
                data = row.find("td")
                if header and data:
                    header_text = header.get_text().strip().lower()
                    data_text = data.get_text().strip()
                    
                    if "alias" in header_text or "also known" in header_text:
                        # Extract aliases
                        aliases = [a.strip() for a in data_text.split(",") if a.strip()]
                        result["aliases"].extend(aliases)
                    elif "occupation" in header_text or "job" in header_text:
                        result["occupation"] = data_text
                    elif "first appearance" in header_text:
                        result["first_appearance"] = data_text
        
        return result
    
    def _extract_universe(self, source_base: str, soup: BeautifulSoup) -> str:
        """Extract universe designation from the wiki."""
        if "marvel.fandom" in source_base:
            # Look for Marvel universe designation
            earth_tag = soup.find(text=re.compile(r"Earth-\d+"))
            if earth_tag:
                match = re.search(r"Earth-\d+", earth_tag)
                if match:
                    return match.group(0)
            return "Marvel Comics (Universe Unknown)"
        elif "dc.fandom" in source_base:
            return "DC Comics"
        elif "harrypotter.fandom" in source_base:
            return "Harry Potter Universe"
        elif "starwars.fandom" in source_base:
            return "Star Wars Galaxy"
        elif "lotr.fandom" in source_base:
            return "Middle-earth"
        else:
            return "Unknown Universe"

    def _classify_traits(self, trait_sets: List[set]) -> (List[str], List[str]):
        """Classify traits as constants or variables based on frequency."""
        if not trait_sets:
            return [], []

        total_sources = len(trait_sets)
        freq: Dict[str, int] = {}

        for traits in trait_sets:
            for trait in traits:
                freq[trait] = freq.get(trait, 0) + 1

        constants = []
        variables = []
        for trait, count in freq.items():
            if count / total_sources >= 0.8:
                constants.append(trait)
            else:
                variables.append(trait)

        return list(set(constants)), list(set(variables))
