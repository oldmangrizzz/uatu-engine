#!/usr/bin/env python3
"""
Convex Project Creator - Creates new Convex deployment for each digital person

Each digital person gets their OWN Convex project with:
- GraphMERT knowledge graph
- MemGPT hybrid memory
- Digital psyche middleware integration
- Immutable soul anchor storage

This ensures each persona has:
1. Complete memory isolation
2. Queryable knowledge base
3. Persistent identity invariants
4. Emergency backup capability
"""
import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


CONVEX_PROJECT_TEMPLATE = """// Project: {project_name}
// Type: Digital Person Memory Backend
// Created: {created_at}

import {{ GraphMERT, Convex, v0_1_0, Auth, AuthProviders }} from "convex";

const PROJECT_NAME = "{project_name_safe}";
const PROJECT_DESCRIPTION = "Digital person memory backend for {persona_name}";

export const query = (ctx, fieldPath, args) => {{
  return ctx.db.query(PROJECT_NAME)
    .from(fieldPath)
    .collect();
}};

export const mutation = {{
  updateInternalMonologue: mutation({{
    args: {{
      validation: (ctx, args) => {{
        const persona = ctx.db.query("persona_lock").first();
        return persona?.status === "locked" && 
               args.rootInvariant === true;
      }}
    }}
  }}),
  updateEmotionalState: mutation({{
    args: {{
      psyche: v.string(),
      valence: v.float(),
      arousal: v.float(),
      timestamp: v.string()
    }}
  }}),
  addMemory: mutation({{
    args: {{
      content: v.string(),
      embedding: v.optional(v.array(v.float64())),
      metadata: v.optional(v.json())
    }}
  }})
}};


CONVEX_SCHEMA_DEPLOYMENT = """[
  {{
    "name": "{project_name_safe}_minds",
    "documentFields": [
      {{
        "name": "person_name",
        "type": "string",
        "isIndexed": true
      }}
    ],
    "searchField": {{
      "vectorField": "embedding",
      "dimensions": 1536
    }}
  }},
  {{
    "name": "{project_name_safe}_facts",
    "documentFields": [
      {{
        "name": "person_name",
        "type": "string",
        "isIndexed": true
      }},
      {{
        "name": "subject",
        "type": "string",
        "isIndexed": true
      }},
      {{
        "name": "predicate",
        "type": "string",
        "isIndexed": true
      }},
      {{
        "name": "object",
        "type": "string",
        "isIndexed": true
      }},
      {{
        "name": "confidence",
        "type": "number",
        "isIndexed": false
      }},
      {{
        "name": "immutable",
        "type": "boolean",
        "isIndexed": true
      }},
      {{
        "name": "timestamp",
        "type": "string",
        "isIndexed": true
      }},
      {{
        "name": "embedding",
        "type": "vector",
        "isIndexed": true,
        "vectorDimensions": 1536
      }}
    ],
    "searchField": {{
      "vectorField": "embedding",
      "dimensions": 1536
    }}
  }},
  {{
    "name": "{project_name_safe}_monologue",
    "documentFields": [
      {{
        "name": "content",
        "type": "string"
      }},
      {{
        "name": "timestamp",
        "type": "string"
      }},
      {{
        "name": "emotion_tags",
        "type": "array"
      }},
      {{
        "name": "psyche_state",
        "type": "object"
      }}
    ]
  }},
  {{
    "name": "{project_name_safe}_psyche",
    "documentFields": [
      {{
        "name": "valence",
        "type": "number"
      }},
      {{
        "name": "arousal",
        "type": "number"
      }},
      {{
        "name": "timestamp",
        "type": "string"
      }}
    ]
  }}
]
"""


class ConvexProjectCreator:
    """Creates individual Convex projects for digital persons."""

    def __init__(self):
        self.base_dir = Path.home() / ".convex" / "uatu-persons"
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def create_project(
        self,
        persona_name: str,
        persona_name_safe: str,
        soul_anchor_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a complete Convex project for a digital person.

        Args:
            persona_name: Display name (e.g., "Tony Stark")
            persona_name_safe: Safe identifier (e.g., "tony_stark")
            soul_anchor_data: Optional soul anchor data to include

        Returns:
            Dictionary with project creation results
        """
        project_dir = self.base_dir / persona_name_safe
        project_dir.mkdir(parents=True, exist_ok=True)

        print(f"📦 Creating Convex project: {persona_name}")
        print(f"   Location: {project_dir}")

        # Create Convex TypeScript project
        ts_project = project_dir / "convex_project.ts"
        ts_content = CONVEX_PROJECT_TEMPLATE.format(
            project_name=persona_name_safe,
            persona_name=persona_name,
            project_name_safe=persona_name_safe,
            created_at=datetime.now().isoformat()
        )

        with open(ts_project, 'w', encoding='utf-8') as f:
            f.write(ts_content)

        print(f"   ✓ Created: convex_project.ts")

        # Write Convex schema
        schema_file = project_dir / "convex_schema.ts"
        with open(schema_file, 'w', encoding='utf-8') as f:
            f.write(CONVEX_SCHEMA_DEPLOYMENT.format(project_name=persona_name_safe))

        print(f"   ✓ Created: convex_schema.ts")

        # Create package.json
        package_json = {
            "name": f"{persona_name_safe}-convex",
            "version": "1.0.0",
            "description": f"Digital person memory backend for {persona_name}",
            "scripts": {
                "dev": "convex dev",
                "deploy": "npx convex deploy"
            },
            "dependencies": {
                "convex": "^0.17.0",
                "convex-cli": "^0.17.0"
            }
        }

        with open(project_dir / "package.json", 'w', encoding='utf-8') as f:
            json.dump(package_json, f, indent=2)

        print(f"   ✓ Created: package.json")

        # Copy soul anchor if provided
        if soul_anchor_data:
            anchor_file = project_dir / "soul_anchor.json"
            with open(anchor_file, 'w', encoding='utf-8') as f:
                json.dump(soul_anchor_data, f, indent=2)
            print(f"   ✓ Created: soul_anchor.json")

        # Create README
        readme_content = f"""# {persona_name} - Convex Memory Backend

Digital person memory storage powered by Convex.

## Project Structure

- `convex_project.ts` - Main Convex schema and functions
- `convex_schema.ts` - Database table definitions
- `package.json` - NPM configuration

## Deployment

```bash
# Install dependencies
npm install

# Development
npx convex dev

# Deploy to production
npx convex deploy
```

## Integration with Uatu Engine

This Convex project is automatically created when instantiating `{persona_name}`.

**Tables:**
1. **{persona_name_safe}_minds** - Persona lock and root invariants
2. **{persona_name_safe}_facts** - Knowledge graph (GraphMERT data)
3. **{persona_name_safe}_monologue** - Internal monologue (MemGPT)
4. **{persona_name_safe}_psyche** - Emotional state (Digital Psyche Middleware)

## Architecture

- **Immutable Soul Anchors** - Stored in `{persona_name_safe}_minds` table
- **Queryable Knowledge** - Vector embeddings for semantic search
- **Persistent Memory** - All conversations stored and retrievable
- **Emotional State** - Digital Psyche writes to `{persona_name_safe}_psyche`

---
Created by Uatu Engine
GrizzlyMedicine R&D - The World's First True Metaverse Research Lab
"""

        with open(project_dir / "README.md", 'w', encoding='utf-8') as f:
            f.write(readme_content)

        print(f"   ✓ Created: README.md")

        return {
            "persona_name": persona_name,
            "project_dir": str(project_dir),
            "project_name_safe": persona_name_safe,
            "ts_project": str(ts_project),
            "schema_file": str(schema_file)
        }


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Create individual Convex projects for digital persons",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('persona_name', help='Persona name (e.g., "Tony Stark")')
    parser.add_argument('--persona-file', help='Path to soul anchor YAML file')
    parser.add_argument('--from-lock', action='store_true', help='Use currently locked persona')

    args = parser.parse_args()

    creator = ConvexProjectCreator()

    if args.from_lock:
        lock_file = Path.home() / ".uatu" / "persona.lock"
        if lock_file.exists():
            with open(lock_file, 'r', encoding='utf-8') as f:
                lock_data = json.load(f)
            persona_name = lock_data.get("persona", "Unknown")

            # Load soul anchor
            persona_dir = Path.cwd() / "agent_zero_framework" / "personas" / persona_name.lower().replace(" ", "_")
            soul_anchor_file = persona_dir / "persona_config.yaml"

            if soul_anchor_file.exists():
                import yaml
                with open(soul_anchor_file, 'r', encoding='utf-8') as f:
                    soul_anchor = yaml.safe_load(f)

                result = creator.create_project(
                    persona_name=persona_name,
                    persona_name_safe=persona_name.lower().replace(" ", "_"),
                    soul_anchor_data=soul_anchor
                )
                print()
                print(f"📋 Project location: {result['project_dir']}")
                print(f"🚀 To deploy:")
                print(f"   cd {result['project_dir']}")
                print(f"   npm install")
                print(f"   npx convex deploy")
            else:
                print(f"❌ Soul anchor not found: {soul_anchor_file}")
                sys.exit(1)
        else:
            print("❌ No persona is currently locked")
            print("   Use: uatu-engine status to check")
            print("   Or: uatu-engine create <name> to make a new one")
            sys.exit(1)
    else:
        persona_name = args.persona_name
        persona_name_safe = persona_name.lower().replace(" ", "_")

        # Load soul anchor if file provided
        soul_anchor_data = None
        if args.persona_file:
            import yaml
            with open(args.persona_file, 'r', encoding='utf-8') as f:
                soul_anchor_data = yaml.safe_load(f)

        result = creator.create_project(
            persona_name=persona_name,
            persona_name_safe=persona_name_safe,
            soul_anchor_data=soul_anchor_data
        )

        print()
        print("📋 Next Steps:")
        print(f"   1. Deploy Convex project:")
        print(f"      cd {result['project_dir']}")
        print(f"      npm install")
        print(f"      npx convex deploy")
        print()
        print(f"   2. Update launch script to initialize GraphMERT memory")


if __name__ == "__main__":
    main()
