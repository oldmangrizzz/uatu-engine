# kokoro_tts.py

import base64
import io
import json
import os
import warnings
import asyncio
import soundfile as sf
from pathlib import Path
from python.helpers.print_style import PrintStyle
from python.helpers.notification import (
    NotificationManager,
    NotificationType,
    NotificationPriority,
)

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

_pipeline = None
_default_voice = "am_puck,am_onyx"
_voice = _default_voice  # Will be overridden by persona manifest if available
_speed = 1.1
is_updating_model = False

# Voice mapping based on persona characteristics
# Kokoro voices: am_* = American male, af_* = American female, bf_* = British female, etc.
VOICE_MAPPINGS = {
    # Archetype-based mappings
    "sardonic": "am_onyx",
    "confident": "am_puck",
    "authoritative": "am_onyx",
    "playful": "am_puck",
    "serious": "am_onyx",
    "warm": "af_bella",
    "professional": "bf_emma",
    "mysterious": "af_sky",
    "calm": "af_nicole",
    # Gender hints (from persona names or explicit tags)
    "male": "am_puck,am_onyx",
    "female": "af_bella,af_sky",
}


from typing import Optional


def get_voice_for_persona(persona_path: Optional[str] = None) -> str:
    """
    Load voice settings from persona's tts_voice_manifest.json.

    Args:
        persona_path: Path to persona directory containing tts_voice_manifest.json

    Returns:
        Kokoro voice string (e.g., "am_puck,am_onyx")
    """
    global _voice

    if not persona_path:
        # Try to get from environment variable
        persona_path = os.environ.get("AGENT_PERSONA_PATH")

    if not persona_path:
        return _default_voice

    manifest_path = Path(persona_path) / "tts_voice_manifest.json"

    if not manifest_path.exists():
        PrintStyle.hint(
            f"No TTS manifest found at {manifest_path}, using default voice"
        )
        return _default_voice

    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        # Extract style tokens to determine voice characteristics
        style_tokens = manifest.get("style_tokens", [])

        # Build voice based on style tokens
        voices = set()
        for token in style_tokens:
            # Parse tokens like "tone:sardonic" or "quirk:deflects with humor"
            if ":" in token:
                _, value = token.split(":", 1)
                value = value.strip().lower()
            else:
                value = token.lower()

            # Match against our voice mappings
            for key, voice in VOICE_MAPPINGS.items():
                if key in value:
                    voices.add(voice.split(",")[0])  # Take primary voice
                    break

        if voices:
            voice_string = ",".join(sorted(voices)[:2])  # Max 2 voices for blending
            PrintStyle.standard(
                f"Loaded persona voice: {voice_string} (from {manifest_path.name})"
            )
            return voice_string

        # Fallback: check archetype for hints
        archetype = manifest.get("archetype", "").lower()
        for key, voice in VOICE_MAPPINGS.items():
            if key in archetype:
                PrintStyle.standard(f"Matched voice from archetype: {voice}")
                return voice

        PrintStyle.hint(f"No voice mapping found in manifest, using default")
        return _default_voice

    except Exception as e:
        PrintStyle.error(f"Error loading TTS manifest: {e}")
        return _default_voice


def set_persona_voice(persona_path: Optional[str] = None) -> str:
    """
    Set the global voice based on persona manifest.
    Call this during agent initialization.
    """
    global _voice
    _voice = get_voice_for_persona(persona_path)
    return _voice


async def preload():
    try:
        # return await runtime.call_development_function(_preload)
        return await _preload()
    except Exception as e:
        # if not runtime.is_development():
        raise e
        # Fallback to direct execution if RFC fails in development
        # PrintStyle.standard("RFC failed, falling back to direct execution...")
        # return await _preload()


async def _preload():
    global _pipeline, is_updating_model

    while is_updating_model:
        await asyncio.sleep(0.1)

    try:
        is_updating_model = True
        if not _pipeline:
            NotificationManager.send_notification(
                NotificationType.INFO,
                NotificationPriority.NORMAL,
                "Loading Kokoro TTS model...",
                display_time=99,
                group="kokoro-preload",
            )
            PrintStyle.standard("Loading Kokoro TTS model...")
            from kokoro import KPipeline

            _pipeline = KPipeline(lang_code="a", repo_id="hexgrad/Kokoro-82M")
            NotificationManager.send_notification(
                NotificationType.INFO,
                NotificationPriority.NORMAL,
                "Kokoro TTS model loaded.",
                display_time=2,
                group="kokoro-preload",
            )
    finally:
        is_updating_model = False


async def is_downloading():
    try:
        # return await runtime.call_development_function(_is_downloading)
        return _is_downloading()
    except Exception as e:
        # if not runtime.is_development():
        raise e
        # Fallback to direct execution if RFC fails in development
        # return _is_downloading()


def _is_downloading():
    return is_updating_model


async def is_downloaded():
    try:
        # return await runtime.call_development_function(_is_downloaded)
        return _is_downloaded()
    except Exception as e:
        # if not runtime.is_development():
        raise e
        # Fallback to direct execution if RFC fails in development
        # return _is_downloaded()


def _is_downloaded():
    return _pipeline is not None


async def synthesize_sentences(sentences: list[str]):
    """Generate audio for multiple sentences and return concatenated base64 audio"""
    try:
        # return await runtime.call_development_function(_synthesize_sentences, sentences)
        return await _synthesize_sentences(sentences)
    except Exception as e:
        # if not runtime.is_development():
        raise e
        # Fallback to direct execution if RFC fails in development
        # return await _synthesize_sentences(sentences)


async def _synthesize_sentences(sentences: list[str]):
    await _preload()

    combined_audio = []

    try:
        for sentence in sentences:
            if sentence.strip():
                segments = _pipeline(sentence.strip(), voice=_voice, speed=_speed)  # type: ignore
                segment_list = list(segments)

                for segment in segment_list:
                    audio_tensor = segment.audio
                    audio_numpy = audio_tensor.detach().cpu().numpy()  # type: ignore
                    combined_audio.extend(audio_numpy)

        # Convert combined audio to bytes
        buffer = io.BytesIO()
        sf.write(buffer, combined_audio, 24000, format="WAV")
        audio_bytes = buffer.getvalue()

        # Return base64 encoded audio
        return base64.b64encode(audio_bytes).decode("utf-8")

    except Exception as e:
        PrintStyle.error(f"Error in Kokoro TTS synthesis: {e}")
        raise
