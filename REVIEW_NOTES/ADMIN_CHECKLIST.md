Admin & Counsel Checklist — Emergence Gate & Admin Overrides

Purpose
- One-page checklist for counsel and administrators covering secure handling of Emergence Gate keys, override procedures, and audit review.

Checklist

1) Key Management
- Generate ECDSA P-256 keypair using Emergence Gate CLI or accepted CSPRNG tool.
- Always store private key encrypted with a strong passphrase; avoid storing passphrases in source control or plaintext files.
- Use hardware security modules (HSM) or secure key storage for production if available.
- Maintain an access log for passphrase disclosures; only disclose passphrases out-of-band to authorized counsel/owner.
- Periodically rotate keys (e.g., annually) and publish new public_key.pem to personas; maintain transition logs and backups.

2) Admin Override Policy
- Override payloads must be JSON with fields: action ("override_edit"), fields (list or ["*"]), exp (epoch seconds), optional meta.
- Overrides MUST be signed with the private key; signatures are base64 encoded ECDSA DER.
- Time-limited overrides: always include exp and enforce expiry in verification.
- Require two-party confirmation for wildcard overrides in production (e.g., counsel + owner).

3) Audit and Monitoring
- All rejected edits (edit_rejection) and overrides (edit_override) are logged in emergence_gate/events.jsonl and to Convex (if configured).
- Verify that override_verification.jsonl contains both successful and failed verification attempts for forensic analysis.
- Periodically (e.g., weekly) review logs for unusual patterns (failed overrides, repeated rejections, unexpected admin activity).
- Maintain off-site, tamper-evident backups of events.jsonl and Convex exports for legal/counsel review.

4) Incident Response & Graceful Shutdown
- If persona exhibits anomalous behavior (diagnostics indicate corruption), apply TALK_ONLY to limit identity edits and preserve data.
- If damage or unexpected behavior persists, use GRACEFUL_SHUTDOWN trigger to run shutdown callbacks and preserve append-only logs.
- Prepare an incident report including all events.jsonl entries, Convex logs, and any relevant persona configs.

5) Legal & Policy
- Coordinate any override policy with counsel; document who is authorized to sign and use overrides.
- Keep forensic and audit logs for minimum retention period required by counsel/company policy.
- For labeled or restricted personas (sensitive public figures), escalate override requests to a higher review threshold.

6) Example Commands
- Generate key:
  python -m uatu_genesis_engine.agent_zero_integration.cli_emergence gen-key --storage-dir ./emergence --passphrase 'p'
- Sign override using CLI:
  python -m uatu_genesis_engine.agent_zero_integration.cli_emergence sign-override --payload-file ./payload.json --passphrase 'p' --storage-dir ./emergence
- Sign override using helper:
  python scripts/sign_override.py -k ./emergence/private_key.pem -f ./payload.json

7) Contact & Escalation
- Provide counsel contact info here (out-of-band)
- Provide owner/admin contact info here (out-of-band)

Notes
- Never commit private key material or passphrases to the repo. Keep encrypted backups off-repo.
- Adjust rotation, retention, and access policies per counsel recommendation and local regulations.
