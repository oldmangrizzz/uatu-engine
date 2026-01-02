"""
Agent for gathering character information from various wikis and databases.
"""

import logging
from typing import Dict, Any, List, Pattern, cast
import asyncio
import re
from urllib.parse import quote_plus
from bs4 import BeautifulSoup, Tag
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
        ]
        # Community and social sources for hypotheses and fan canon
        self.community_sources = [
            ("reddit", "https://old.reddit.com/search?q={query}"),
            (
                "fandom_forums",
                "https://www.reddit.com/r/FanTheories/search?q={query}&restrict_sr=1",
            ),
        ]
        self.max_insights = 3
        self.min_snippet_length = 40
        self.max_candidate_multiplier = 20
        self._pattern_cache: Dict[str, Pattern] = {}

    async def execute(
        self, character_name: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
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
        constants: List[str] = []

        # Search across multiple wiki sources
        tasks = []
        for source_base in self.sources:
            # Format character name for URL
            formatted_name = character_name.replace(" ", "_")
            url = f"{source_base}{formatted_name}"
            tasks.append(self._search_wiki_source(url, source_base, character_name))

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
            community_tasks.append(
                self._search_community_source(url, name, name_pattern)
            )

        search_results = await asyncio.gather(*tasks, return_exceptions=True)
        community_results = await asyncio.gather(
            *community_tasks, return_exceptions=True
        )

        # Aggregate wiki results
        for result in search_results:
            if isinstance(result, dict):
                r = cast(Dict[str, Any], result)
                if r.get("found"):
                    # Add extracted data
                    aliases.extend(r.get("aliases", []))
                    occupations_list.extend(r.get("occupations", []))
                    first_appearances.extend(r.get("first_appearances", []))
                    multiversal_identities.extend(r.get("identities", []))
                    sources_list.extend(r.get("sources", []))
                    if r.get("traits"):
                        trait_sets.append(set(r.get("traits", [])))

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

        # Deduplicate and classify
        aliases = list(set(aliases))
        occupations_list = list(set(occupations_list))
        first_appearances = list(set(first_appearances))
        sources_list = list(set(sources_list))

        if trait_sets:
            constants, variables = self._classify_traits(trait_sets)
        else:
            constants, variables = self._extract_traits_from_multiverse(
                multiversal_identities
            )

        results = {
            "character_name": character_name,
            "aliases": aliases,
            "multiversal_identities": multiversal_identities,
            "occupations": occupations_list,
            "first_appearances": first_appearances,
            "sources": sources_list,
            "community_insights": community_insights,
            "constants": constants,
            "variables": variables,
        }

        logger.info(
            f"Found {len(multiversal_identities)} multiversal identities for {character_name}"
        )
        logger.info(f"Found {len(aliases)} aliases for {character_name}")
        logger.info(f"Found {len(occupations_list)} occupations for {character_name}")

        return results

    async def _search_wiki_source(
        self, url: str, source_base: str, character_name: str
    ) -> Dict[str, Any]:
        """Search a wiki source for character information, parsing infoboxes."""
        html = await self.fetch_url(url)
        if not html:
            return {"found": False, "source": url}

        soup = self.parse_html(html)

        # Look for infoboxes (common in wikis)
        infobox = soup.find("table", class_=re.compile("infobox", re.I))
        if not infobox:
            # Try alternative infobox selectors
            infobox = soup.find("table", {"class": "infobox"})

        if infobox:
            return self._parse_infobox(infobox, source_base, character_name, url)

        return {"found": False, "source": url}

    def _parse_infobox(
        self, infobox: Tag, source_base: str, character_name: str, url: str
    ) -> Dict[str, Any]:
        """Parse a wiki infobox table for character data."""
        aliases: List[str] = []
        occupations: List[str] = []
        first_appearances: List[str] = []
        universe: str = self._extract_universe(source_base, infobox)
        name: str = character_name
        traits: List[str] = []

        # Find all rows in the infobox
        rows = infobox.find_all("tr")
        for row in rows:
            header = row.find(["th", "td"], recursive=False)
            data = row.find_all(["td", "th"], recursive=False)

            if not header or len(data) < 2:
                continue

            header_text = header.get_text(strip=True).lower()
            data_text = data[1].get_text(strip=True)

            # Extract based on common infobox field names
            if "full name" in header_text or "real name" in header_text:
                if data_text and data_text != character_name:
                    aliases.append(data_text)
                    traits.append(f"Real name: {data_text}")
            elif (
                "alias" in header_text
                or "aliases" in header_text
                or "also known as" in header_text
            ):
                # Extract aliases (usually comma-separated)
                alias_list = [
                    a.strip() for a in re.split(r"[,;]|and", data_text) if a.strip()
                ]
                aliases.extend(alias_list)
                traits.extend(alias_list)
            elif (
                "occupation" in header_text
                or "job" in header_text
                or "profession" in header_text
            ):
                occupation_list = [
                    o.strip() for o in re.split(r"[,;]|and", data_text) if o.strip()
                ]
                occupations.extend(occupation_list)
                traits.extend(occupation_list)
            elif "first appearance" in header_text or "debut" in header_text:
                first_appearances.append(data_text)
                traits.append(f"First appearance: {data_text}")
            elif "species" in header_text or "race" in header_text:
                traits.append(f"Species: {data_text}")
            elif "place of origin" in header_text or "origin" in header_text:
                traits.append(f"Origin: {data_text}")
            elif "abilities" in header_text or "powers" in header_text:
                traits.append(f"Abilities: {data_text}")
            elif (
                "affiliation" in header_text
                or "team" in header_text
                or "organization" in header_text
            ):
                traits.append(f"Affiliation: {data_text}")
            elif "creator" in header_text or "created by" in header_text:
                traits.append(f"Creator: {data_text}")

        # Clean up aliases to remove empty strings and duplicates
        aliases = list(set([a for a in aliases if a and a.strip()]))
        occupations = list(set([o for o in occupations if o and o.strip()]))
        first_appearances = list(set([f for f in first_appearances if f and f.strip()]))

        return {
            "found": True,
            "source": url,
            "name": name,
            "aliases": aliases,
            "occupations": occupations,
            "first_appearances": first_appearances,
            "universe": universe,
            "traits": traits,
            "identities": [{"universe": universe, "name": name, "source": url}],
        }

    async def _search_community_source(
        self, url: str, label: str, name_pattern: Pattern[str]
    ) -> Dict[str, Any]:
        """Search community-driven sources for headcanon and hypotheses."""
        html = await self.fetch_url(url)
        if not html:
            return {"found": False, "source": url}

        soup = self.parse_html(html)
        insights: List[str] = []

        # Collect a handful of relevant snippets mentioning the character
        candidate_nodes = soup.find_all(
            ["p", "li", "div", "span"],
            limit=self.max_insights * self.max_candidate_multiplier,
        )

        for snippet in candidate_nodes:
            if len(insights) >= self.max_insights:
                break
            if snippet.name in {"div", "span"}:
                classes: List[str] = cast(List[str], snippet.get("class") or [])
                if classes and not any(
                    "content" in str(cls) or "comment" in str(cls) for cls in classes
                ):
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
            "insights": insights,
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

    def _extract_traits_from_multiverse(
        self, multiversal_identities: List[Dict[str, Any]]
    ) -> tuple[List[str], List[str]]:
        """Extract traits from multiversal identities when no trait_sets available."""
        constants = []
        variables = []

        universe_names = [ident.get("universe", "") for ident in multiversal_identities]
        universe_freq = {}
        for universe in universe_names:
            universe_freq[universe] = universe_freq.get(universe, 0) + 1

        for universe, count in universe_freq.items():
            if count >= 2:
                variables.append(universe)
            else:
                constants.append(universe)

        return constants, variables
