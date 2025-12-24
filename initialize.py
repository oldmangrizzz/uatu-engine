"""
Minimal initialize shim for tests to create a default agent configuration without pulling heavy runtime code.
"""

def initialize_agent():
    return {"initialized": True}