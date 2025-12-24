import json

import pytest

from uatu_genesis_engine.agent_zero_integration.emergence_gate import (
    EmergenceGate,
    GateState,
    TALK_ONLY_PHRASE,
)
from uatu_genesis_engine.agent_zero_integration.convex_state_logger import ConvexStateLogger


@pytest.mark.asyncio
async def test_convex_logging_on_state_change(tmp_path):
    convex_backup = tmp_path / "convex_backups"
    convex_backup.mkdir()

    # Convex logger in mock mode with immediate flush
    convex_logger = ConvexStateLogger(
        convex_url=None,
        api_key=None,
        batch_size=1,
        flush_interval=0.1,
        enable_local_backup=True,
        local_backup_path=str(convex_backup),
    )

    await convex_logger.start()

    gate_dir = tmp_path / "gate"
    gate = EmergenceGate(storage_dir=str(gate_dir), convex_logger=convex_logger)
    gate.generate_key(passphrase=b"p")

    # Sign trigger and apply it
    gate.sign_trigger_with_private_key(TALK_ONLY_PHRASE, GateState.TALK_ONLY, passphrase=b"p")
    applied = gate.apply_trigger_phrase(TALK_ONLY_PHRASE)
    assert applied is True

    # Ensure local event log contains transition
    assert gate.events_log.exists()
    lines = list(open(gate.events_log, 'r', encoding='utf-8'))
    assert any('TALK_ONLY' in l or 'state_transition' in l for l in lines)

    # Flush convex logs and check for backups
    await convex_logger.flush()
    # There should be at least one backup file
    backups = list(convex_backup.glob('state_log_*.json'))
    assert len(backups) >= 1

    # Ensure the backup contains emergence_gate or state_transition entries
    found = False
    for b in backups:
        data = json.loads(b.read_text(encoding='utf-8'))
        if any('emergence_gate' in e.get('entry_type', '') or e.get('entry_type') == 'security_event' for e in data.get('entries', [])):
            found = True
            break
    assert found

    await convex_logger.stop()
