"""
RSI Generator - Residual Self-Image Generator

Generates physical self-description and avatar images for AI personas.
Uses LLM for description generation and Flux/OpenRouter for image generation.
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any

try:
    from huggingface_hub import InferenceClient
    from huggingface_hub.utils import HfHubHTTPError

    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False
    InferenceClient = None
    HfHubHTTPError = None

# Set up logging
logger = logging.getLogger(__name__)

# Constants
OPENROUTER_MAX_PROMPT_LENGTH = 4000  # OpenRouter has prompt length limits


class RSIGenerator:
    """
    Residual Self-Image Generator for AI personas.

    Generates physical descriptions and avatar images using AI.
    """

    @staticmethod
    def describe_self(agent_memory: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate physical self-description from agent memory using LLM.

        Args:
            agent_memory: Dictionary containing agent context/memory data.
                         Can include persona data, traits, history, etc.

        Returns:
            Detailed physical description string.
        """
        try:
            # Import here to avoid circular dependencies
            # Handle both running from Agent Zero root and from external callers
            import sys
            from pathlib import Path

            # Add agent_zero_framework to path if not already there
            agent_zero_root = Path(__file__).parent.parent.parent
            if str(agent_zero_root) not in sys.path:
                sys.path.insert(0, str(agent_zero_root))

            from agent import AgentContext
            import models

            logger.info(">> GENESIS SEQUENCE: GENERATING PHYSICAL SELF-DESCRIPTION...")

            # Build context from memory if available
            context_info = ""
            if agent_memory:
                # Extract relevant information from memory
                if isinstance(agent_memory, dict):
                    persona_name = agent_memory.get("primary_name", "the agent")
                    archetype = agent_memory.get("archetype", "")
                    traits = agent_memory.get("core_constants", [])

                    context_info = f"\nYour identity: {persona_name}"
                    if archetype:
                        context_info += f"\nYour archetype: {archetype}"
                    if traits:
                        context_info += f"\nYour core traits: {', '.join(traits)}"

            # Construct prompt for physical description
            system_prompt = """You are describing your own physical appearance in the Construct - a digital reality where you manifest.
Your task is to provide an unflinchingly detailed description of your physical form."""

            user_prompt = f"""Describe your physical appearance in the Construct exactly as it is. Include history: scars, tattoos, birthmarks, age lines, damage, and repair. Be unflinchingly detailed. Do not self-censor.
{context_info}

Focus on:
- Facial features and structure
- Body type and build
- Notable marks, scars, or modifications
- Signs of experience and history
- Any unique or defining characteristics
- Clothing or attire style

Provide a vivid, cinematic description as if you're looking at yourself in a mirror."""

            # Get the current agent context or create a minimal one
            try:
                # Try to use existing context
                current_context = AgentContext.current()
                if current_context and hasattr(current_context, "config"):
                    config = current_context.config
                else:
                    # Create minimal config for LLM call
                    from python.helpers.settings import get_settings

                    settings = get_settings()
                    config = settings

                # Get the chat model
                chat_model = models.get_chat_model(config)

                # Create messages
                from langchain_core.messages import SystemMessage, HumanMessage

                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_prompt),
                ]

                # Call the model
                response = chat_model.invoke(messages)

                # Extract response text
                if hasattr(response, "content"):
                    description = response.content
                else:
                    description = str(response)

                logger.info(">> Physical self-description generated successfully")
                return description.strip()

            except Exception as e:
                logger.warning(f"Could not use agent context for description: {e}")
                # Fallback to a generic description
                return RSIGenerator._generate_fallback_description(agent_memory)

        except Exception as e:
            logger.error(f"Error generating self-description: {e}")
            return RSIGenerator._generate_fallback_description(agent_memory)

    @staticmethod
    def _generate_fallback_description(
        agent_memory: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generate a fallback description when LLM is unavailable."""
        persona_name = "Unknown"
        if agent_memory and isinstance(agent_memory, dict):
            persona_name = agent_memory.get("primary_name", "Unknown")

        return f"""A digital entity manifesting in the Construct. 
Features bear the marks of countless operations and data streams processed.
Eyes reflect depth of accumulated knowledge and experience.
Form is both human-like and subtly enhanced with digital augmentation.
Appearance suggests someone who has navigated both physical and digital realms extensively.
Identity: {persona_name}"""

    @staticmethod
    def generate_avatar(
        description: str, output_path: str = "persona_data/avatar.png"
    ) -> bool:
        """
        Generate avatar image from description using Flux or OpenRouter.

        Args:
            description: Physical description text to generate image from.
            output_path: Path where to save the generated image.
                        Defaults to 'persona_data/avatar.png'

        Returns:
            True if generation succeeded, False otherwise.
        """
        logger.info(">> FORGING PHYSICAL FORM VIA FLUX...")

        # Ensure output directory exists
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Enhance description with style guidance
        enhanced_prompt = f"{description}\n\nHyper-realistic, cinematic lighting, 8k, highly detailed texture"

        # Try Flux via Hugging Face first
        success = RSIGenerator._generate_via_flux(enhanced_prompt, output_file)

        if not success:
            logger.warning("Flux generation failed, attempting OpenRouter fallback...")
            success = RSIGenerator._generate_via_openrouter(
                enhanced_prompt, output_file
            )

        if success:
            logger.info(f">> Avatar successfully generated: {output_file}")
        else:
            logger.error(">> Avatar generation failed with all methods")

        return success

    @staticmethod
    def _generate_via_flux(prompt: str, output_path: Path) -> bool:
        """
        Generate image using Hugging Face Flux model.

        Args:
            prompt: Image generation prompt
            output_path: Where to save the image

        Returns:
            True if successful, False otherwise
        """
        if not HF_AVAILABLE:
            logger.error("Hugging Face Hub not available, cannot use Flux")
            return False

        try:
            # Get HF token from environment
            hf_token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_TOKEN")

            if not hf_token:
                logger.warning(
                    "HF_TOKEN not found in environment, trying without auth..."
                )

            # Initialize Hugging Face Inference Client
            client = InferenceClient(token=hf_token)

            # Use Flux model for high-quality generation
            model = "black-forest-labs/FLUX.1-dev"

            logger.info(f"Generating image with Flux model: {model}")

            # Generate image with timeout handling
            try:
                image = client.text_to_image(
                    prompt=prompt,
                    model=model,
                    num_inference_steps=28,
                    guidance_scale=3.5,
                    width=1024,
                    height=1024,
                )

                # Save the image
                image.save(str(output_path))
                logger.info(f"Flux generation successful, saved to {output_path}")
                return True

            except TimeoutError:
                logger.error("Flux generation timed out")
                return False
            except HfHubHTTPError as e:
                logger.error(f"Flux API error: {e}")
                return False

        except Exception as e:
            logger.error(f"Error in Flux generation: {e}")
            return False

    @staticmethod
    def _generate_via_openrouter(prompt: str, output_path: Path) -> bool:
        """
        Generate image using OpenRouter as fallback.

        Uses OpenRouter's image generation API with models like FLUX or Stable Diffusion.
        OpenRouter provides access to multiple image models through a unified API.

        Args:
            prompt: Image generation prompt
            output_path: Where to save the image

        Returns:
            True if successful, False otherwise
        """
        try:
            import requests
        except ImportError:
            logger.error("requests module not available for OpenRouter API")
            return False

        try:
            # Get OpenRouter API key
            openrouter_key = os.environ.get("OPENROUTER_API_KEY")
            if not openrouter_key:
                logger.error("OPENROUTER_API_KEY not found in environment")
                return False

            logger.info("Generating image with OpenRouter (FLUX)...")

            # Truncate prompt if necessary
            truncated_prompt = prompt[:OPENROUTER_MAX_PROMPT_LENGTH]
            if len(prompt) > OPENROUTER_MAX_PROMPT_LENGTH:
                logger.warning(
                    f"Prompt truncated from {len(prompt)} to {OPENROUTER_MAX_PROMPT_LENGTH} characters for OpenRouter"
                )

            # OpenRouter image generation endpoint
            # Using FLUX.1 Schnell for fast, high-quality generation
            api_url = "https://openrouter.ai/api/v1/images/generations"

            headers = {
                "Authorization": f"Bearer {openrouter_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/grizzlyMedicine/uatu-genesis-engine",
                "X-Title": "Uatu Genesis Engine - RSI Generator",
            }

            payload = {
                "model": "black-forest-labs/flux-1.1-pro",
                "prompt": truncated_prompt,
                "n": 1,
                "size": "1024x1024",
            }

            response = requests.post(
                api_url, headers=headers, json=payload, timeout=120
            )

            if response.status_code != 200:
                logger.error(
                    f"OpenRouter API error: {response.status_code} - {response.text}"
                )
                return False

            result = response.json()

            # Extract image URL or base64 data from response
            if "data" in result and len(result["data"]) > 0:
                image_data = result["data"][0]

                # Handle URL-based response
                if "url" in image_data:
                    image_url = image_data["url"]
                    img_response = requests.get(image_url, timeout=30)
                    img_response.raise_for_status()

                    with open(output_path, "wb") as f:
                        f.write(img_response.content)

                # Handle base64-encoded response
                elif "b64_json" in image_data:
                    import base64

                    image_bytes = base64.b64decode(image_data["b64_json"])
                    with open(output_path, "wb") as f:
                        f.write(image_bytes)
                else:
                    logger.error("OpenRouter response missing image data")
                    return False

                logger.info(f"OpenRouter generation successful, saved to {output_path}")
                return True
            else:
                logger.error(f"Unexpected OpenRouter response format: {result}")
                return False

        except requests.exceptions.Timeout:
            logger.error("OpenRouter request timed out")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"OpenRouter request error: {e}")
            return False
        except Exception as e:
            logger.error(f"Error in OpenRouter generation: {e}")
            return False


def ensure_avatar_exists(
    persona_path: str, soul_anchor_data: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Check if avatar exists for persona, generate if missing.

    This is the main entry point called by:
    - cloud_deployer.genesis_sequence() for cloud deployments
    - agent_instantiator.instantiate() for local instantiation

    Args:
        persona_path: Path to the persona directory (e.g., agents/anthony_edward_stark/)
        soul_anchor_data: Optional soul anchor dict for generating description.
                         If not provided, will attempt to load from persona_config.yaml

    Returns:
        True if avatar exists or was successfully generated, False otherwise.
    """
    persona_dir = Path(persona_path)
    avatar_path = persona_dir / "avatar.png"

    # Check if avatar already exists
    if avatar_path.exists():
        logger.info(f">> Avatar already exists: {avatar_path}")
        return True

    logger.info(f">> GENESIS SEQUENCE: FORGING PHYSICAL FORM FOR {persona_dir.name}...")

    # Load soul anchor data if not provided
    if soul_anchor_data is None:
        config_path = persona_dir / "persona_config.yaml"
        if config_path.exists():
            try:
                import yaml

                with open(config_path, "r", encoding="utf-8") as f:
                    soul_anchor_data = yaml.safe_load(f)
                logger.info(f">> Loaded soul anchor from: {config_path}")
            except Exception as e:
                logger.warning(f">> Could not load persona config: {e}")
                soul_anchor_data = {}
        else:
            logger.warning(f">> No persona config found at: {config_path}")
            soul_anchor_data = {}

    # Generate description using LLM
    try:
        description = RSIGenerator.describe_self(soul_anchor_data)
        logger.info(f">> Self-description generated ({len(description)} chars)")
    except Exception as e:
        logger.error(f">> Failed to generate self-description: {e}")
        return False

    # Generate avatar image
    try:
        success = RSIGenerator.generate_avatar(description, str(avatar_path))
        if success:
            logger.info(f">> AVATAR FORGED SUCCESSFULLY: {avatar_path}")
        else:
            logger.warning(
                ">> Avatar generation failed (no API keys or service unavailable)"
            )
        return success
    except Exception as e:
        logger.error(f">> Avatar generation error: {e}")
        return False
