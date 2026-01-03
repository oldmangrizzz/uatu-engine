"""
Agent for gathering economic history and financial information.
"""

import logging
from typing import Dict, Any, List, Optional, Set
import re
from urllib.parse import quote_plus
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class EconomicHistoryAgent(BaseAgent):
    """Agent specialized in gathering economic and financial history."""

    # Canonical name mappings for known characters (mirrors CharacterInfoAgent)
    CHARACTER_MAPPINGS: Dict[str, Dict[str, str]] = {
        "anthony edward stark": {
            "wikipedia": "Iron_Man",
            "marvel_fandom": "Anthony_Stark_(Earth-616)",
            "aliases": ["tony stark", "iron man", "stark", "tony"],
            "companies": [
                "stark industries",
                "stark enterprises",
                "stark international",
                "stark unlimited",
            ],
        },
        "tony stark": {
            "wikipedia": "Iron_Man",
            "marvel_fandom": "Anthony_Stark_(Earth-616)",
            "aliases": ["anthony edward stark", "iron man", "stark", "tony"],
            "companies": [
                "stark industries",
                "stark enterprises",
                "stark international",
                "stark unlimited",
            ],
        },
        "iron man": {
            "wikipedia": "Iron_Man",
            "marvel_fandom": "Anthony_Stark_(Earth-616)",
            "aliases": ["tony stark", "anthony edward stark", "stark"],
            "companies": ["stark industries", "stark enterprises"],
        },
        "steve rogers": {
            "wikipedia": "Captain_America",
            "marvel_fandom": "Steven_Rogers_(Earth-616)",
            "aliases": ["captain america", "cap", "steve"],
            "companies": [],
        },
        "peter parker": {
            "wikipedia": "Spider-Man",
            "marvel_fandom": "Peter_Parker_(Earth-616)",
            "aliases": ["spider-man", "spiderman", "peter"],
            "companies": ["parker industries"],
        },
        "bruce banner": {
            "wikipedia": "Hulk",
            "marvel_fandom": "Bruce_Banner_(Earth-616)",
            "aliases": ["hulk", "bruce", "the hulk"],
            "companies": [],
        },
        "victor von doom": {
            "wikipedia": "Doctor_Doom",
            "marvel_fandom": "Victor_von_Doom_(Earth-616)",
            "aliases": ["doctor doom", "doom", "dr. doom", "dr doom"],
            "companies": ["latveria", "doom industries"],
        },
    }

    # Economic keywords that signal financial/business content
    ECONOMIC_KEYWORDS: Set[str] = {
        "billion",
        "million",
        "trillion",
        "wealth",
        "fortune",
        "net worth",
        "company",
        "corporation",
        "enterprise",
        "industries",
        "business",
        "ceo",
        "founder",
        "owner",
        "inherited",
        "acquisition",
        "merger",
        "stock",
        "shares",
        "investment",
        "revenue",
        "profit",
        "assets",
        "bankrupt",
        "sold",
        "purchased",
        "buy",
        "sell",
        "trade",
        "contract",
        "deal",
        "funding",
        "investor",
        "entrepreneur",
    }

    def __init__(self):
        super().__init__("economic_history_agent")

    def _get_canonical_names(self, character_name: str) -> Dict[str, Any]:
        """Get canonical wiki page names and aliases for a character."""
        normalized = character_name.lower().strip()
        if normalized in self.CHARACTER_MAPPINGS:
            return self.CHARACTER_MAPPINGS[normalized]
        # Fallback: use formatted name
        formatted = character_name.replace(" ", "_")
        return {
            "wikipedia": formatted,
            "marvel_fandom": f"{formatted}_(Earth-616)",
            "aliases": [
                normalized,
                normalized.split()[0] if " " in normalized else normalized,
            ],
            "companies": [],
        }

    def _get_search_terms(self, character_name: str) -> Set[str]:
        """Get all search terms (name, aliases, companies) for matching."""
        canonical = self._get_canonical_names(character_name)
        terms = {character_name.lower()}
        terms.update(alias.lower() for alias in canonical.get("aliases", []))
        terms.update(company.lower() for company in canonical.get("companies", []))
        return terms

    async def execute(
        self, character_name: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Gather economic history information."""
        logger.info(f"Economic History Agent gathering data for: {character_name}")

        # Explicitly typed containers
        economic_events: List[Dict[str, Any]] = []
        wealth_estimates: List[Dict[str, Any]] = []
        business_ventures: List[Dict[str, Any]] = []
        sources_list: List[str] = []

        results = {
            "character_name": character_name,
            "economic_events": economic_events,
            "wealth_estimates": wealth_estimates,
            "business_ventures": business_ventures,
            "sources": sources_list,
        }

        # Get all search terms for this character
        search_terms = self._get_search_terms(character_name)
        logger.info(f"Search terms for economic data: {search_terms}")

        # Use canonical names for wiki lookups
        canonical = self._get_canonical_names(character_name)
        wealth_urls = [
            f"https://en.wikipedia.org/wiki/{canonical['wikipedia']}",
            f"https://marvel.fandom.com/wiki/{canonical['marvel_fandom']}",
            f"https://www.cbr.com/?s={quote_plus(character_name)}+net+worth",
        ]
        logger.info(f"Using canonical URLs: {wealth_urls[:2]}")

        for url in wealth_urls:
            html = await self.fetch_url(url)
            if html:
                economic_data = self._extract_economic_data(html, search_terms, url)
                if economic_data:
                    events = economic_data.get("events") or []
                    economic_events.extend(events)
                    wealth = economic_data.get("wealth_estimate")
                    if wealth:
                        wealth_estimates.append(wealth)
                    ventures = economic_data.get("business_ventures") or []
                    business_ventures.extend(ventures)
                    if events or wealth or ventures:
                        sources_list.append(url)

        # Deduplicate events by description
        seen_descriptions: Set[str] = set()
        unique_events = []
        for event in economic_events:
            desc = event.get("description", "").strip().lower()
            if desc and desc not in seen_descriptions:
                seen_descriptions.add(desc)
                unique_events.append(event)

        results["economic_events"] = unique_events

        logger.info(
            f"Found {len(unique_events)} economic events and {len(wealth_estimates)} wealth estimates for {character_name}"
        )
        return results

    def _extract_economic_data(
        self, html: str, search_terms: Set[str], source_url: str
    ) -> Dict[str, Any]:
        """Extract economic data from HTML content using flexible matching."""
        soup = self.parse_html(html)
        events: List[Dict[str, Any]] = []
        business_ventures: List[Dict[str, Any]] = []
        wealth_estimate: Optional[Dict[str, Any]] = None

        # Get full text for wealth extraction
        text = soup.get_text()

        # Extract dollar amounts with context
        # Pattern matches $X, $X million, $X billion, etc.
        dollar_pattern = r"\$\s*([\d,]+(?:\.\d{1,2})?)\s*(million|billion|trillion)?"
        matches = re.findall(dollar_pattern, text, re.IGNORECASE)

        if matches:
            # Find the largest amount as the wealth estimate
            max_amount = 0.0
            for amount_str, multiplier in matches:
                amount = self._parse_monetary_value(f"${amount_str} {multiplier}")
                if amount > max_amount:
                    max_amount = amount

            if max_amount > 0:
                wealth_estimate = {
                    "amount": max_amount,
                    "currency": "USD",
                    "source": source_url,
                }
                logger.debug(
                    f"Found wealth estimate: ${max_amount:,.0f} from {source_url}"
                )

        # Look for business/company mentions in paragraphs
        paragraphs = soup.find_all("p")
        for p in paragraphs:
            p_text = p.get_text()
            p_lower = p_text.lower()

            # Check if paragraph contains any search term
            term_found = any(term in p_lower for term in search_terms)
            if not term_found:
                continue

            # Check if paragraph contains economic keywords
            has_economic_content = any(kw in p_lower for kw in self.ECONOMIC_KEYWORDS)
            if not has_economic_content:
                continue

            # Extract sentences that contain economic content
            sentences = re.split(r"(?<=[.!?])\s+", p_text)
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) < 20:  # Skip very short fragments
                    continue

                sentence_lower = sentence.lower()

                # Must contain a search term OR a company name
                has_relevant_term = any(term in sentence_lower for term in search_terms)
                if not has_relevant_term:
                    continue

                # Classify the event type
                event_type = self._classify_event_type(sentence_lower)

                if event_type:
                    events.append(
                        {
                            "description": sentence[:500],  # Limit length
                            "type": event_type,
                            "source": source_url,
                        }
                    )

                    # Also capture as business venture if company-related
                    if event_type in [
                        "company_founding",
                        "acquisition",
                        "business_activity",
                    ]:
                        business_ventures.append(
                            {
                                "description": sentence[:500],
                                "type": event_type,
                            }
                        )

        return {
            "events": events,
            "wealth_estimate": wealth_estimate,
            "business_ventures": business_ventures,
        }

    def _classify_event_type(self, text: str) -> Optional[str]:
        """Classify the type of economic event from text."""
        text = text.lower()

        if any(kw in text for kw in ["founded", "established", "created", "started"]):
            return "company_founding"
        elif any(kw in text for kw in ["acquired", "bought", "purchased", "takeover"]):
            return "acquisition"
        elif any(kw in text for kw in ["sold", "divested", "liquidated"]):
            return "divestiture"
        elif any(kw in text for kw in ["bankrupt", "insolvency", "chapter 11"]):
            return "bankruptcy"
        elif any(kw in text for kw in ["ceo", "chairman", "president", "owner"]):
            return "leadership"
        elif any(
            kw in text for kw in ["billion", "million", "wealth", "fortune", "worth"]
        ):
            return "wealth_event"
        elif any(kw in text for kw in ["contract", "deal", "agreement", "partnership"]):
            return "deal"
        elif any(
            kw in text for kw in ["company", "corporation", "enterprise", "industries"]
        ):
            return "business_activity"

        return None

    def _parse_monetary_value(self, value_str: str) -> float:
        """Parse a monetary string to a float value."""
        try:
            # Remove $ and commas
            value_str = value_str.replace("$", "").replace(",", "").strip()

            # Handle millions, billions, trillions
            multiplier = 1
            value_str_lower = value_str.lower()

            if "trillion" in value_str_lower:
                multiplier = 1_000_000_000_000
                value_str = re.sub(r"\s*trillion.*", "", value_str_lower)
            elif "billion" in value_str_lower:
                multiplier = 1_000_000_000
                value_str = re.sub(r"\s*billion.*", "", value_str_lower)
            elif "million" in value_str_lower:
                multiplier = 1_000_000
                value_str = re.sub(r"\s*million.*", "", value_str_lower)

            base_value = float(value_str.strip())
            return base_value * multiplier
        except (ValueError, TypeError):
            return 0.0
