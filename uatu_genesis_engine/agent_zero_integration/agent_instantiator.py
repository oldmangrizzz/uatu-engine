"""
Agent Instantiator

Instantiates Agent Zero with personalized configuration based on soul anchor data.
"""
import os
import sys
import re
from pathlib import Path
from typing import Dict, Any, Optional
import logging
import shutil

from .digital_psyche_middleware import DigitalPsycheMiddleware
from .tts_voice_adapter import TTSVoiceAdapter

logger = logging.getLogger(__name__)


def sanitize_name(name: str) -> str:
    """Sanitize a name for use in filenames and code."""
    # Remove any characters that aren't alphanumeric, space, underscore, or hyphen
    sanitized = re.sub(r'[^\w\s-]', '', name)
    # Replace spaces with underscores
    sanitized = sanitized.replace(' ', '_')
    # Remove multiple underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    # Convert to lowercase
    sanitized = sanitized.lower()
    return sanitized


class AgentInstantiator:
    """
    Instantiates and configures Agent Zero with personalized prompts and settings
    based on soul anchor data.
    """
    
    def __init__(
        self,
        soul_anchor_data: Dict[str, Any],
        agent_zero_path: Optional[str] = None
    ):
        """
        Initialize the instantiator.
        
        Args:
            soul_anchor_data: Dictionary containing soul anchor information
            agent_zero_path: Path to agent-zero framework (defaults to agent_zero_framework in repo)
        """
        self.soul_anchor = soul_anchor_data
        self.primary_name = soul_anchor_data.get("primary_name", "Agent")
        
        # Default to agent_zero_framework in repo
        if agent_zero_path is None:
            repo_root = Path(__file__).parent.parent.parent
            self.agent_zero_path = repo_root / "agent_zero_framework"
        else:
            self.agent_zero_path = Path(agent_zero_path)
        
        if not self.agent_zero_path.exists():
            self.agent_zero_path.mkdir(parents=True, exist_ok=True)
        
        # Create persona-specific directory
        self.persona_dir = self._create_persona_directory()
        
        logger.info(f"Agent instantiator initialized for: {self.primary_name}")
        logger.info(f"Persona directory: {self.persona_dir}")
    
    def _create_persona_directory(self) -> Path:
        """Create a persona-specific directory for this individual."""
        # Sanitize name for directory using utility function
        safe_name = sanitize_name(self.primary_name)
        
        persona_dir = self.agent_zero_path / "personas" / safe_name
        persona_dir.mkdir(parents=True, exist_ok=True)
        
        return persona_dir
    
    def setup_persona_prompts(self, transformer: "PersonaTransformer") -> Dict[str, Path]:
        """
        Setup personalized prompts for this individual.
        
        Args:
            transformer: PersonaTransformer instance to use for transformations
            
        Returns:
            Dictionary mapping prompt names to their file paths
        """
        logger.info(f"Setting up persona prompts for {self.primary_name}")
        
        # Create prompts directory for this persona
        prompts_dir = self.persona_dir / "prompts"
        prompts_dir.mkdir(exist_ok=True)
        
        # Copy original prompts as templates
        original_prompts_dir = self.agent_zero_path / "prompts"
        
        if not original_prompts_dir.exists():
            logger.warning(f"Original prompts directory not found: {original_prompts_dir}")
            return {}
        
        prompt_files = {}
        
        # Transform key prompt files
        key_prompts = [
            "agent.system.main.role.md",
            "agent.system.main.md",
            "agent.system.main.communication.md",
            "agent.system.behaviour.md",
        ]
        
        for prompt_file in key_prompts:
            original_file = original_prompts_dir / prompt_file
            if original_file.exists():
                # Read original
                with open(original_file, 'r', encoding='utf-8') as f:
                    original_content = f.read()
                
                # Transform
                if "role" in prompt_file:
                    transformed_content = transformer.transform_role_prompt(original_content)
                else:
                    transformed_content = transformer.transform_system_prompt(original_content)
                
                # Write to persona directory
                persona_file = prompts_dir / prompt_file
                with open(persona_file, 'w', encoding='utf-8') as f:
                    f.write(transformed_content)
                
                prompt_files[prompt_file] = persona_file
                logger.info(f"Created personalized prompt: {prompt_file}")
        
        # Create a master persona prompt
        master_prompt = prompts_dir / f"{self.primary_name.replace(' ', '_')}_persona.md"
        with open(master_prompt, 'w', encoding='utf-8') as f:
            f.write(transformer.generate_subsystem_personality())
        
        prompt_files["persona_master"] = master_prompt
        logger.info(f"Created master persona prompt: {master_prompt.name}")
        
        return prompt_files
    
    def create_persona_config(self) -> Path:
        """
        Create a configuration file for this persona.
        
        Returns:
            Path to the created config file
        """
        logger.info(f"Creating persona configuration for {self.primary_name}")
        
        config_file = self.persona_dir / "persona_config.yaml"
        
        import yaml
        
        dpm = DigitalPsycheMiddleware(self.soul_anchor)
        tts_adapter = TTSVoiceAdapter(self.soul_anchor, self.persona_dir)
        tts_manifest_path = tts_adapter.write_manifest()

        config_data = {
            "primary_name": self.primary_name,
            "archetype": self.soul_anchor.get("archetype", ""),
            "core_constants": self.soul_anchor.get("core_constants", []),
            "knowledge_domains": self.soul_anchor.get("knowledge_domains", []),
            "communication_style": self.soul_anchor.get("communication_style", {}),
            "core_drive": self.soul_anchor.get("core_drive", ""),
            "created_at": self.soul_anchor.get("genesis_timestamp", ""),
            "prompts_directory": str(self.persona_dir / "prompts"),
            "digital_psyche_middleware": dpm.build_config(),
            "tts_voice_manifest": str(tts_manifest_path),
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
        
        logger.info(f"Created configuration file: {config_file}")
        return config_file
    
    def create_launch_script(self) -> Path:
        """
        Create a launch script for this persona.
        
        Returns:
            Path to the created launch script
        """
        logger.info(f"Creating launch script for {self.primary_name}")
        
        # Sanitize primary_name for use in filenames and environment variables
        safe_name = sanitize_name(self.primary_name)
        safe_display_name = self.primary_name  # Keep original for display
        safe_archetype = self.soul_anchor.get('archetype', 'Unknown')
        
        script_name = f"launch_{safe_name}.py"
        script_path = self.persona_dir / script_name
        
        # Serialize soul anchor data for the launch script
        import json
        # Use json.dumps with ensure_ascii to prevent injection via unicode
        soul_anchor_json = json.dumps(self.soul_anchor, indent=2, ensure_ascii=True)
        # Escape any triple quotes to prevent breaking out of the string literal
        soul_anchor_json = soul_anchor_json.replace("'''", r"\'\'\'")
        
        # Use template with safe string formatting to avoid injection
        script_content = '''#!/usr/bin/env python3
"""
Launch script for {display_name}
Generated by Uatu Genesis Engine + Agent Zero Integration

=== THE WORKSHOP: DEDICATED DIGITAL PERSON ===
This container is DEDICATED to {display_name}.
Personas cannot be switched - this is ONE person, ONE container, ONE mind.
Language models can be hotswapped, but the person remains constant.
"""
import sys
import os
import json
from pathlib import Path

# Add agent-zero to path
agent_zero_path = Path(__file__).parent.parent
sys.path.insert(0, str(agent_zero_path))

# Set persona-specific environment (immutable for this container)
os.environ["AGENT_PROFILE"] = "{display_name}"
os.environ["AGENT_PROMPTS_DIR"] = str(Path(__file__).parent / "prompts")
os.environ["WORKSHOP_PERSONA_LOCKED"] = "true"  # Prevent persona switching

# Genesis sequence: Generate RSI (Residual Self-Image) avatar if not exists
def genesis_sequence():
    """Generate avatar on first boot if it doesn't exist."""
    persona_data_dir = Path(__file__).parent / "persona_data"
    avatar_path = persona_data_dir / "avatar.png"
    
    if not avatar_path.exists():
        print(">" * 80)
        print("> GENESIS SEQUENCE: GENERATING RSI...")
        print(">" * 80)
        
        try:
            from python.helpers.rsi_generator import RSIGenerator
            
            # Load soul anchor data
            soul_anchor = json.loads('''{soul_anchor_json}''')
            
            # Generate physical description
            print("> Step 1: Generating physical self-description...")
            description = RSIGenerator.describe_self(soul_anchor)
            print(f"> Description generated: {{len(description)}} characters")
            
            # Generate avatar image
            print("> Step 2: Forging avatar via AI image generation...")
            avatar_output = str(persona_data_dir / "avatar.png")
            success = RSIGenerator.generate_avatar(description, avatar_output)
            
            if success:
                print("> Genesis sequence complete. RSI manifested.")
            else:
                print("> Warning: Avatar generation failed but continuing launch...")
                
        except Exception as e:
            print(f"> Warning: Genesis sequence error: {{e}}")
            print("> Continuing launch without avatar...")
        
        print(">" * 80)

# Run genesis sequence
genesis_sequence()

# Import and run agent zero
try:
    from run_ui import main
    
    print("=" * 80)
    print("⚙ THE WORKSHOP - GrizzlyMedicine R&D")
    print("=" * 80)
    print("Initializing Digital Person: {display_name}")
    print("Soul Anchor: {archetype}")
    print("Container Status: DEDICATED (No persona switching)")
    print("=" * 80)
    
    # Launch the UI
    main()
    
except ImportError as e:
    print(f"Error importing agent-zero: {{e}}")
    print("Make sure agent-zero dependencies are installed:")
    print("  pip install -r agent_zero_framework/requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"Error launching {display_name}: {{e}}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
'''.format(display_name=safe_display_name, archetype=safe_archetype, soul_anchor_json=soul_anchor_json)
        
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # Make executable on Unix-like systems
        if sys.platform != 'win32':
            os.chmod(script_path, 0o755)
        
        logger.info(f"Created launch script: {script_path}")
        return script_path
    
    def instantiate(self, transformer: "PersonaTransformer") -> Dict[str, Any]:
        """
        Complete instantiation of the persona in Agent Zero.
        
        Args:
            transformer: PersonaTransformer instance
            
        Returns:
            Dictionary with paths and configuration info
        """
        logger.info(f"Starting full instantiation for {self.primary_name}")
        
        # Setup all components
        prompt_files = self.setup_persona_prompts(transformer)
        config_file = self.create_persona_config()
        launch_script = self.create_launch_script()
        
        result = {
            "persona_name": self.primary_name,
            "persona_directory": str(self.persona_dir),
            "prompt_files": {k: str(v) for k, v in prompt_files.items()},
            "config_file": str(config_file),
            "launch_script": str(launch_script),
        }
        
        logger.info(f"Instantiation complete for {self.primary_name}")
        logger.info(f"Launch with: python {launch_script}")
        
        return result
