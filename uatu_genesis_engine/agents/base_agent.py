"""
Base agent class for swarm framework.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
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
                # Modern desktop Chrome UA to reduce 404/429 blocks from some hosts
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            },
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    @abstractmethod
    async def execute(
        self, character_name: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute agent's task."""
        pass

    async def fetch_url(self, url: str) -> str:
        """Fetch content from URL with exponential backoff."""
        max_attempts = 3
        backoff_base = 1.0

        for attempt in range(1, max_attempts + 1):
            try:
                if not self.session:
                    logger.error(
                        f"{self.agent_id}: session not available, cannot fetch {url}"
                    )
                    return ""

                async with self.session.get(url) as response:
                    if response.status == 200:
                        return await response.text()

                    transient_statuses = {404, 429, 502, 503, 504}
                    if response.status in transient_statuses and attempt < max_attempts:
                        delay = backoff_base * (2 ** (attempt - 1))
                        logger.warning(
                            f"{self.agent_id}: received {response.status} for {url}; "
                            f"retrying in {delay:.1f}s (attempt {attempt}/{max_attempts})"
                        )
                        await asyncio.sleep(delay)
                        continue

                    logger.warning(f"Failed to fetch {url}: status {response.status}")
                    return ""

            except asyncio.TimeoutError:
                if attempt < max_attempts:
                    delay = backoff_base * (2 ** (attempt - 1))
                    logger.warning(
                        f"{self.agent_id}: timeout fetching {url}; "
                        f"retrying in {delay:.1f}s (attempt {attempt}/{max_attempts})"
                    )
                    await asyncio.sleep(delay)
                    continue

                logger.error(f"{self.agent_id}: timeout error fetching {url}")
                return ""

            except aiohttp.ClientError:
                if attempt < max_attempts:
                    delay = backoff_base * (2 ** (attempt - 1))
                    logger.warning(
                        f"{self.agent_id}: client error fetching {url}; "
                        f"retrying in {delay:.1f}s (attempt {attempt}/{max_attempts})"
                    )
                    await asyncio.sleep(delay)
                    continue

                logger.error(f"{self.agent_id}: client error fetching {url}")
                return ""

            except Exception as e:
                if attempt < max_attempts:
                    delay = backoff_base * (2 ** (attempt - 1))
                    logger.warning(
                        f"{self.agent_id}: error fetching {url}: {e}; "
                        f"retrying in {delay:.1f}s (attempt {attempt}/{max_attempts})"
                    )
                    await asyncio.sleep(delay)
                    continue

                logger.error(f"Error fetching {url}: {e}")
                return ""

        return ""

    def parse_html(self, html: str) -> BeautifulSoup:
        """Parse HTML content."""
        return BeautifulSoup(html, "html.parser")
