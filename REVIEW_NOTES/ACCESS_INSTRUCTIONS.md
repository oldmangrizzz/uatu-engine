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
- Audit logs:
  - edit_rejection and edit_override events are recorded in emergence_gate/events.jsonl
  - override verification attempts are logged to emergence_gate/override_verification.jsonl
  - Convex local backups include security_event entries when Convex is enabled
