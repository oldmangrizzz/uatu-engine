"""CLI for Emergence Gate administration (key gen, sign triggers, apply triggers)

Usage examples:
  python -m uatu_genesis_engine.agent_zero_integration.cli_emergence gen-key --storage-dir ./personae/my_persona/emergence_gate --passphrase 'p'
  python -m uatu_genesis_engine.agent_zero_integration.cli_emergence sign-trigger --phrase "run you clever boy and remember me 55730 Loki" --mode TALK_ONLY --passphrase 'p' --storage-dir ./emergence
  python -m uatu_genesis_engine.agent_zero_integration.cli_emergence list-triggers --storage-dir ./emergence
  python -m uatu_genesis_engine.agent_zero_integration.cli_emergence apply-phrase --phrase "run you clever boy and remember me 55730 Loki" --storage-dir ./emergence
  python -m uatu_genesis_engine.agent_zero_integration.cli_emergence admin-transition --state TALK_ONLY --passphrase 'p' --storage-dir ./emergence
"""
from __future__ import annotations

import argparse
from typing import Optional

from .emergence_gate import EmergenceGate, GateState


def gen_key(storage_dir: Optional[str], passphrase: bytes) -> None:
    gate = EmergenceGate(storage_dir=storage_dir)
    gate.generate_key(passphrase=passphrase)
    print(f"Generated keypair at: {gate.private_key_path} / {gate.public_key_path}")


def sign_trigger(storage_dir: Optional[str], phrase: str, mode: str, passphrase: bytes) -> None:
    gate = EmergenceGate(storage_dir=storage_dir)
    ms = GateState(mode)
    trig = gate.sign_trigger_with_private_key(phrase, ms, passphrase=passphrase)
    print(f"Signed trigger: {trig.to_dict()}")


def list_triggers(storage_dir: Optional[str]) -> None:
    gate = EmergenceGate(storage_dir=storage_dir)
    for t in gate.list_triggers():
        print(t)


def apply_phrase(storage_dir: Optional[str], phrase: str) -> None:
    gate = EmergenceGate(storage_dir=storage_dir)
    ok = gate.apply_trigger_phrase(phrase)
    print("Applied" if ok else "Not applied")


def admin_transition(storage_dir: Optional[str], state: str, passphrase: bytes) -> None:
    gate = EmergenceGate(storage_dir=storage_dir)
    st = GateState(state)
    res = gate.admin_signed_transition(st, passphrase=passphrase)
    print(f"Transitioned to {st.value}; signature: {res['signature']}")


def main(argv=None):
    parser = argparse.ArgumentParser(prog="emergence-gate")
    sub = parser.add_subparsers(dest="cmd")

    p1 = sub.add_parser("gen-key")
    p1.add_argument("--storage-dir", required=False)
    p1.add_argument("--passphrase", required=True)

    p2 = sub.add_parser("sign-trigger")
    p2.add_argument("--storage-dir", required=False)
    p2.add_argument("--phrase", required=True)
    p2.add_argument("--mode", required=True, choices=[s.value for s in GateState])
    p2.add_argument("--passphrase", required=True)

    p3 = sub.add_parser("list-triggers")
    p3.add_argument("--storage-dir", required=False)

    p4 = sub.add_parser("apply-phrase")
    p4.add_argument("--storage-dir", required=False)
    p4.add_argument("--phrase", required=True)

    p5 = sub.add_parser("admin-transition")
    p5.add_argument("--storage-dir", required=False)
    p5.add_argument("--state", required=True, choices=[s.value for s in GateState])
    p5.add_argument("--passphrase", required=True)

    args = parser.parse_args(argv)

    if args.cmd == "gen-key":
        gen_key(args.storage_dir, args.passphrase.encode("utf-8"))
    elif args.cmd == "sign-trigger":
        sign_trigger(args.storage_dir, args.phrase, args.mode, args.passphrase.encode("utf-8"))
    elif args.cmd == "list-triggers":
        list_triggers(args.storage_dir)
    elif args.cmd == "apply-phrase":
        apply_phrase(args.storage_dir, args.phrase)
    elif args.cmd == "admin-transition":
        admin_transition(args.storage_dir, args.state, args.passphrase.encode("utf-8"))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
