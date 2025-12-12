"""
Agent Instantiator

Instantiates Agent Zero with personalized configuration based on soul anchor data.
"""
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import logging
import shutil

logger = logging.getLogger(__name__)


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
            raise FileNotFoundError(
                f"Agent Zero framework not found at: {self.agent_zero_path}"
            )
        
        # Create persona-specific directory
        self.persona_dir = self._create_persona_directory()
        
        logger.info(f"Agent instantiator initialized for: {self.primary_name}")
        logger.info(f"Persona directory: {self.persona_dir}")
    
    def _create_persona_directory(self) -> Path:
        """Create a persona-specific directory for this individual."""
        # Sanitize name for directory
        safe_name = self.primary_name.replace(" ", "_").lower()
        safe_name = "".join(c for c in safe_name if c.isalnum() or c == "_")
        
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
        
        config_data = {
            "primary_name": self.primary_name,
            "archetype": self.soul_anchor.get("archetype", ""),
            "core_constants": self.soul_anchor.get("core_constants", []),
            "knowledge_domains": self.soul_anchor.get("knowledge_domains", []),
            "communication_style": self.soul_anchor.get("communication_style", {}),
            "core_drive": self.soul_anchor.get("core_drive", ""),
            "created_at": self.soul_anchor.get("genesis_timestamp", ""),
            "prompts_directory": str(self.persona_dir / "prompts"),
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
        
        script_name = f"launch_{self.primary_name.replace(' ', '_').lower()}.py"
        script_path = self.persona_dir / script_name
        
        script_content = f'''#!/usr/bin/env python3
"""
Launch script for {self.primary_name}
Generated by Uatu Genesis Engine + Agent Zero Integration
"""
import sys
import os
from pathlib import Path

# Add agent-zero to path
agent_zero_path = Path(__file__).parent.parent
sys.path.insert(0, str(agent_zero_path))

# Set persona-specific environment
os.environ["AGENT_PROFILE"] = "{self.primary_name}"
os.environ["AGENT_PROMPTS_DIR"] = str(Path(__file__).parent / "prompts")

# Import and run agent zero
try:
    from run_ui import main
    
    print("=" * 80)
    print(f"Initializing {self.primary_name}...")
    print(f"Soul Anchor Loaded: {self.soul_anchor.get('archetype', 'Unknown')}")
    print("=" * 80)
    
    # Launch the UI
    main()
    
except ImportError as e:
    print(f"Error importing agent-zero: {{e}}")
    print("Make sure agent-zero dependencies are installed:")
    print("  pip install -r agent_zero_framework/requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"Error launching {self.primary_name}: {{e}}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
'''
        
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
