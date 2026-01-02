#!/usr/bin/env python3
"""
Launch script
"""
import sys
import os
import json
from pathlib import Path

# Set persona-specific environment
os.environ["AGENT_PROFILE"] = "Agent"
os.environ["AGENT_PROMPTS_DIR"] = str(Path(__file__).parent / "prompts")

try:
    from uatu_genesis_engine.agent_zero_integration.emergence_gate import EmergenceGate, GateState
    gate = EmergenceGate(storage_dir=str(Path(__file__).parent / "emergence_gate"))
    if gate.get_state() == GateState.TALK_ONLY:
        os.environ["WORKSHOP_TALK_ONLY"] = "true"
except Exception:
    pass

print(f"Genesis: {os.environ.get('AGENT_PROFILE')}")
