#!/usr/bin/env python3
"""Sign an admin override payload using an ECDSA P-256 private key (PEM).

Usage examples:

# Sign a payload file (passphrase will be prompted if key is encrypted):
python scripts/sign_override.py --private-key ./emergence_gate/private_key.pem --payload-file ./payload.json

# Inline payload:
python scripts/sign_override.py --private-key ./emergence_gate/private_key.pem --payload '{"action":"override_edit","fields":["primary_name"],"exp":1700000000}'
"""
from __future__ import annotations

import argparse
import base64
from getpass import getpass
from pathlib import Path
from typing import Optional

try:
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.serialization import load_pem_private_key
except Exception as exc:  # pragma: no cover - runtime environment may vary
    raise RuntimeError("cryptography library is required for signing override payloads") from exc


def sign_payload(private_key_path: str, passphrase: Optional[str], payload_json: str) -> str:
    """Sign payload_json (string) using private key at private_key_path. Returns base64 signature."""
    pk_path = Path(private_key_path)
    if not pk_path.exists():
        raise FileNotFoundError(f"Private key not found: {private_key_path}")

    data = payload_json.encode("utf-8")
    with open(pk_path, "rb") as f:
        pem = f.read()

    password = passphrase.encode("utf-8") if passphrase is not None else None
    priv = load_pem_private_key(pem, password=password)

    # Ensure key type is ECDSA-capable
    from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey
    if not isinstance(priv, EllipticCurvePrivateKey):
        raise TypeError("Private key is not elliptic curve key suitable for ECDSA signing")

    sig = priv.sign(data, ec.ECDSA(hashes.SHA256()))
    return base64.b64encode(sig).decode("ascii")


def main(argv: Optional[list[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Sign admin override payloads (ECDSA P-256)")
    p.add_argument("--private-key", "-k", required=True, help="Path to private key PEM file")
    p.add_argument("--passphrase", "-p", help="Passphrase for encrypted private key (optional). If omitted, you will be prompted if needed.")
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--payload-file", "-f", help="Path to JSON payload file")
    group.add_argument("--payload", "-j", help="Inline JSON payload string")
    p.add_argument("--out", "-o", help="Write signature to file (otherwise printed to stdout)")

    args = p.parse_args(argv)

    if args.payload_file:
        payload_json = Path(args.payload_file).read_text(encoding="utf-8")
    else:
        payload_json = args.payload

    passphrase = args.passphrase
    if passphrase is None:
        # We do not require passphrase; but try to sign and if key is encrypted, load_pem_private_key will raise TypeError
        try:
            sig = sign_payload(args.private_key, None, payload_json)
        except TypeError:
            # key likely encrypted
            passphrase = getpass("Private key passphrase: ")
            sig = sign_payload(args.private_key, passphrase, payload_json)
    else:
        sig = sign_payload(args.private_key, passphrase, payload_json)

    if args.out:
        Path(args.out).write_text(sig, encoding="utf-8")
        print(f"Signature written to {args.out}")
    else:
        print(sig)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())