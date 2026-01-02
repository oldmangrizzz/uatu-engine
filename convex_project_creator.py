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
import re
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
"""


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
        soul_anchor_data: Optional[Dict[str, Any]] = None,
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
            created_at=datetime.now().isoformat(),
        )

        with open(ts_project, "w", encoding="utf-8") as f:
            f.write(ts_content)

        print(f"   ✓ Created: convex_project.ts")

        # Write Convex schema
        schema_file = project_dir / "convex_schema.ts"
        with open(schema_file, "w", encoding="utf-8") as f:
            f.write(
                CONVEX_SCHEMA_DEPLOYMENT.format(project_name_safe=persona_name_safe)
            )

        print(f"   ✓ Created: convex_schema.ts")

        # Create package.json
        package_json = {
            "name": f"{persona_name_safe}-convex",
            "version": "1.0.0",
            "description": f"Digital person memory backend for {persona_name}",
            "scripts": {"dev": "convex dev", "deploy": "npx convex deploy"},
            "dependencies": {"convex": "^0.17.0", "convex-cli": "^0.17.0"},
        }

        with open(project_dir / "package.json", "w", encoding="utf-8") as f:
            json.dump(package_json, f, indent=2)

        print(f"   ✓ Created: package.json")

        # Copy soul anchor if provided
        if soul_anchor_data:
            anchor_file = project_dir / "soul_anchor.json"
            with open(anchor_file, "w", encoding="utf-8") as f:
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

        with open(project_dir / "README.md", "w", encoding="utf-8") as f:
            f.write(readme_content)

        print(f"   ✓ Created: README.md")

        return {
            "persona_name": persona_name,
            "project_dir": str(project_dir),
            "project_name_safe": persona_name_safe,
            "ts_project": str(ts_project),
            "schema_file": str(schema_file),
        }

    def deploy_project(
        self, project_dir: str, deploy_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Deploy Convex project and return the deployment URL.

        Runs npm install + npx convex deploy in the project directory.
        Requires CONVEX_DEPLOY_KEY environment variable for non-interactive deployment.

        Args:
            project_dir: Path to the Convex project directory
            deploy_key: Optional Convex deploy key (falls back to CONVEX_DEPLOY_KEY env var)

        Returns:
            Dictionary with deployment results:
            {
                "deployed": bool,
                "convex_url": str or None,
                "convex_admin_key": str or None,
                "error": str or None
            }
        """
        project_path = Path(project_dir)
        if not project_path.exists():
            return {
                "deployed": False,
                "convex_url": None,
                "convex_admin_key": None,
                "error": f"Project directory not found: {project_dir}",
            }

        # Get deploy key from argument or environment
        convex_deploy_key = deploy_key or os.environ.get("CONVEX_DEPLOY_KEY")

        print(f"🚀 Deploying Convex project: {project_path.name}")

        # Step 1: npm install
        print("   📦 Installing dependencies (npm install)...")
        try:
            npm_result = subprocess.run(
                ["npm", "install"],
                cwd=str(project_path),
                capture_output=True,
                text=True,
                timeout=120,  # 2 minute timeout for npm install
            )

            if npm_result.returncode != 0:
                print(f"   ❌ npm install failed: {npm_result.stderr}")
                return {
                    "deployed": False,
                    "convex_url": None,
                    "convex_admin_key": None,
                    "error": f"npm install failed: {npm_result.stderr}",
                }

            print("   ✓ Dependencies installed")

        except subprocess.TimeoutExpired:
            return {
                "deployed": False,
                "convex_url": None,
                "convex_admin_key": None,
                "error": "npm install timed out after 120 seconds",
            }
        except FileNotFoundError:
            return {
                "deployed": False,
                "convex_url": None,
                "convex_admin_key": None,
                "error": "npm not found. Please install Node.js/npm.",
            }

        # Step 2: npx convex deploy
        print("   🌐 Deploying to Convex cloud...")

        # Build deploy command
        deploy_cmd = ["npx", "convex", "deploy", "--cmd", "echo"]

        # Set up environment with deploy key if available
        deploy_env = os.environ.copy()
        if convex_deploy_key:
            deploy_env["CONVEX_DEPLOY_KEY"] = convex_deploy_key

        try:
            deploy_result = subprocess.run(
                deploy_cmd,
                cwd=str(project_path),
                capture_output=True,
                text=True,
                timeout=180,  # 3 minute timeout for deployment
                env=deploy_env,
            )

            # Parse output for URL
            output = deploy_result.stdout + deploy_result.stderr
            convex_url = None
            convex_admin_key = None

            # Look for the deployment URL in output
            # Convex typically outputs something like:
            # "Deployed to https://xxx-xxx-xxx.convex.cloud"
            # or "Convex URL: https://xxx.convex.cloud"
            for line in output.split("\n"):
                line_lower = line.lower()
                if "convex.cloud" in line_lower or "convex.site" in line_lower:
                    # Extract URL from line
                    url_match = re.search(
                        r"https://[^\s]+\.convex\.(cloud|site)[^\s]*", line
                    )
                    if url_match:
                        convex_url = url_match.group(0).rstrip(".,;:")
                        break

                # Also look for admin key if present
                if "admin_key" in line_lower or "deploy_key" in line_lower:
                    key_match = re.search(r"[a-zA-Z0-9_-]{32,}", line)
                    if key_match:
                        convex_admin_key = key_match.group(0)

            if deploy_result.returncode != 0:
                # Check if it's an auth error
                if "auth" in output.lower() or "login" in output.lower():
                    return {
                        "deployed": False,
                        "convex_url": None,
                        "convex_admin_key": None,
                        "error": "Convex authentication required. Set CONVEX_DEPLOY_KEY or run 'npx convex login' first.",
                        "output": output,
                    }
                return {
                    "deployed": False,
                    "convex_url": convex_url,  # May have captured URL even if deploy failed
                    "convex_admin_key": convex_admin_key,
                    "error": f"Convex deploy failed: {deploy_result.stderr}",
                    "output": output,
                }

            if convex_url:
                print(f"   ✓ Deployed to: {convex_url}")
            else:
                # Even if no URL found, deployment may have succeeded
                print("   ⚠ Deployed but URL not captured from output")
                print(f"   Output: {output[:500]}")

            return {
                "deployed": True,
                "convex_url": convex_url,
                "convex_admin_key": convex_admin_key,
                "error": None,
                "output": output,
            }

        except subprocess.TimeoutExpired:
            return {
                "deployed": False,
                "convex_url": None,
                "convex_admin_key": None,
                "error": "Convex deploy timed out after 180 seconds",
            }
        except FileNotFoundError:
            return {
                "deployed": False,
                "convex_url": None,
                "convex_admin_key": None,
                "error": "npx not found. Please install Node.js/npm.",
            }

    def create_and_deploy(
        self,
        persona_name: str,
        persona_name_safe: str,
        soul_anchor_data: Optional[Dict[str, Any]] = None,
        deploy_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create AND deploy a Convex project in one operation.

        This is the primary method for genesis sequence integration.
        Creates the project files, runs npm install, and deploys to Convex cloud.

        Args:
            persona_name: Display name (e.g., "Tony Stark")
            persona_name_safe: Safe identifier (e.g., "tony_stark")
            soul_anchor_data: Optional soul anchor data to include
            deploy_key: Optional Convex deploy key

        Returns:
            Dictionary with combined creation and deployment results
        """
        # Step 1: Create the project
        create_result = self.create_project(
            persona_name=persona_name,
            persona_name_safe=persona_name_safe,
            soul_anchor_data=soul_anchor_data,
        )

        # Step 2: Deploy it
        deploy_result = self.deploy_project(
            project_dir=create_result["project_dir"], deploy_key=deploy_key
        )

        # Combine results
        return {**create_result, **deploy_result}


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Create individual Convex projects for digital persons",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("persona_name", help='Persona name (e.g., "Tony Stark")')
    parser.add_argument("--persona-file", help="Path to soul anchor YAML file")
    parser.add_argument(
        "--from-lock", action="store_true", help="Use currently locked persona"
    )

    args = parser.parse_args()

    creator = ConvexProjectCreator()

    if args.from_lock:
        lock_file = Path.home() / ".uatu" / "persona.lock"
        if lock_file.exists():
            with open(lock_file, "r", encoding="utf-8") as f:
                lock_data = json.load(f)
            persona_name = lock_data.get("persona", "Unknown")

            # Load soul anchor
            persona_dir = (
                Path.cwd()
                / "agent_zero_framework"
                / "personas"
                / persona_name.lower().replace(" ", "_")
            )
            soul_anchor_file = persona_dir / "persona_config.yaml"

            if soul_anchor_file.exists():
                import yaml

                with open(soul_anchor_file, "r", encoding="utf-8") as f:
                    soul_anchor = yaml.safe_load(f)

                result = creator.create_project(
                    persona_name=persona_name,
                    persona_name_safe=persona_name.lower().replace(" ", "_"),
                    soul_anchor_data=soul_anchor,
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

            with open(args.persona_file, "r", encoding="utf-8") as f:
                soul_anchor_data = yaml.safe_load(f)

        result = creator.create_project(
            persona_name=persona_name,
            persona_name_safe=persona_name_safe,
            soul_anchor_data=soul_anchor_data,
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
