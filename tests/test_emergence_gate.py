import json
from pathlib import Path

import pytest

from uatu_genesis_engine.agent_zero_integration.emergence_gate import (
    EmergenceGate,
    GateState,
    TALK_ONLY_PHRASE,
    GRACEFUL_SHUTDOWN_PHRASE,
)


def test_generate_key_and_sign_triggers(tmp_path):
    storage = tmp_path / "gate"
    gate = EmergenceGate(storage_dir=str(storage))

    # generate key
    gate.generate_key(passphrase=b"testpass")
    assert gate.private_key_path.exists()
    assert gate.public_key_path.exists()

    # sign triggers
    t1 = gate.sign_trigger_with_private_key(TALK_ONLY_PHRASE, GateState.TALK_ONLY, passphrase=b"testpass")
    t2 = gate.sign_trigger_with_private_key(GRACEFUL_SHUTDOWN_PHRASE, GateState.GRACEFUL_SHUTDOWN, passphrase=b"testpass")

    triggers = gate.list_triggers()
    assert len(triggers) == 2
    assert triggers[0]["phrase"] == TALK_ONLY_PHRASE
    assert triggers[1]["phrase"] == GRACEFUL_SHUTDOWN_PHRASE


def test_apply_trigger_and_shutdown(tmp_path):
    storage = tmp_path / "gate2"
    gate = EmergenceGate(storage_dir=str(storage))
    gate.generate_key(passphrase=b"pass")
    gate.sign_trigger_with_private_key(TALK_ONLY_PHRASE, GateState.TALK_ONLY, passphrase=b"pass")
    gate.sign_trigger_with_private_key(GRACEFUL_SHUTDOWN_PHRASE, GateState.GRACEFUL_SHUTDOWN, passphrase=b"pass")

    # cannot graceful shutdown from EMERGENT
    assert gate.get_state() == GateState.EMERGENT
    assert gate.apply_trigger_phrase(GRACEFUL_SHUTDOWN_PHRASE) is False

    # apply talk only
    assert gate.apply_trigger_phrase(TALK_ONLY_PHRASE) is True
    assert gate.get_state() == GateState.TALK_ONLY

    # register shutdown callback
    called = {"ok": False}

    def cb():
        called["ok"] = True

    gate.register_shutdown_callback(cb)

    # apply graceful shutdown
    assert gate.apply_trigger_phrase(GRACEFUL_SHUTDOWN_PHRASE) is True
    assert gate.get_state() == GateState.GRACEFUL_SHUTDOWN
    assert called["ok"] is True

    # events log created and contains entries
    lines = list(open(gate.events_log, "r", encoding="utf-8"))
    assert len(lines) >= 1
    rec = json.loads(lines[-1])
    assert rec["event"]["new_state"] == GateState.GRACEFUL_SHUTDOWN.value


def test_admin_signed_transition_and_status(tmp_path):
    storage = tmp_path / "gate3"
    gate = EmergenceGate(storage_dir=str(storage))
    gate.generate_key(passphrase=b"p")

    res = gate.admin_signed_transition(GateState.TALK_ONLY, passphrase=b"p")
    assert "signature" in res and "payload" in res
    assert gate.get_state() == GateState.TALK_ONLY

    # status returns expected fields
    st = gate.status()
    assert st["state"] == GateState.TALK_ONLY.value
    assert st["triggers_count"] == 0
    assert Path(st["events_log"]).exists()


def test_wrong_passphrase_raises(tmp_path):
    storage = tmp_path / "gate4"
    gate = EmergenceGate(storage_dir=str(storage))
    gate.generate_key(passphrase=b"abc")
    with pytest.raises(Exception):
        gate.sign_trigger_with_private_key("x", GateState.TALK_ONLY, passphrase=b"wrong")
