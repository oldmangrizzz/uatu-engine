# Genesis Engine: Step-by-Step Walkthrough

This document orients a new teammate to the **Genesis engine**—the orchestration path that powers Lucius Fox’s multiversal history runs. Use it as a hands-on briefing so you can jump in quickly.

## Mental Model
- **Goal:** Turn a character name into a validated `CharacterProfile`, visual DAG, and optional JSON export.
- **Core runtime:** `MultiversalSwarmOrchestrator` (in `lucius_fox_swarm/orchestrator.py`) coordinates three specialized agents, compiles results into Pydantic models, and hands them to the graph generator.
- **Entry points:** CLI (`python main.py "Name"`), programmatic (`MultiversalSwarmOrchestrator()`), or demos (`demo_mock.py`, `example.py`).

## End-to-End Flow (Happy Path)
1. **Invoke**  
   - CLI parses args (character name, `--export`, `--graph`, output dir, verbosity).  
   - Programmatic usage calls `await orchestrator.gather_multiversal_history(name)`.

2. **Phase 1 – Character intel** (`CharacterInfoAgent`)  
   - Crawls key wikis (Marvel, DC, HP, Star Wars, LOTR, Wikipedia).  
   - Normalizes aliases, occupations, first appearances, multiversal IDs, and source URLs.

3. **Phase 2 – Economic history** (`EconomicHistoryAgent`)  
   - Seeds search with prior sources plus wealth-specific queries.  
   - Extracts dollar figures and business snippets into economic events + wealth estimates.

4. **Phase 3 – Knowledge domains** (`KnowledgeDomainAgent`)  
   - Reuses earlier sources + occupations to infer skills/abilities.  
   - Maps fictional categories (magic/tech/combat/etc.) to Earth-1218 equivalents with proficiency hints.

5. **Profile compilation** (`_compile_profile`)  
   - Converts raw dicts into Pydantic models (`CharacterProfile`, `MultiversalIdentity`, `KnowledgeDomain`, `EconomicEvent`).  
   - Dedupes sources and calculates a completeness score (25% each for IDs, domains, events, wealth, plus small bonuses for richer data).

6. **Outputs**  
   - **JSON export:** `export_profile()` writes `{name}_profile.json` (datetime is ISO formatted).  
   - **Graphing:** `generate_graph()` builds a DAG (NetworkX) and saves PNG + GEXF; node colors reflect role (character, universe, knowledge, economic, wealth).  
   - Console summary highlights counts, wealth, and completeness.

## Files Worth Knowing
- `main.py` — CLI wiring and console UX.
- `lucius_fox_swarm/orchestrator.py` — lifecycle + phase coordination.
- `lucius_fox_swarm/agents/*` — per-domain gatherers.
- `lucius_fox_swarm/graph/graph_generator.py` — DAG creation/visualization/export.
- `lucius_fox_swarm/models/__init__.py` — canonical data contracts.

## Running It
- **Online run (real scrape):**
  ```bash
  python main.py "Tony Stark" --export --graph --verbose
  ```
- **Offline demo (no network needed):**
  ```bash
  python demo_mock.py
  ```
  Produces a complete mocked profile + graphs for Tony Stark.

## Extending or Debugging Quickly
- Add a new data source: subclass `BaseAgent`, then wire it into the orchestrator before `_compile_profile`.
- Observe failures: enable `--verbose` to surface HTTP warnings and layout fallbacks during graphing.
- Validate models: reuse Pydantic schemas to catch shape mismatches early.
- Performance levers: adjust concurrency within agents or throttle requests when targeting rate-limited sources.

## What “Done” Looks Like Per Run
- Non-empty `CharacterProfile` with reasonable completeness.
- JSON file (if `--export`), PNG + GEXF (if graphing enabled or no `--no-graph` flag).
- Console summary shows aliases, IDs, domain count, economic event count, wealth estimate, and completeness percentage.
