"""
Persona Customization API
Handles RSI (avatar) upload and voice manifest customization.
"""
import os
import json
from pathlib import Path
try:
    from flask import Request
except Exception:
    from typing import Any as Request  # type: ignore
from python.helpers.api import ApiHandler
import logging
from datetime import datetime, timezone
logger = logging.getLogger(__name__)


class PersonaCustomization(ApiHandler):
    """Handler for persona customization operations."""

    @classmethod
    def requires_auth(cls) -> bool:
        return False

    @classmethod
    def requires_csrf(cls) -> bool:
        return False

    @classmethod
    def get_methods(cls) -> list[str]:
        return ["POST"]

    async def process(self, input: dict, request: Request | None = None) -> dict:
        """
        Handle persona customization.

        Accepts:
        - rsi_upload: File upload for avatar image
        - rsi_mode: "generate", "upload", or "skip"
        - voice_preset: "generated", "minimal", "expressive", or "custom"
        - custom_tokens: Custom style tokens (when voice_preset="custom")

        Returns:
            Dictionary with status and updated paths.
        """
        persona_dir = os.environ.get("AGENT_PROMPTS_DIR", "")
        persona_root = Path(persona_dir).parent if persona_dir else None
        
        # Enforce Emergence Gate edits policy if present (identity-only protection under TALK_ONLY)
        # Build list of fields being edited from explicit 'fields' key and any other indicators
        fields_being_edited = []
        if isinstance(input.get("fields"), dict):
            fields_being_edited.extend(list(input.get("fields", {}).keys()))
        # infer field edits from higher-level inputs
        if "voice_preset" in input:
            fields_being_edited.append("voice_preset")
        if "rsi_mode" in input or (request and hasattr(request, "files") and "rsi_upload" in getattr(request, "files", {})):
            fields_being_edited.append("avatar")

        # Write an incoming debug record to aid diagnostics in tests
        try:
            if persona_root:
                dbg_in = persona_root / "persona_customize_incoming.jsonl"
                with open(dbg_in, "a", encoding="utf-8") as f:
                    f.write(json.dumps({"ts": datetime.now(timezone.utc).isoformat(), "input": input, "fields_being_edited": fields_being_edited}) + "\n")
        except Exception:
            logger.exception("Failed to write incoming debug record")

        # Helper to append debug lines under persona root
        def _append_persona_debug(name: str, data: dict):
            try:
                if persona_root:
                    dbg = persona_root / name
                    with open(dbg, "a", encoding="utf-8") as f:
                        f.write(json.dumps({"ts": datetime.now(timezone.utc).isoformat(), **data}) + "\n")
            except Exception:
                logger.exception("Failed to write persona debug %s", name)
        try:
            from python.helpers.emergence_check import edits_allowed_fields, get_gate_for_persona
            allowed, message, rejected = edits_allowed_fields(persona_root, fields_being_edited or None)
            override_used = False

            # If edits are not allowed, check for admin override
            if not allowed:
                gate = get_gate_for_persona(persona_root)
                override_payload_json = input.get("override_payload")
                override_signature = input.get("override_signature")
                if gate and override_payload_json and override_signature:
                    logger.debug("PersonaCustomization: attempting admin override verification")
                    parsed = gate.verify_admin_override(override_payload_json, override_signature)
                    logger.debug("PersonaCustomization: override parsed=%s", parsed)
                    # Write debug trace to persona root for easier test inspection
                    try:
                        if persona_root:
                            dbg_path = persona_root / "persona_customize_debug.jsonl"
                            with open(dbg_path, "a", encoding="utf-8") as dbg:
                                dbg.write(json.dumps({
                                    "ts": datetime.now(timezone.utc).isoformat(),
                                    "fields_being_edited": fields_being_edited,
                                    "override_payload_present": bool(override_payload_json),
                                    "override_signature_present": bool(override_signature),
                                    "parsed": parsed,
                                }) + "\n")
                    except Exception:
                        logger.exception("Failed to write persona_customize debug")

                    if parsed and parsed.get("action") == "override_edit":
                        allowed_fields = parsed.get("fields", [])
                        logger.debug("PersonaCustomization: override allowed_fields=%s", allowed_fields)
                        if "*" in allowed_fields or all(f in allowed_fields for f in (fields_being_edited or [])):
                            try:
                                gate.record_override_usage(persona_root, fields_being_edited, parsed, override_signature)
                            except Exception:
                                logger.exception("Failed to record override usage")
                            allowed = True
                            rejected = []
                            override_used = True
                if not allowed:
                    # Record rejected edit attempts for auditing
                    try:
                        if gate:
                            gate.record_edit_rejection(persona_root, rejected or [], message or "edits disabled in TALK_ONLY")
                    except Exception:
                        logger.exception("Failed to record edit rejection")
                    return {"error": message, "status": "forbidden", "rejected_fields": rejected}
        except Exception:
            # If emergence_check is unavailable, we proceed as before
            pass

        # Keep override usage flag available for downstream logic
        _override_used = override_used if 'override_used' in locals() else False

        # If edits were allowed (including via override), apply top-level 'fields' edits if present
        applied_fields = []
        if input.get("fields") and isinstance(input.get("fields"), dict):
            try:
                config_path = persona_root / "persona_config.yaml"
                # Try to read existing YAML/JSON
                try:
                    import yaml
                    if config_path.exists():
                        with open(config_path, 'r', encoding='utf-8') as cf:
                            config = yaml.safe_load(cf) or {}
                    else:
                        config = {}
                except Exception:
                    # Fallback to JSON if PyYAML not available
                    if config_path.exists():
                        with open(config_path, 'r', encoding='utf-8') as cf:
                            config = json.load(cf)
                    else:
                        config = {}

                # Apply field edits
                for k, v in input.get("fields", {}).items():
                    config[k] = v
                    applied_fields.append(k)

                # Write back using YAML if available
                try:
                    import yaml
                    with open(config_path, 'w', encoding='utf-8') as cf:
                        yaml.safe_dump(config, cf)
                except Exception:
                    with open(config_path, 'w', encoding='utf-8') as cf:
                        json.dump(config, cf, indent=2)

                # Log applied edits
                try:
                    gate = None
                    try:
                        from python.helpers.emergence_check import get_gate_for_persona
                        gate = get_gate_for_persona(persona_root)
                    except Exception:
                        gate = None
                    if gate:
                        gate._append_event_log({"type": "edit_applied", "fields": applied_fields, "persona_root": str(persona_root)})
                except Exception:
                    logger.exception("Failed to log applied edits to emergence gate")
            except Exception:
                logger.exception("Failed to apply persona field edits")

        # If edits were allowed/override_used, ensure subsequent manifest updates do not re-check and block
        edits_globally_allowed = True if (fields_being_edited or []) and (not message or message is None) else False
        if override_used:
            edits_globally_allowed = True



        if not persona_root or not persona_root.exists():
            return {"error": "Persona directory not found"}
        
        result = {"status": "success", "rsi_path": None, "voice_updated": False}
        
        # Handle RSI (Avatar) customization
        rsi_mode = input.get("rsi_mode", "skip")
        
        if rsi_mode == "upload":
            if "rsi_upload" in request.files:
                file = request.files["rsi_upload"]
                avatar_dir = persona_root / "persona_data"
                avatar_dir.mkdir(parents=True, exist_ok=True)
                avatar_path = avatar_dir / "avatar.png"
                file.save(str(avatar_path))
                result["rsi_path"] = str(avatar_path)
                result["rsi_mode"] = "upload"
        
        elif rsi_mode == "generate":
            result["rsi_mode"] = "generate"
            result["message"] = "RSI will be generated from soul anchor during launch"
        
        else:
            result["rsi_mode"] = "skip"
            result["message"] = "Using default avatar placeholder"
        
        # Handle Voice Manifest customization
        voice_preset = input.get("voice_preset", "generated")
        tts_manifest_path = persona_root / "tts_voice_manifest.json"
        
        # Validate whether the requested fields are allowed under current gate state
        # If no specific fields provided in the input, we assume whole-file update (fields=None)
        fields_being_edited = None
        if isinstance(input.get("fields"), dict):
            fields_being_edited = list(input.get("fields", {}).keys())

        # If edits are disallowed, edits_allowed_fields will return rejected fields and message
        try:
            from python.helpers.emergence_check import edits_allowed_fields, get_gate_for_persona
            allowed, message, rejected = edits_allowed_fields(persona_root, fields_being_edited)
            if not allowed:
                gate = get_gate_for_persona(persona_root)
                override_payload_json = input.get("override_payload")
                override_signature = input.get("override_signature")
                if gate and override_payload_json and override_signature:
                    parsed = gate.verify_admin_override(override_payload_json, override_signature)
                    if parsed and parsed.get("action") == "override_edit":
                        allowed_fields = parsed.get("fields", [])
                        if "*" in allowed_fields or all(f in allowed_fields for f in (fields_being_edited or [])):
                            try:
                                gate.record_override_usage(persona_root, fields_being_edited, parsed, override_signature)
                            except Exception:
                                logger.exception("Failed to record override usage")
                            allowed = True
                            rejected = []
                if not allowed:
                    # Record rejected edit attempts for auditing
                    try:
                        if gate:
                            gate.record_edit_rejection(persona_root, rejected or [], message or "edits disabled in TALK_ONLY")
                    except Exception:
                        logger.exception("Failed to record edit rejection")
                    return {"error": message, "status": "forbidden", "rejected_fields": rejected}
        except Exception:
            # if emergence_check is unavailable, we proceed as before
            pass

        if tts_manifest_path.exists():
            try:
                with open(tts_manifest_path, 'r') as f:
                    manifest = json.load(f)
                
                # Update voice preset
                if voice_preset in ["minimal", "expressive", "custom"]:
                    manifest["voice_preset"] = voice_preset
                    
                    # If custom tokens provided
                    if voice_preset == "custom" and "custom_tokens" in input:
                        manifest["style_tokens"] = [token.strip() for token in input["custom_tokens"].split(",")]
                    
                    # Update engine if it was "generated"
                    manifest["engine"] = "neutts-air"
                    
                    # Save updated manifest
                    with open(tts_manifest_path, 'w') as f:
                        json.dump(manifest, f, indent=2)
                    
                    result["voice_updated"] = True
                    result["voice_preset"] = voice_preset
                
            except Exception as e:
                result["error"] = f"Failed to update voice manifest: {str(e)}"
        
        return result
