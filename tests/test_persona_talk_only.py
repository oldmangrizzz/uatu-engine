import json
from pathlib import Path
import pytest

from uatu_genesis_engine.agent_zero_integration.emergence_gate import EmergenceGate, GateState, TALK_ONLY_PHRASE


def make_persona_dir(tmp_path: Path) -> Path:
    persona_root = tmp_path / "persona"
    persona_root.mkdir()
    prompts = persona_root / "prompts"
    prompts.mkdir()
    # create minimal persona_config.yaml
    with open(persona_root / "persona_config.yaml", "w") as f:
        f.write(json.dumps({"primary_name": "Test Persona", "archetype": "Test"}))
    return persona_root


def test_talk_only_blocks_identity_edits(tmp_path: Path):
    persona_root = make_persona_dir(tmp_path)

    # Create gate and generate key
    gate_dir = persona_root / "emergence_gate"
    gate = EmergenceGate(storage_dir=str(gate_dir))
    gate.generate_key(passphrase=b"p")

    # Sign talk_only trigger and add
    gate.sign_trigger_with_private_key(TALK_ONLY_PHRASE, GateState.TALK_ONLY, passphrase=b"p")

    # Apply trigger
    assert gate.apply_trigger_phrase(TALK_ONLY_PHRASE)
    assert gate.get_state() == GateState.TALK_ONLY

    # Attempt an identity edit via edits_allowed_fields helper
    from python.helpers.emergence_check import edits_allowed_fields

    allowed, message, rejected = edits_allowed_fields(persona_root, ["primary_name"])
    assert not allowed
    assert "primary_name" in message or "protected" in message

    # non-identity edit allowed
    allowed2, message2, rejected2 = edits_allowed_fields(persona_root, ["voice_preset"])
    assert allowed2


@pytest.mark.asyncio
async def test_persona_customize_rejection_and_audit(tmp_path: Path):
    persona_root = make_persona_dir(tmp_path)

    # Setup convex mock backup directory
    from uatu_genesis_engine.agent_zero_integration.convex_state_logger import ConvexStateLogger
    convex_backup = tmp_path / "convex_backups"
    convex_backup.mkdir()

    convex_logger = ConvexStateLogger(convex_url=None, api_key=None, batch_size=1, flush_interval=0.01, enable_local_backup=True, local_backup_path=str(convex_backup))
    await convex_logger.start()

    gate_dir = persona_root / "emergence_gate"
    gate = EmergenceGate(storage_dir=str(gate_dir), convex_logger=convex_logger)
    gate.generate_key(passphrase=b"p")
    gate.sign_trigger_with_private_key(TALK_ONLY_PHRASE, GateState.TALK_ONLY, passphrase=b"p")
    gate.apply_trigger_phrase(TALK_ONLY_PHRASE)

    # Simulate persona_customize attempt to edit primary_name
    from agent_zero_framework.python.api.persona_customize import PersonaCustomization

    # Create a minimal ApiHandler to call process without running a Flask app
    from python.helpers.api import ApiHandler
    import os

    # Set AGENT_PROMPTS_DIR so persona_customize can find the persona
    os.environ["AGENT_PROMPTS_DIR"] = str(persona_root / "prompts")

    dummy_app = None
    dummy_lock = None
    handler = PersonaCustomization(dummy_app, dummy_lock)
    input_data = {"fields": {"primary_name": "Hijacked"}}
    res = await handler.process(input_data, request=None)

    assert res.get("status") == "forbidden" or "rejected_fields" in res

    # Verify events log has edit_rejection entry
    lines = list(open(gate.events_log, 'r', encoding='utf-8'))
    assert any('edit_rejection' in l for l in lines)

    # Now test admin override (signed payload)
    payload = {"action": "override_edit", "fields": ["primary_name"], "exp": (__import__('time').time() + 60)}
    payload_json = json.dumps(payload)
    priv = gate._load_private_key(b"p")
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives import hashes
    import base64
    sig = priv.sign(payload_json.encode('utf-8'), ec.ECDSA(hashes.SHA256()))
    sig_b64 = base64.b64encode(sig).decode('ascii')

    # Sanity check: verify override directly with gate
    parsed = gate.verify_admin_override(payload_json, sig_b64)
    assert parsed is not None and parsed.get("action") == "override_edit"

    # Attempt the edit with override
    input_data2 = {"fields": {"primary_name": "HijackedAgain"}, "override_payload": payload_json, "override_signature": sig_b64}
    res2 = await handler.process(input_data2, request=None)

    # After override, the result should NOT be forbidden
    assert res2.get("status") != "forbidden"

    # Verify events log contains an edit_override entry
    lines = list(open(gate.events_log, 'r', encoding='utf-8'))
    assert any('edit_override' in l for l in lines)

    # Flush convex backup and check for edit_rejection or edit_override in backups
    await convex_logger.flush()
    backups = list(convex_backup.glob('state_log_*.json'))
    found = False
    for b in backups:
        data = json.loads(b.read_text(encoding='utf-8'))
        if any(e.get('type') in ('edit_rejection', 'edit_override') or e.get('entry_type') == 'security_event' for e in data.get('entries', [])):
            found = True
            break

    assert found
    await convex_logger.stop()

    # Verify events log has edit_rejection entry
    lines = list(open(gate.events_log, 'r', encoding='utf-8'))
    assert any('edit_rejection' in l for l in lines)

    # Flush convex backup and check for edit_rejection in backups
    await convex_logger.flush()
    backups = list(convex_backup.glob('state_log_*.json'))
    found = False
    for b in backups:
        data = json.loads(b.read_text(encoding='utf-8'))
        if any(e.get('type') == 'edit_rejection' or e.get('entry_type') == 'security_event' for e in data.get('entries', [])):
            found = True
            break

    assert found
    await convex_logger.stop()