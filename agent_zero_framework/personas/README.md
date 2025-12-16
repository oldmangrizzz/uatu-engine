# Personas Directory

This directory is intentionally empty in the base system.

## Purpose

This is the **output directory** where the Uatu Genesis Engine will place newly generated digital personas. The system is designed to be 100% agnostic and sterile - no pre-engineered personalities are included.

## How It Works

When you run the Uatu Engine to generate a new digital person:

```bash
python main.py "Subject Name" --export
```

The engine will:
1. Generate a complete soul anchor profile
2. Create persona-specific prompts and configuration
3. Output a dedicated launch script
4. Place everything in `personas/[subject_name]/`

## Structure

Each generated persona will have:

```
personas/
└── [subject_name]/
    ├── launch_[subject_name].py      # Dedicated launch script with secure boot
    ├── persona_config.yaml            # Configuration and metadata
    ├── tts_voice_manifest.json        # Voice settings
    ├── prompts/                       # Persona-specific prompts
    │   ├── [Subject_Name]_persona.md  # Core identity
    │   ├── agent.system.main.md       # System prompt
    │   ├── agent.system.main.role.md  # Role definition
    │   ├── agent.system.main.communication.md  # Communication style
    │   └── agent.system.behaviour.md  # Behavioral traits
    └── persona_data/                  # Runtime data (avatars, etc.)
```

## Important

**No personas are pre-generated or hard-coded.** This ensures:
- Complete neutrality and flexibility
- No bias toward specific characters
- Clean slate for any subject matter
- Professional presentation for public deployment

Characters can be described in documentation examples, but they only become "real" when the Uatu Engine generates them.
