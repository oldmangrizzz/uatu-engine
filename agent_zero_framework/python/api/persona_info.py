"""
Persona Info API
Returns information about the current loaded persona including name, archetype, and avatar path.
"""
import os
from pathlib import Path
import yaml
from python.helpers.api import ApiHandler
from flask import Request


class PersonaInfo(ApiHandler):
    """Handler for retrieving persona information."""

    @classmethod
    def requires_auth(cls) -> bool:
        return False

    @classmethod
    def requires_csrf(cls) -> bool:
        return False

    @classmethod
    def get_methods(cls) -> list[str]:
        return ["GET"]

    async def process(self, input: dict, request: Request) -> dict:
        """
        Return persona information for the UI.

        Returns:
            Dictionary containing persona details.
        """
        # Try to load persona config from environment
        persona_dir = os.environ.get("AGENT_PROMPTS_DIR")
        primary_name = os.environ.get("AGENT_PROFILE", "The Workshop")
        
        # Look for persona config file
        config_path = None
        if persona_dir:
            # persona_dir is the prompts directory, go up one level
            persona_root = Path(persona_dir).parent
            config_path = persona_root / "persona_config.yaml"
        else:
            persona_root = None
        
        persona_data = {
            "primary_name": primary_name,
            "archetype": "Digital Person",
            "avatar_path": None
        }
        
        # Try to load persona config
        if persona_root and config_path and config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                
                persona_data["primary_name"] = config.get("primary_name", primary_name)
                persona_data["archetype"] = config.get("archetype", "Digital Person")
                
                # Check for avatar
                avatar_path = persona_root / "persona_data" / "avatar.png"
                if avatar_path.exists():
                    persona_data["avatar_path"] = str(avatar_path)
                
            except Exception as e:
                print(f"Warning: Could not load persona config: {e}")
        
        return persona_data
