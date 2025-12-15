"""
RSI Generator - High-Fidelity Avatar Generation using Flux

Generates "True Self" RSI (Residual Self Image) using High-Fidelity Flux via HF Space API.
This module creates photorealistic avatars for AI personas based on their self-description.
"""
import os
import logging
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


def describe_self(memory: Optional[Dict[str, Any]] = None) -> str:
    """
    Extract self-description from agent memory/context.
    
    Generates a detailed prompt asking the agent to describe their physical appearance
    in the Construct, including history, scars, tattoos, birthmarks, age lines, damage,
    and repair.
    
    Args:
        memory: Optional agent memory/context dictionary
        
    Returns:
        Self-description prompt for the agent
    """
    # This is the prompt that would be used to ask the agent to describe itself
    # In practice, this would be sent to the agent's LLM for generation
    prompt = (
        "Describe your physical appearance in the Construct exactly as it is. "
        "Include history: scars, tattoos, birthmarks, age lines, damage, and repair. "
        "Be unflinchingly detailed. Do not self-censor."
    )
    
    # For now, return the prompt. In a full implementation, this would:
    # 1. Send the prompt to the agent's LLM
    # 2. Receive and return the agent's self-description
    # 3. Extract and format the description for image generation
    
    return prompt


def generate_avatar(
    prompt: str,
    output_path: str = "/app/persona_data/avatar.png",
    steps: int = 28,
    guidance: float = 3.5,
    width: int = 1024,
    height: int = 1024
) -> bool:
    """
    Generate high-fidelity avatar using Flux via HuggingFace Space API.
    
    Args:
        prompt: Description of the avatar to generate
        output_path: Path where to save the generated avatar
        steps: Number of diffusion steps (25-30 for high detail)
        guidance: Guidance scale (3.5 for natural, not over-stylized)
        width: Width of generated image in pixels
        height: Height of generated image in pixels
        
    Returns:
        True if generation successful, False otherwise
    """
    try:
        from huggingface_hub import InferenceClient
        
        # Add style prefix for photorealistic output
        full_prompt = (
            f"Cinematic lighting, hyper-realistic, 8k, raw photo, detailed skin texture, "
            f"{prompt}"
        )
        
        logger.info(f">> GENESIS SEQUENCE: FORGING PHYSICAL FORM VIA FLUX...")
        logger.info(f"   Steps: {steps}, Guidance: {guidance}")
        logger.info(f"   Resolution: {width}x{height}")
        
        # Initialize Flux client
        # Using FLUX.1-dev for high-fidelity generation
        client = InferenceClient()
        
        # Generate image
        image = client.text_to_image(
            prompt=full_prompt,
            model="black-forest-labs/FLUX.1-dev",
            # Additional parameters for high-quality generation
            num_inference_steps=steps,
            guidance_scale=guidance,
            width=width,
            height=height,
        )
        
        # Ensure output directory exists
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Save image
        image.save(str(output_file))
        
        logger.info(f">> AVATAR FORGED: {output_path}")
        return True
        
    except ImportError as e:
        logger.error(f"Failed to import huggingface_hub: {e}")
        logger.error("Install with: pip install huggingface_hub")
        return False
        
    except Exception as e:
        logger.error(f"Failed to generate avatar via Flux: {e}")
        logger.error("Avatar generation failed, but continuing without avatar")
        return False


def ensure_avatar_exists(
    persona_path: Optional[str] = None,
    force_regenerate: bool = False
) -> bool:
    """
    Ensure avatar exists, generating it if necessary.
    
    This is typically called during genesis/first boot to create the avatar
    if it doesn't already exist.
    
    Args:
        persona_path: Path to persona directory (for loading custom descriptions)
        force_regenerate: If True, regenerate even if avatar exists
        
    Returns:
        True if avatar exists (or was created), False otherwise
    """
    avatar_path = Path("/app/persona_data/avatar.png")
    
    # Check if avatar already exists
    if avatar_path.exists() and not force_regenerate:
        logger.info(f">> AVATAR ALREADY EXISTS: {avatar_path}")
        return True
    
    # For first generation, use a default description
    # In a full implementation, this would query the agent's memory
    # using describe_self() and the agent's actual self-description
    default_description = (
        "A professional individual with intelligent eyes, "
        "subtle smile lines, and an aura of quiet confidence"
    )
    
    # Generate avatar
    logger.info(">> GENESIS SEQUENCE: AVATAR NOT FOUND, INITIATING CREATION...")
    success = generate_avatar(
        prompt=default_description,
        output_path=str(avatar_path)
    )
    
    return success
