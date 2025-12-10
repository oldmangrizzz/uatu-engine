"""
Agent for mapping knowledge domains across dimensions.
"""
import logging
from typing import Dict, Any, List
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class KnowledgeDomainAgent(BaseAgent):
    """Agent specialized in mapping knowledge domains from fictional universe to Earth-1218."""
    
    def __init__(self):
        super().__init__("knowledge_domain_agent")
        
        # Domain mapping rules
        self.domain_mappings = {
            "magic": {
                "earth_1218_equivalent": "theoretical physics, quantum mechanics, advanced chemistry",
                "categories": ["science", "research"]
            },
            "technology": {
                "earth_1218_equivalent": "engineering, computer science, applied physics",
                "categories": ["engineering", "computer_science"]
            },
            "combat": {
                "earth_1218_equivalent": "martial arts, tactical training, military strategy",
                "categories": ["physical", "strategic"]
            },
            "healing": {
                "earth_1218_equivalent": "medicine, surgery, pharmacology, emergency response",
                "categories": ["medicine", "healthcare"]
            },
            "hacking": {
                "earth_1218_equivalent": "cybersecurity, network engineering, cryptography",
                "categories": ["computer_science", "security"]
            },
            "alchemy": {
                "earth_1218_equivalent": "chemistry, biochemistry, materials science",
                "categories": ["science", "research"]
            },
            "telepathy": {
                "earth_1218_equivalent": "psychology, neuroscience, cognitive science",
                "categories": ["science", "psychology"]
            }
        }
    
    async def execute(self, character_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Map knowledge domains for the character."""
        logger.info(f"Knowledge Domain Agent mapping domains for: {character_name}")
        
        results = {
            "character_name": character_name,
            "knowledge_domains": [],
            "skills": [],
            "sources": []
        }
        
        # Get character info from context
        occupations = context.get("occupations", [])
        multiversal_identities = context.get("multiversal_identities", [])
        
        # Search for skill and ability information
        sources = context.get("sources", [])
        
        for source in sources[:5]:  # Limit to prevent too many requests
            html = await self.fetch_url(source)
            if html:
                domains = self._extract_knowledge_domains(html, character_name, occupations)
                results["knowledge_domains"].extend(domains)
                if domains:
                    results["sources"].append(source)
        
        # Map to Earth-1218 equivalents
        results["knowledge_domains"] = self._map_to_earth_1218(results["knowledge_domains"])
        
        # Deduplicate
        results["knowledge_domains"] = self._deduplicate_domains(results["knowledge_domains"])
        
        logger.info(f"Mapped {len(results['knowledge_domains'])} knowledge domains for {character_name}")
        return results
    
    def _extract_knowledge_domains(self, html: str, character_name: str, occupations: List[str]) -> List[Dict[str, Any]]:
        """Extract knowledge domains from HTML content."""
        soup = self.parse_html(html)
        domains = []
        
        # Skills/abilities keywords to look for
        skill_keywords = [
            "skill", "ability", "power", "expertise", "knowledge", 
            "proficiency", "mastery", "talent", "capability", "competence",
            "genius", "expert", "specialist", "trained"
        ]
        
        # Look for skills sections
        text = soup.get_text().lower()
        
        # Check occupations for domain hints
        for occupation in occupations:
            occupation_lower = occupation.lower()
            if any(keyword in occupation_lower for keyword in ["scientist", "engineer", "doctor", "physician"]):
                domains.append({
                    "category": "science" if "scientist" in occupation_lower else "medicine" if "doctor" in occupation_lower or "physician" in occupation_lower else "engineering",
                    "original_context": occupation,
                    "proficiency": "expert"
                })
            elif any(keyword in occupation_lower for keyword in ["hacker", "programmer", "computer"]):
                domains.append({
                    "category": "computer_science",
                    "original_context": occupation,
                    "proficiency": "expert"
                })
            elif any(keyword in occupation_lower for keyword in ["business", "ceo", "executive", "entrepreneur"]):
                domains.append({
                    "category": "business",
                    "original_context": occupation,
                    "proficiency": "expert"
                })
        
        # Look for specific skill mentions in text
        if "genius" in text and "intellect" in text:
            domains.append({
                "category": "intelligence",
                "original_context": "genius-level intellect",
                "proficiency": "expert"
            })
        
        if any(keyword in text for keyword in ["martial arts", "combat", "fighter", "warrior"]):
            domains.append({
                "category": "combat",
                "original_context": "combat training",
                "proficiency": "advanced"
            })
        
        if any(keyword in text for keyword in ["magic", "sorcery", "wizard", "witch"]):
            domains.append({
                "category": "magic",
                "original_context": "magical abilities",
                "proficiency": "advanced"
            })
        
        return domains
    
    def _map_to_earth_1218(self, domains: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Map fictional domains to Earth-1218 equivalents."""
        mapped_domains = []
        
        for domain in domains:
            category = domain.get("category", "").lower()
            
            # Check if we have a mapping rule
            earth_equivalent = None
            if category in self.domain_mappings:
                earth_equivalent = self.domain_mappings[category]["earth_1218_equivalent"]
            else:
                # Default mapping - keep as is if already realistic
                earth_equivalent = category.replace("_", " ")
            
            mapped_domains.append({
                "category": category,
                "original_context": domain.get("original_context", ""),
                "earth_1218_equivalent": earth_equivalent,
                "proficiency_level": domain.get("proficiency", "intermediate"),
                "description": f"Mastery of {earth_equivalent}"
            })
        
        return mapped_domains
    
    def _deduplicate_domains(self, domains: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate domains."""
        seen = set()
        unique_domains = []
        
        for domain in domains:
            key = (domain["category"], domain["earth_1218_equivalent"])
            if key not in seen:
                seen.add(key)
                unique_domains.append(domain)
        
        return unique_domains
