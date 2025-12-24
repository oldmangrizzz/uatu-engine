Admin override usage

Overview
- Admins can create an override payload (JSON) and sign it with the Emergence Gate private key (ECDSA P-256).
- The payload must include the following fields:
  - action: must be "override_edit"
  - fields: list of fields to permit (e.g., ["primary_name"]), or ["*"] for wildcard
  - exp: optional expiry (epoch seconds) to limit validity
  - meta: optional free-form metadata

Example payload
{
  "action": "override_edit",
  "fields": ["primary_name"],
  "exp": 1700000000
}

How to sign
- Use scripts/sign_override.py to sign payloads. Example:

$ python scripts/sign_override.py -k ./emergence_gate/private_key.pem -f ./payload.json

- The script will prompt for the private key passphrase if the key is encrypted.
- The script outputs a base64 ECDSA signature which should be submitted with the payload as "override_signature".

API use
- The persona customization API accepts override_payload (JSON string) and override_signature (base64) alongside the requested edits.
- If the override verifies and authorizes the requested fields, the edit will be applied and recorded as an edit_override event.

Security notes
- Keep the private key encrypted on disk with a strong passphrase.
- Share the passphrase via an out-of-band secure channel only with authorized counsel or administrators.
- Overrides are auditable; the gate records both successful and failed override verifications to override_verification.jsonl in the gate storage directory.
