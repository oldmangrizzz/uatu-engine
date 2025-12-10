"""
Agent for gathering economic history and financial information.
"""
import logging
from typing import Dict, Any, List
import re
from urllib.parse import quote_plus
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class EconomicHistoryAgent(BaseAgent):
    """Agent specialized in gathering economic and financial history."""
    
    def __init__(self):
        super().__init__("economic_history_agent")
    
    async def execute(self, character_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Gather economic history information."""
        logger.info(f"Economic History Agent gathering data for: {character_name}")
        
        results = {
            "character_name": character_name,
            "economic_events": [],
            "wealth_estimates": [],
            "business_ventures": [],
            "sources": []
        }
        
        # Search for economic information
        sources_to_check = context.get("sources", [])
        
        # Add specialized economic search terms
        search_queries = [
            f"{character_name} net worth",
            f"{character_name} wealth",
            f"{character_name} business",
            f"{character_name} company",
            f"{character_name} fortune",
            f"{character_name} assets"
        ]
        
        # For demonstration, we'll search fictional character wealth databases
        # Use proper URL encoding for safety
        wealth_urls = [
            f"https://www.therichest.com/tag/{quote_plus(character_name.lower())}/",
            f"https://fictionhorizon.com/?s={quote_plus(character_name)}+wealth",
        ]
        
        for url in wealth_urls:
            html = await self.fetch_url(url)
            if html:
                economic_data = self._extract_economic_data(html, character_name)
                if economic_data:
                    results["economic_events"].extend(economic_data.get("events", []))
                    if economic_data.get("wealth_estimate"):
                        results["wealth_estimates"].append(economic_data["wealth_estimate"])
                    results["sources"].append(url)
        
        logger.info(f"Found {len(results['economic_events'])} economic events for {character_name}")
        return results
    
    def _extract_economic_data(self, html: str, character_name: str) -> Dict[str, Any]:
        """Extract economic data from HTML content."""
        soup = self.parse_html(html)
        data = {
            "events": [],
            "wealth_estimate": None
        }
        
        # Look for wealth mentions in text
        text = soup.get_text()
        
        # Extract dollar amounts
        dollar_pattern = r'\$[\d,]+(?:\.\d{2})?(?:\s*(?:million|billion|trillion))?'
        matches = re.findall(dollar_pattern, text, re.IGNORECASE)
        
        if matches:
            # Try to extract the largest amount as wealth estimate
            max_amount = self._parse_monetary_value(matches[0])
            data["wealth_estimate"] = {
                "amount": max_amount,
                "currency": "USD",
                "source": "estimated"
            }
        
        # Look for business/company mentions
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            p_text = p.get_text()
            if any(keyword in p_text.lower() for keyword in ['company', 'business', 'corporation', 'enterprise', 'wealth', 'fortune']):
                # Extract potential economic events
                sentences = p_text.split('.')
                for sentence in sentences:
                    if character_name.lower() in sentence.lower():
                        data["events"].append({
                            "description": sentence.strip(),
                            "type": "business_activity"
                        })
        
        return data
    
    def _parse_monetary_value(self, value_str: str) -> float:
        """Parse a monetary string to a float value."""
        try:
            # Remove $ and commas
            value_str = value_str.replace('$', '').replace(',', '').strip()
            
            # Handle millions, billions, trillions
            multiplier = 1
            value_str_lower = value_str.lower()
            
            if 'trillion' in value_str_lower:
                multiplier = 1_000_000_000_000
                value_str = re.sub(r'\s*trillion.*', '', value_str_lower)
            elif 'billion' in value_str_lower:
                multiplier = 1_000_000_000
                value_str = re.sub(r'\s*billion.*', '', value_str_lower)
            elif 'million' in value_str_lower:
                multiplier = 1_000_000
                value_str = re.sub(r'\s*million.*', '', value_str_lower)
            
            base_value = float(value_str)
            return base_value * multiplier
        except (ValueError, TypeError) as e:
            return 0.0
