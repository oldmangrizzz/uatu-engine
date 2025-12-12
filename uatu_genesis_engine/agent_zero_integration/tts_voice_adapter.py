"""
Neutts-Air TTS voice adapter

Lightweight, optional scaffolding to describe persona-specific voice profiles
for the Neutts-Air platform. This does not vend the Neutts-Air code; it
produces a JSON/YAML friendly manifest derived from the soul anchor so a
downstream Neutts-Air deployment can synthesize a unique voice per individual.
"""
from pathlib import Path
from typing import Any, Dict, List
import json


class TTSVoiceAdapter:
    """
    Build persona-specific voice metadata for Neutts-Air.

    This is intentionally declarative; downstream systems can ingest the
    manifest to drive dataset curation, style tokens, and synthesis runs.
    """

    def __init__(self, soul_anchor_data: Dict[str, Any], output_dir: Path):
        self.anchor = {} if soul_anchor_data is None else soul_anchor_data
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _style_tokens(self) -> List[str]:
        tokens = []
        communication = self.anchor.get("communication_style", {})
        tone = communication.get("tone")
        formality = communication.get("formality")
        quirks = communication.get("quirks", [])
        if tone:
            tokens.append(f"tone:{tone}")
        if formality:
            tokens.append(f"formality:{formality}")
        tokens.extend([f"quirk:{q}" for q in quirks])
        return tokens

    def _lexical_seeds(self) -> List[str]:
        seeds = []
        constants = self.anchor.get("core_constants", [])
        domains = self.anchor.get("knowledge_domains", [])
        for c in constants:
            seeds.append(str(c))
        for d in domains:
            if isinstance(d, dict):
                cat = d.get("category")
                equiv = d.get("earth_1218_equivalent")
                if cat:
                    seeds.append(f"domain:{cat}")
                if equiv:
                    seeds.append(f"equiv:{equiv}")
        return seeds

    def build_manifest(self) -> Dict[str, Any]:
        """Return the manifest dictionary."""
        primary_name = self.anchor.get("primary_name", "persona")
        archetype = self.anchor.get("archetype", "unknown")
        return {
            "engine": "neutts-air",
            "persona": primary_name,
            "archetype": archetype,
            "style_tokens": self._style_tokens(),
            "lexical_seeds": self._lexical_seeds(),
            "memory_seed_notes": self.anchor.get("contextual_variables", []),
            "ethics_alignment": self.anchor.get("core_drive", ""),
            "dataset_instruction": "Generate synthetic utterances grounded in soul anchor constants and knowledge domains; do not clone external voices.",
        }

    def write_manifest(self) -> Path:
        """Persist manifest to disk and return its path."""
        manifest = self.build_manifest()
        path = self.output_dir / "tts_voice_manifest.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        return path
