"""
Agent for gathering character information from various wikis and databases.
"""
import logging
from typing import Dict, Any, List, Pattern, cast
import asyncio
import re
from urllib.parse import quote_plus
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
        # Community and social sources for hypotheses and fan canon
        self.community_sources = [
            ("reddit", "https://old.reddit.com/search?q={query}"),
            ("fandom_forums", "https://www.reddit.com/r/FanTheories/search?q={query}&restrict_sr=1"),
            ("twitter_alt", "https://nitter.net/search?f=tweets&q={query}"),
            ("fanfiction", "https://www.fanfiction.net/search/?keywords={query}"),
            ("archiveofourown", "https://archiveofourown.org/works/search?work_search%5Bquery%5D={query}")
        ]
        self.max_insights = 3
        self.min_snippet_length = 40
        self.max_candidate_multiplier = 20
        self._pattern_cache: Dict[str, Pattern] = {}
    
    async def execute(self, character_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Gather basic character information."""
        logger.info(f"Character Info Agent gathering data for: {character_name}")
        
        # Local typed accumulators to satisfy static typing
        aliases: List[str] = []
        multiversal_identities: List[Dict[str, Any]] = []
        occupations_list: List[str] = list(context.get("occupations", []))
        first_appearances: List[str] = []
        sources_list: List[str] = []
        community_insights: List[str] = []
        trait_sets: List[set] = []
        
        # Search across multiple wiki sources
        tasks = []
        for source_base in self.sources:
            # Format character name for URL
            formatted_name = character_name.replace(" ", "_")
            url = f"{source_base}{formatted_name}"
            tasks.append(self._search_source(url, source_base))

        # Community/social sources (fan theories, headcanon, discussions)
        community_tasks = []
        encoded_query = quote_plus(character_name)
        name_pattern = self._pattern_cache.get(character_name)
        if not name_pattern:
            pattern_text = re.escape(character_name)
            name_pattern = re.compile(pattern_text, re.IGNORECASE)
            self._pattern_cache[character_name] = name_pattern
        for name, template in self.community_sources:
            url = template.format(query=encoded_query)
            community_tasks.append(self._search_community_source(url, name, name_pattern))
        
        search_results = await asyncio.gather(*tasks, return_exceptions=True)
        community_results = await asyncio.gather(*community_tasks, return_exceptions=True)
        
        # Aggregate results
        for result in search_results:
            if isinstance(result, dict):
                r = cast(Dict[str, Any], result)
                if r.get("found"):
                    traits_for_source = set()
                    aliases_val = r.get("aliases")
                    if aliases_val:
                        aliases.extend(cast(List[str], aliases_val))
                        traits_for_source.update(cast(List[str], aliases_val))
                    occupation_val = r.get("occupation")
                    if occupation_val:
                        occupations_list.append(cast(str, occupation_val))
                        traits_for_source.add(cast(str, occupation_val))
                    first_app = r.get("first_appearance")
                    if first_app:
                        first_appearances.append(cast(str, first_app))
                        traits_for_source.add(cast(str, first_app))
                    if r.get("universe"):
                        source_val = r.get("source")
                        multiversal_identities.append({
                            "universe": r.get("universe"),
                            "name": r.get("name", character_name),
                            "source": source_val
                        })
                        traits_for_source.add(cast(str, r.get("universe")))
                    source_val = r.get("source")
                    if source_val:
                        sources_list.append(cast(str, source_val))
                    if traits_for_source:
                        trait_sets.append(traits_for_source)
        # Aggregate community/headcanon sources
        for result in community_results:
            if isinstance(result, dict):
                r = cast(Dict[str, Any], result)
                if r.get("found"):
                    insights_val = r.get("insights")
                    if insights_val:
                        community_insights.extend(cast(List[str], insights_val))
                    source_val = r.get("source")
                    if source_val:
                        sources_list.append(cast(str, source_val))
        
        # Deduplicate
        aliases = list(set(aliases))
        occupations_list = list(set(occupations_list))
        sources_list = list(set(sources_list))
        constants, variables = self._classify_traits(trait_sets)
        
        results = {
            "character_name": character_name,
            "aliases": aliases,
            "multiversal_identities": multiversal_identities,
            "occupations": occupations_list,
            "first_appearances": first_appearances,
            "sources": sources_list,
            "community_insights": community_insights,
            "constants": constants,
            "variables": variables
        }
        
        logger.info(f"Found {len(results['sources'])} sources for {character_name}")
        return results
    
    async def _search_source(self, url: str, source_base: str) -> Dict[str, Any]:
        """Search a specific source for character information."""
        html = await self.fetch_url(url)
        if not html:
            return {"found": False, "source": url}
        
        soup = self.parse_html(html)
        aliases_local: List[str] = []
        occupation_local: str = ""
        first_appearance_local: str = ""
        name_local: str = ""
        
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
                    # Cast data.get_text() to str to satisfy type checkers
                    data_text = str(data.get_text()).strip()
                    
                    if "alias" in header_text or "also known" in header_text:
                        # Extract aliases
                        aliases = [a.strip() for a in data_text.split(",") if a.strip()]
                        aliases_local.extend(aliases)
                    elif "occupation" in header_text or "job" in header_text:
                        occupation_local = data_text
                    elif "first appearance" in header_text:
                        first_appearance_local = data_text
        
        return {
            "found": True,
            "source": url,
            "name": name_local,
            "aliases": aliases_local,
            "occupation": occupation_local,
            "first_appearance": first_appearance_local,
            "universe": self._extract_universe(source_base, soup)
        }

    async def _search_community_source(self, url: str, label: str, name_pattern: Pattern[str]) -> Dict[str, Any]:
        """Search community-driven sources (Reddit, social mirrors, forums) for headcanon and hypotheses."""
        html = await self.fetch_url(url)
        if not html:
            return {"found": False, "source": url}

        soup = self.parse_html(html)
        insights: List[str] = []

        # Collect a handful of relevant snippets mentioning the character
        candidate_nodes = soup.find_all(
            ["p", "li", "div", "span"],
            limit=self.max_insights * self.max_candidate_multiplier
        )  # BeautifulSoup returns a list[Tag] which supports get_text()

        for snippet in candidate_nodes:
            if len(insights) >= self.max_insights:
                break
            if snippet.name in {"div", "span"}:
                from typing import cast, List
                classes: List[str] = cast(List[str], snippet.get("class") or [])
                if classes and not any("content" in str(cls) or "comment" in str(cls) for cls in classes):
                    continue
            text = snippet.get_text(" ", strip=True)
            if not text or len(text) < self.min_snippet_length:
                continue
            if name_pattern.search(text):
                insights.append(text)

        return {
            "found": len(insights) > 0,
            "source": url,
            "community": label,
            "insights": insights
        }
    
    def _extract_universe(self, source_base: str, soup: BeautifulSoup) -> str:
        """Extract universe designation from the wiki."""
        if "marvel.fandom" in source_base:
            # Look for Marvel universe designation
            earth_tag = soup.find(text=re.compile(r"Earth-\d+"))
            if earth_tag:
                match = re.search(r"Earth-\d+", str(earth_tag))
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

    def _classify_traits(self, trait_sets: List[set]) -> tuple[List[str], List[str]]:
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
