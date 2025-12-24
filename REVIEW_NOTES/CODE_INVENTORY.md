# Code Inventory

Top-level modules and responsibilities:

- main.py: CLI entry point, pipeline orchestration
- uatu_genesis_engine/orchestrator.py: MultiversalSwarmOrchestrator - coordinates agents and compiles CharacterProfile
- uatu_genesis_engine/agents/: Agents for character info, economic history, knowledge domain
- uatu_genesis_engine/graphmert/: GraphMERT compiler for neuro-symbolic knowledge graph
- uatu_genesis_engine/agent_zero_integration/: Integration layer for Agent Zero instantiation (soul anchor loader, instantiator, digital psyche middleware, tts adapter, state logger)
- agent_zero_framework/: Modified Agent Zero runtime for persona launching and UI
- research-whitepapers/: Dozens of conceptual whitepapers and protocol documents relevant to governance, ethics, and system design
- tests/: Unit tests for core components

Notes:
- Heavy use of aiohttp and asynchronous I/O across agents
- Emphasis on one-person-per-container and immutable soul anchors
- Several components write files to disk (configs, backups, seed files) and call external HTTP services (Convex, image generation, etc.)
