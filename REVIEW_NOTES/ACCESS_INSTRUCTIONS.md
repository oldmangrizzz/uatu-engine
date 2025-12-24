How to access the provisional package and PDF (simple steps)

Package location:
- REVIEW_NOTES/PROVISIONAL_PACKAGE_root_20251224.zip

Files included:
- PATENT_PROVISIONAL_BRIEF.md
- state_log_*.json backups (ConvexStateLogger local backups)
- emergence_gate_events.jsonl (if present)
- FILES_LIST.txt (list of files included in the snapshot)

Basic steps to access locally (Linux/macOS):
1. Open a terminal and change to the project directory:
   cd ~/uatu-engine

2. View the ZIP file:
   ls -lh REVIEW_NOTES/PROVISIONAL_PACKAGE_root_20251224.zip

3. Extract to a folder:
   unzip REVIEW_NOTES/PROVISIONAL_PACKAGE_root_20251224.zip -d ~/Downloads/uatu_provisional

4. View the brief (Markdown):
   less ~/Downloads/uatu_provisional/PATENT_PROVISIONAL_BRIEF.md

5. Convert to PDF (optional):
   - If you have pandoc installed:
       pandoc ~/Downloads/uatu_provisional/PATENT_PROVISIONAL_BRIEF.md -o ~/Downloads/uatu_provisional/PATENT_PROVISIONAL_BRIEF.pdf
   - If you don’t have pandoc, any Markdown viewer or GitHub will render it nicely.

6. If you requested redaction/encryption, I will produce a password-protected ZIP and provide the passphrase via an agreed out-of-band channel.

If you'd like, I can also prepare a short, non-technical README that explains what's in the package step by step for a first-time reviewer. Reply 'Yes' to have me create that README and optionally encrypt the package (I'll ask for your chosen passphrase or generate a secure one and show it to you interactively).

Admin override & Emergence Gate quick guide
- To sign an override payload, use scripts/sign_override.py. Example:
  - Create payload.json with {"action":"override_edit", "fields":["primary_name"], "exp": 1700000000}
  - Sign: python scripts/sign_override.py -k ./emergence_gate/private_key.pem -f payload.json
- To apply an override using the Persona Customization API, include:
  - override_payload: JSON string
  - override_signature: the base64 signature

Quick CLI & script examples
- Use the emergence CLI to sign triggers or perform admin transitions:
  - Generate key: python -m uatu_genesis_engine.agent_zero_integration.cli_emergence gen-key --storage-dir ./emergence --passphrase 'p'
  - Sign trigger: python -m uatu_genesis_engine.agent_zero_integration.cli_emergence sign-trigger --phrase "<phrase>" --mode TALK_ONLY --passphrase 'p' --storage-dir ./emergence
  - Sign an override payload (new CLI subcommand): python -m uatu_genesis_engine.agent_zero_integration.cli_emergence sign-override --payload-file ./payload.json --passphrase 'p' --storage-dir ./emergence

- Alternatively use the signing helper script:
  - Create payload.json with {"action":"override_edit","fields":["primary_name"],"exp": 1700000000}
  - Sign: python scripts/sign_override.py -k ./emergence/private_key.pem -f payload.json
  - The script will print a base64 signature to pass as override_signature with the payload

- Example persona_customize payload (HTTP API):
  {
    "fields": {"primary_name": "New Name"},
    "override_payload": "{...}",
    "override_signature": "<base64_signature>"
  }
- Audit logs:
  - edit_rejection and edit_override events are recorded in emergence_gate/events.jsonl
  - override verification attempts are logged to emergence_gate/override_verification.jsonl
  - Convex local backups include security_event entries when Convex is enabled
