from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple, List


def _get_gate_for_persona(persona_root: Path):
    try:
        from uatu_genesis_engine.agent_zero_integration.emergence_gate import EmergenceGate
    except Exception:
        return None

    gate_dir = persona_root / "emergence_gate"
    return EmergenceGate(storage_dir=str(gate_dir))


def get_gate_for_persona(persona_root: Path):
    """Public accessor for the EmergenceGate instance for a persona (or None)."""
    return _get_gate_for_persona(persona_root)


DEFAULT_IDENTITY_FIELDS = [
    "primary_name",
    "aliases",
    "constants",
    "core_constants",
    "multiversal_identities",
]


def edits_allowed_fields(persona_root: Path, fields: Optional[List[str]] = None) -> Tuple[bool, Optional[str], List[str]]:
    """Return (allowed, message, rejected_fields).

    - If no gate present: allowed True
    - If gate present and not TALK_ONLY: allowed True
    - If gate present and TALK_ONLY:
        - If fields is None: disallow all edits (legacy behavior)
        - Otherwise, disallow only identity fields (returns list of rejected fields)
    """
    gate = _get_gate_for_persona(persona_root)
    if not gate:
        return True, None, []

    try:
        state = gate.get_state()
    except Exception:
        return True, None, []

    if state.value != "TALK_ONLY":
        return True, None, []

    # In TALK_ONLY: if no specific fields provided, disallow all edits (backwards compatible)
    if not fields:
        return False, "Persona is in TALK_ONLY mode; edits are disabled.", []

    # Determine protected identity fields
    protected = set(getattr(gate, "IDENTITY_FIELDS", DEFAULT_IDENTITY_FIELDS))
    rejected = [f for f in fields if f in protected]
    if rejected:
        return False, f"Persona is in TALK_ONLY mode; protected fields cannot be edited: {rejected}", rejected

    return True, None, []


def edits_allowed(persona_root: Path) -> Tuple[bool, Optional[str]]:
    """Legacy API: Return (allowed, message)."""
    allowed, message, _ = edits_allowed_fields(persona_root, None)
    return allowed, message
