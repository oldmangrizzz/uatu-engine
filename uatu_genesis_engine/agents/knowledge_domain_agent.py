"""
Agent for mapping knowledge domains across dimensions.
"""
import logging
from typing import Dict, Any, List
from .base_agent import BaseAgent
from ..models import DomainCategory

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
            },
            "repulsor": {
                "earth_1218_equivalent": "High-Density Muon Propulsion / Ion Thruster Theoreticals",
                "categories": ["technology", "physics"]
            },
            "vibranium": {
                "earth_1218_equivalent": "Advanced Material Science / Impact-Absorbing Lattice Structures",
                "categories": ["materials_science", "physics"]
            }
        }
        self.tech_equivalents = {
            "repulsor": "High-Density Muon Propulsion / Ion Thruster Theoreticals",
            "arc reactor": "Compact Fusion Torus / Palladium-Free Energy Systems",
            "vibranium": "Advanced Material Science / Impact-Absorbing Lattice Structures",
            "web-shooter": "Non-Newtonian Polymer Dynamics / High-Tensile Microfluidics",
        }
    
    async def execute(self, character_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Map knowledge domains for the character."""
        from typing import cast
        logger.info(f"Knowledge Domain Agent mapping domains for: {character_name}")
        
        # Explicitly typed containers to satisfy mypy
        knowledge_domains: List[Dict[str, Any]] = []
        sources_list: List[str] = []
        results: Dict[str, Any] = {
            "character_name": character_name,
            "knowledge_domains": knowledge_domains,
            "skills": [],
            "sources": sources_list
        }
        
        # Get character info from context
        occupations = list(context.get("occupations", []))
        multiversal_identities = list(context.get("multiversal_identities", []))

        # Search for skill and ability information
        sources = list(context.get("sources", []))
        
        for source in sources[:5]:  # Limit to prevent too many requests
            html = await self.fetch_url(source)
            if html:
                domains = self._extract_knowledge_domains(html, character_name, occupations)
                # Ensure we work with a list
                if isinstance(domains, list):
                    knowledge_domains.extend(cast(List[Dict[str, Any]], domains))
                    if domains:
                        sources_list.append(source)
        
        # Map to Earth-1218 equivalents
        knowledge_domains = self._map_to_earth_1218(knowledge_domains)
        
        # Deduplicate - ensure list typing for mypy
        knowledge_domains = list(self._deduplicate_domains(knowledge_domains))
        results["knowledge_domains"] = knowledge_domains
        results["sources"] = sources_list
        
        logger.info(f"Mapped {len(results['knowledge_domains'])} knowledge domains for {character_name}")
        return results
        
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

        tech_keywords = {
            "repulsor": "repulsor technology",
            "arc reactor": "arc reactor technology",
            "vibranium": "vibranium-based equipment",
        }
        for keyword, context in tech_keywords.items():
            if keyword in text:
                domains.append({
                    "category": DomainCategory.TECHNOLOGY,
                    "original_context": context,
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
            search_text = f"{category} {domain.get('original_context', '')}".lower()

            # Direct technology keyword translation (repulsor tech, vibranium, etc.)
            for keyword, translation in self.tech_equivalents.items():
                if keyword in search_text:
                    earth_equivalent = translation
                    category = "technology"
                    break

            if earth_equivalent is None:
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
