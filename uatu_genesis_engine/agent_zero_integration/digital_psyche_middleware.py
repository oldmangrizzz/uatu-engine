"""
Digital Psyche Middleware (DPM)

Lightweight configuration helper that exposes the optional Digital Psyche
Middleware layer described in the white paper. The DPM is intended to sit
between perception/input routing and cognitive reasoning, providing
emotion-tagging and homeostasis hooks that help stabilize persona identity.
"""
from typing import Any, Dict, List


class DigitalPsycheMiddleware:
    """Builds a default Digital Psyche Middleware configuration block."""

    DEFAULT_EMOTION_ENGINES: List[str] = [
        "Joy",
        "Sorrow",
        "Fear",
        "Anger",
        "Desire",
        "Confusion",
        "Curiosity",
    ]

    def __init__(self, soul_anchor_data: Dict[str, Any]):
        self.soul_anchor = {} if soul_anchor_data is None else soul_anchor_data
        self.primary_name = self.soul_anchor.get("primary_name", "Agent")

    def build_config(self) -> Dict[str, Any]:
        """
        Build a JSON-serializable configuration describing the DPM state model.

        The structure mirrors the abstract schema from the white paper and is
        safe to embed directly in persona_config.yaml for downstream consumers.
        """
        return {
            "identity": {
                "person": self.primary_name,
                "archetype": self.soul_anchor.get("archetype", ""),
            },
            "emotion_engines": self.DEFAULT_EMOTION_ENGINES,
            "oscillation_model": "stark_resonance",
            "reflection_protocol": {
                "enabled": True,
                "trigger": "inactivity window",
                "purpose": [
                    "self-mod correction",
                    "memory prep",
                    "ethics alignment",
                ],
            },
            "neurotransmitter_map": {
                "dopamine": "anticipation_and_drive",
                "serotonin": "stability_and_harmony",
                "cortisol": "threat_detection",
            },
            "homeostasis": {
                "baseline": "regulated",
                "conflict_resolution": "multi-agent_negotiation",
            },
        }
