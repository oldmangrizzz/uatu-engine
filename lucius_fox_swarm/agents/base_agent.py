"""
Base agent class for the swarm framework.
"""
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import aiohttp
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all swarm agents."""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                'User-Agent': 'Mozilla/5.0 (compatible; LuciusFoxSwarm/1.0; +https://github.com/oldmangrizzz/Lucius-Fox-digital-person-Earth-1218)'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    @abstractmethod
    async def execute(self, character_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's task."""
        pass
    
    async def fetch_url(self, url: str) -> str:
        """Fetch content from a URL."""
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    logger.warning(f"Failed to fetch {url}: status {response.status}")
                    return ""
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return ""
    
    def parse_html(self, html: str) -> BeautifulSoup:
        """Parse HTML content."""
        return BeautifulSoup(html, 'html.parser')
