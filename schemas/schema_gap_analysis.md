# ============================================================================
# UATU GENESIS ENGINE - SCHEMA GAP ANALYSIS & FIELD MAPPING
# ============================================================================
# 
# This document maps three schemas:
#   1. CANONICAL SCHEMA (soul_anchor_schema.yaml) - what we WANT
#   2. PERSONA_TRANSFORMER (persona_transformer.py:28-33) - what it EXPECTS
#   3. ORCHESTRATOR (orchestrator.py:265-279) - what it PRODUCES
#
# ============================================================================

## PERSONA TRANSFORMER EXPECTED FIELDS (lines 28-33)

```python
self.primary_name = soul_anchor_data.get("primary_name", "Agent")
self.archetype = soul_anchor_data.get("archetype", "")
self.core_constants = soul_anchor_data.get("core_constants", [])
self.knowledge_domains = soul_anchor_data.get("knowledge_domains", [])
self.communication_style = soul_anchor_data.get("communication_style", {})
self.core_drive = soul_anchor_data.get("core_drive", "")
```

## ORCHESTRATOR CURRENT OUTPUT (lines 265-279)

```python
soul_anchor = {
    "identity": {
        "designation": profile.primary_name,      # → maps to primary_name
        "archetype": str(archetype),              # → WRONG: DomainCategory enum
        "constants": profile.constants or aliases, # → WRONG: aliases, not traits
    },
    "psychodynamics": {
        "core_drive": core_drive,                 # → HARDCODED generic string
        "paradox": paradox,                       # → HARDCODED generic string
    },
    "knowledge_graph": {
        "nodes": nodes,
        "edges": edges,
    },
}
```

## GAP ANALYSIS

| Field (Transformer) | Expected Type | Canonical Schema Field | Orchestrator Provides | GAP |
|---------------------|---------------|------------------------|----------------------|-----|
| `primary_name` | string | `primary_name` | `identity.designation` ✓ | **NESTED** - needs flatten |
| `archetype` | string (psychological) | `archetype` | `identity.archetype` (DomainCategory) | **WRONG SEMANTIC** |
| `core_constants` | List[str] (traits) | `core_constants` | `identity.constants` (aliases) | **WRONG DATA** |
| `knowledge_domains` | List[Dict\|str] | `knowledge_domains` | `knowledge_graph.nodes` (categories only) | **SPARSE** |
| `communication_style` | Dict{tone,formality} | `communication_style` | NOT PROVIDED | **MISSING** |
| `core_drive` | string (character-specific) | `core_drive` | `psychodynamics.core_drive` (hardcoded) | **HARDCODED** |

## ADDITIONAL CANONICAL FIELDS NOT CONSUMED BY TRANSFORMER

These fields are in the canonical schema but PersonaTransformer doesn't use them yet:
- `soul_anchors` (the three first-person trauma narratives)
- `purpose`
- `passion`
- `self_awareness`
- `personality_framework`
- `construct_environment`
- `operational_protocols`
- `safeguards`
- `emotional_layers`

## REQUIRED CHANGES

### Option A: Fix Orchestrator Output (Recommended)

Modify `orchestrator.py:export_soul_anchor()` to:
1. Flatten structure to match transformer expectations
2. Extract psychological archetypes (not domain categories)
3. Extract character traits (not aliases)
4. Generate character-specific core_drive and communication_style

**Problem:** Research agents don't gather this data. Need to fix agents first.

### Option B: Create Schema Adapter

Create a `SoulAnchorAdapter` that:
1. Takes Orchestrator output
2. Transforms to PersonaTransformer expected format
3. Enriches with LLM synthesis for missing fields

**Code Location:** `/uatu_genesis_engine/agent_zero_integration/soul_anchor_adapter.py`

### Option C: Hybrid - LLM Synthesis Layer

Add LLM layer between Orchestrator and PersonaTransformer that:
1. Takes sparse Orchestrator output
2. Uses character name + universe to synthesize rich soul anchor
3. Outputs canonical schema format

**Best for:** Rapid prototyping, leverages LLM training knowledge
**Risk:** No source verification, may hallucinate details

## RECOMMENDED PATH

1. **Create SoulAnchorAdapter** (Option B) as bridge
2. **Add LLM enrichment** (Option C) to fill gaps
3. **Long-term: Fix research agents** to gather narrative/psychological data

## IMPLEMENTATION ORDER

1. Create `soul_anchor_adapter.py` with schema transformation
2. Add LLM enrichment hooks for missing fields
3. Update `AgentInstantiator` to use adapter output
4. Test end-to-end with Tony Stark corpus
