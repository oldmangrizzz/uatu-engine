"""Compatibility shim: expose agent_zero_framework/python as top-level 'python' package.

This allows existing imports like `from python.helpers import ...` to continue working.
"""
import os
from pathlib import Path

# Compute the path to agent_zero_framework/python relative to this file
HERE = Path(__file__).parent
SHIM_PATH = (HERE.parent / "agent_zero_framework" / "python").resolve()

# Insert at front of package __path__ so imports find the real package modules
__path__.insert(0, str(SHIM_PATH))
