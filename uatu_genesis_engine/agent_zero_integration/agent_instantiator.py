"""
Agent Instantiator

Instantiates Agent Zero with personalized configuration based on soul anchor data.
"""

from __future__ import annotations

import os
import sys
import re
from pathlib import Path
from typing import Dict, Any, Optional
import logging

from .digital_psyche_middleware import DigitalPsycheMiddleware
from .tts_voice_adapter import TTSVoiceAdapter
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .persona_transformer import PersonaTransformer

logger = logging.getLogger(__name__)


def sanitize_name(name: str) -> str:
    """Sanitize a name for use in filenames and code."""
    # Remove any characters that aren't alphanumeric, space, underscore, or hyphen
    sanitized = re.sub(r"[^\w\s-]", "", name)
    # Replace spaces with underscores
    sanitized = sanitized.replace(" ", "_")
    # Remove multiple underscores
    sanitized = re.sub(r"_+", "_", sanitized)
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
        agent_zero_path: Optional[str] = None,
        output_subdir: str = "agents",
    ):
        """
        Initialize the instantiator.

        Args:
            soul_anchor_data: Dictionary containing soul anchor information
            agent_zero_path: Path to agent-zero framework.
                Defaults to agent_zero_framework in the repository.
            output_subdir: Subdirectory to create personas in.
                Use "agents" for native Agent Zero profile integration.
                Use "personas" for standalone persona directories.
        """
        self.soul_anchor = soul_anchor_data
        self.primary_name = soul_anchor_data.get("primary_name", "Agent")
        self.output_subdir = output_subdir

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

        # Use the configured output subdirectory (default: agents for native integration)
        persona_dir = self.agent_zero_path / self.output_subdir / safe_name
        persona_dir.mkdir(parents=True, exist_ok=True)

        return persona_dir

    def setup_persona_prompts(
        self,
        transformer: "PersonaTransformer",
    ) -> Dict[str, Path]:
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
            logger.warning(
                f"Original prompts directory not found: {original_prompts_dir}"
            )
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
                with open(original_file, "r", encoding="utf-8") as f:
                    original_content = f.read()

                # Transform
                if "role" in prompt_file:
                    transformed_content = transformer.transform_role_prompt(
                        original_content
                    )
                else:
                    transformed_content = transformer.transform_system_prompt(
                        original_content
                    )

                # Write to persona directory
                persona_file = prompts_dir / prompt_file
                with open(persona_file, "w", encoding="utf-8") as f:
                    f.write(transformed_content)

                prompt_files[prompt_file] = persona_file
                logger.info(f"Created personalized prompt: {prompt_file}")

        # Create a master persona prompt
        master_filename = f"{self.primary_name.replace(' ', '_')}_persona.md"
        master_prompt = prompts_dir / master_filename
        with open(master_prompt, "w", encoding="utf-8") as f:
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

        # Add LLM model configuration if provided
        if hasattr(self, "_model_config") and self._model_config:
            config_data["llm_config"] = {
                "provider": self._model_config.get("provider", "openrouter"),
                "model": self._model_config.get("model", "anthropic/claude-3-haiku"),
                "display_name": self._model_config.get("display_name", "Default Model"),
            }

        with open(config_file, "w", encoding="utf-8") as f:
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
        safe_archetype = self.soul_anchor.get("archetype", "Unknown")

        script_name = f"launch_{safe_name}.py"
        script_path = self.persona_dir / script_name

        # Serialize soul anchor data for the launch script
        import json

        # Use json.dumps with ensure_ascii to prevent injection via unicode
        soul_anchor_json = json.dumps(self.soul_anchor, indent=2, ensure_ascii=True)
        # Escape any triple quotes to prevent breaking out of the string literal
        soul_anchor_json = soul_anchor_json.replace("'''", r"\'\'\'")

        # Build script content from a template file when available. This keeps the code
        # concise and avoids embedding a large multi-line string directly in source.
        template_path = Path(__file__).parent / "templates" / "launch_template.py.tpl"
        if template_path.exists():
            tpl = template_path.read_text(encoding="utf-8")
            script_content = (
                tpl.replace("<<DISPLAY_NAME>>", safe_display_name)
                .replace("<<SAFE_NAME>>", safe_name)
                .replace("<<ARCHETYPE>>", safe_archetype)
                .replace("<<SOUL_ANCHOR_JSON>>", repr(soul_anchor_json))
            )
        else:
            # Fallback minimal script if template missing
            script_content = (
                f'#!/usr/bin/env python3\nprint("Initializing {safe_display_name}")\n'
            )

        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script_content)

        # Make executable on Unix-like systems
        if sys.platform != "win32":
            os.chmod(script_path, 0o755)

        logger.info(f"Created launch script: {script_path}")
        return script_path

    def instantiate(
        self,
        transformer: "PersonaTransformer",
        model_config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Complete instantiation of the persona in Agent Zero.

        Args:
            transformer: PersonaTransformer instance
            model_config: Optional dictionary with LLM configuration:
                - provider: The LLM provider (e.g., "openrouter", "github_copilot")
                - model: The model ID (e.g., "anthropic/claude-3-haiku")
                - display_name: Human-readable name for the model

        Returns:
            Dictionary with paths and configuration info
        """
        logger.info(f"Starting full instantiation for {self.primary_name}")

        # Store model config for use in persona config
        self._model_config = model_config

        # Setup all components
        prompt_files = self.setup_persona_prompts(transformer)
        config_file = self.create_persona_config()
        launch_script = self.create_launch_script()

        # Generate RSI (avatar) if image generation APIs are available
        avatar_generated = False
        try:
            # Import from the agent_zero_framework helper
            import sys

            rsi_helper_path = self.agent_zero_path / "python" / "helpers"
            if str(rsi_helper_path) not in sys.path:
                sys.path.insert(0, str(rsi_helper_path))

            from rsi_generator import ensure_avatar_exists

            avatar_generated = ensure_avatar_exists(
                persona_path=str(self.persona_dir), soul_anchor_data=self.soul_anchor
            )
            if avatar_generated:
                logger.info(f">> RSI (avatar) generated for {self.primary_name}")
            else:
                logger.warning(
                    f">> RSI generation skipped for {self.primary_name} "
                    "(set HF_TOKEN or OPENAI_API_KEY to enable)"
                )
        except ImportError as e:
            logger.warning(f">> RSI generator not available: {e}")
        except Exception as e:
            logger.warning(f">> RSI generation failed (non-critical): {e}")

        result = {
            "persona_name": self.primary_name,
            "persona_directory": str(self.persona_dir),
            "prompt_files": {k: str(v) for k, v in prompt_files.items()},
            "config_file": str(config_file),
            "launch_script": str(launch_script),
            "avatar_generated": avatar_generated,
        }

        logger.info(f"Instantiation complete for {self.primary_name}")
        logger.info(f"Launch with: python {launch_script}")

        return result
