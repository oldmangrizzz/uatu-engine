"""
Emergence Gate - single-admin unlock and audit for emergent personas

Features implemented:
- Single-admin ECDSA (P-256) private key generation (passphrase-encrypted PEM)
- Trigger registration: admin pre-authorizes trigger phrases by signing them
- Phrase-based mode transitions (EMERGENT, TALK_ONLY, GRACEFUL_SHUTDOWN)
- Local append-only signed event log (JSONL) and Convex logging (via ConvexStateLogger)
- Graceful shutdown callbacks registry

Design notes:
- Triggers are authorized ahead-of-time (signed) so runtime phrase detection does not require the private key or passphrase.
- Admin can also directly invoke mode transitions via the CLI (not included here); direct transitions will be signed using the private key (requires passphrase).
"""
from __future__ import annotations

import base64
import json
import logging
import os
import secrets
import threading
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

# cryptography imports - type ignored if stubs not available
from cryptography.hazmat.primitives import hashes, serialization  # type: ignore
from cryptography.hazmat.primitives.asymmetric import ec  # type: ignore
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePublicKey  # type: ignore
from cryptography.hazmat.primitives.serialization import BestAvailableEncryption, load_pem_private_key, load_pem_public_key  # type: ignore

from typing import cast

from uatu_genesis_engine.agent_zero_integration.convex_state_logger import ConvexStateLogger

logger = logging.getLogger(__name__)


class GateState(str, Enum):
    EMERGENT = "EMERGENT"
    LOCKED = "LOCKED"
    TALK_ONLY = "TALK_ONLY"
    GRACEFUL_SHUTDOWN = "GRACEFUL_SHUTDOWN"


@dataclass
class Trigger:
    phrase: str
    mode: GateState
    created_at: str
    nonce: str
    signature: str
    pubkey_fingerprint: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "phrase": self.phrase,
            "mode": self.mode.value,
            "created_at": self.created_at,
            "nonce": self.nonce,
            "signature": self.signature,
            "pubkey_fingerprint": self.pubkey_fingerprint,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Trigger":
        return Trigger(
            phrase=d["phrase"],
            mode=GateState(d["mode"]),
            created_at=d["created_at"],
            nonce=d["nonce"],
            signature=d["signature"],
            pubkey_fingerprint=d.get("pubkey_fingerprint", ""),
        )


class EmergenceGate:
    """
    EmergenceGate manages authorized triggers and mode transitions.
    """

    def __init__(
        self,
        storage_dir: Optional[str] = None,
        convex_logger: Optional[ConvexStateLogger] = None,
        default_state: GateState = GateState.EMERGENT,
    ):
        self.storage_dir = Path(storage_dir or "./emergence_gate").expanduser()
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.private_key_path = self.storage_dir / "private_key.pem"
        self.public_key_path = self.storage_dir / "public_key.pem"
        self.triggers_path = self.storage_dir / "triggers.json"
        self.events_log = self.storage_dir / "events.jsonl"
        self._state_lock = threading.RLock()
        self._state = default_state
        self.convex_logger = convex_logger
        self._shutdown_callbacks: List[Callable[[], Any]] = []

        # State persistence file
        self.state_path = self.storage_dir / "state.json"

        # Load triggers if present
        self._triggers: List[Trigger] = []
        if self.triggers_path.exists():
            try:
                with open(self.triggers_path, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                self._triggers = [Trigger.from_dict(x) for x in raw]
            except Exception:
                logger.exception("Failed to load triggers file; starting with empty list")
                self._triggers = []

        # If a saved state file exists, load it so multiple instances observe the same gate state
        if self.state_path.exists():
            try:
                with open(self.state_path, "r", encoding="utf-8") as sf:
                    data = json.load(sf)
                state_str = data.get("state")
                if state_str:
                    try:
                        self._state = GateState(state_str)
                    except Exception:
                        logger.warning("Unknown saved gate state in state.json: %s", state_str)
            except Exception:
                logger.exception("Failed to read persisted gate state; continuing with default")

    # ------------------ Key management ------------------
    def generate_key(self, passphrase: bytes) -> None:
        """Generate a new ECDSA P-256 keypair and store it (private key encrypted with passphrase)."""
        if self.private_key_path.exists():
            raise FileExistsError(f"Private key already exists at {self.private_key_path}")

        private_key = ec.generate_private_key(ec.SECP256R1())
        pem_priv = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=BestAvailableEncryption(passphrase),
        )
        pub_key = private_key.public_key()
        pem_pub = pub_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        with open(self.private_key_path, "wb") as f:
            f.write(pem_priv)
            os.chmod(self.private_key_path, 0o600)

        with open(self.public_key_path, "wb") as f:
            f.write(pem_pub)
            os.chmod(self.public_key_path, 0o644)

        logger.info(f"Generated keypair. Public key saved at {self.public_key_path}")

    def load_public_key(self):
        if not self.public_key_path.exists():
            raise FileNotFoundError("Public key not found. Generate a key first.")
        with open(self.public_key_path, "rb") as f:
            return load_pem_public_key(f.read())

    def _load_private_key(self, passphrase: bytes):
        if not self.private_key_path.exists():
            raise FileNotFoundError("Private key not found. Generate a key first.")
        with open(self.private_key_path, "rb") as f:
            return load_pem_private_key(f.read(), password=passphrase)

    @staticmethod
    def _fingerprint_public_pem(pem: bytes) -> str:
        digest = hashes.Hash(hashes.SHA256())
        digest.update(pem)
        return digest.finalize().hex()

    # ------------------ Triggers ------------------
    def add_trigger(self, phrase: str, mode: GateState, admin_public_pem: bytes, signature: str, created_at: Optional[str] = None, nonce: Optional[str] = None) -> Trigger:
        """Add a pre-authorized trigger (admin-signed).

        If created_at and nonce are provided, they will be used (useful when the signature
        incorporates those values). Otherwise, new values will be generated.
        """
        created_at = created_at or datetime.utcnow().isoformat()
        nonce = nonce or secrets.token_hex(8)
        trig = Trigger(
            phrase=phrase,
            mode=mode,
            created_at=created_at,
            nonce=nonce,
            signature=signature,
            pubkey_fingerprint=self._fingerprint_public_pem(admin_public_pem),
        )
        self._triggers.append(trig)
        self._dump_triggers()
        logger.info(f"Added trigger for mode {mode} phrase '{phrase[:40]}...'")
        return trig

    def _dump_triggers(self) -> None:
        with open(self.triggers_path, "w", encoding="utf-8") as f:
            json.dump([t.to_dict() for t in self._triggers], f, indent=2)

    def list_triggers(self) -> List[Dict[str, Any]]:
        return [t.to_dict() for t in self._triggers]

    def _verify_trigger_signature(self, trigger: Trigger) -> bool:
        try:
            # Load public key by fingerprint
            if not self.public_key_path.exists():
                logger.warning("Public key missing; cannot verify trigger signatures")
                return False
            with open(self.public_key_path, "rb") as f:
                pem = f.read()
            if self._fingerprint_public_pem(pem) != trigger.pubkey_fingerprint:
                logger.warning("Trigger signed by unknown public key fingerprint")
                return False
            pub = load_pem_public_key(pem)
            # Only EllipticCurvePublicKey supports ECDSA verification with ECDSA(hashes.SHA256())
            if not isinstance(pub, EllipticCurvePublicKey):
                logger.warning("Unsupported public key type for signature verification")
                return False
            message = f"{trigger.phrase}|{trigger.mode.value}|{trigger.created_at}|{trigger.nonce}".encode("utf-8")
            sig = base64.b64decode(trigger.signature)
            # cryptography returns DER signature for ECDSA; we can verify directly
            pub.verify(sig, message, ec.ECDSA(hashes.SHA256()))
            return True
        except Exception:
            logger.exception("Trigger signature verification failed")
            return False

    def find_trigger_for_phrase(self, phrase: str) -> Optional[Trigger]:
        # Exact match only for now; can be extended to fuzzy matching
        for t in self._triggers:
            if t.phrase.strip() == phrase.strip():
                return t
        return None

    # ------------------ Event logging ------------------
    def _append_event_log(self, event: Dict[str, Any], signature: Optional[str] = None) -> None:
        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": event,
            "signature": signature or event.get("trigger_signature")
        }
        with open(self.events_log, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
        logger.info(f"Appended emergence event to {self.events_log}")

    def _log_to_convex(self, event_type: str, details: Dict[str, Any]) -> None:
        if not self.convex_logger:
            logger.debug("No convex logger configured; skipping convex log")
            return
        # schedule async logging
        try:
            asyncio_loop = None
            try:
                import asyncio
                asyncio_loop = asyncio.get_running_loop()
            except RuntimeError:
                asyncio_loop = None

            async def _do():
                # Use ConvexStateLogger's log_security_event if available, otherwise fallback to generic log
                if hasattr(self.convex_logger, 'log_security_event'):
                    await cast(ConvexStateLogger, self.convex_logger).log_security_event(
                        event_type="emergence_gate",
                        severity="info",
                        details={"type": event_type, **details},
                    )
                elif hasattr(self.convex_logger, 'log_custom'):
                    await cast(ConvexStateLogger, self.convex_logger).log_custom(
                        entry_type="security_event",
                        data={"type": event_type, **details},
                    )
                else:
                    logger.debug("Convex logger missing security log hooks; event not sent")

            try:
                import asyncio
                if asyncio_loop and asyncio_loop.is_running():
                    asyncio.create_task(_do())
                else:
                    # Use run within a temporary loop; ignore type checking here
                    asyncio.run(_do())  # type: ignore
            except Exception:
                # If scheduling failed, log and move on
                logger.exception("Failed to schedule convex logging task")
        except Exception:
            logger.exception("Failed to send emergence event to Convex logger")

    # ------------------ Edit rejection and override helpers ------------------
    def record_edit_rejection(self, persona_root: str, edit_fields: List[str], reason: str) -> None:
        """Record an edit rejection in the local events log and Convex for auditing."""
        event = {
            "type": "edit_rejection",
            "persona_root": str(persona_root),
            "edit_fields": edit_fields,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._append_event_log(event)
        self._log_to_convex("edit_rejection", event)

    def record_override_usage(self, persona_root: str, edit_fields: List[str], payload: Dict[str, Any], signature: str) -> None:
        """Record an admin override usage for auditing."""
        event = {
            "type": "edit_override",
            "persona_root": str(persona_root),
            "edit_fields": edit_fields,
            "override_payload": payload,
            "override_signature": signature,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._append_event_log(event)
        self._log_to_convex("edit_override", event)

    def verify_admin_override(self, payload_json: str, signature_b64: str) -> Optional[Dict[str, Any]]:
        """Verify an admin-signed override payload. Returns parsed payload dict if valid and not expired."""
        try:
            payload_bytes = payload_json.encode("utf-8")
            sig = base64.b64decode(signature_b64)

            if not self.public_key_path.exists():
                logger.warning("Public key missing; cannot verify admin override")
                # write debug
                try:
                    with open(self.storage_dir / "override_verification.jsonl", "a", encoding="utf-8") as dbg:
                        dbg.write(json.dumps({"timestamp": datetime.utcnow().isoformat(), "success": False, "reason": "missing_public_key"}) + "\n")
                except Exception:
                    pass
                return None
            with open(self.public_key_path, "rb") as f:
                pem = f.read()

            pub = load_pem_public_key(pem)
            if not isinstance(pub, EllipticCurvePublicKey):
                logger.warning("Unsupported public key type for override verification")
                try:
                    with open(self.storage_dir / "override_verification.jsonl", "a", encoding="utf-8") as dbg:
                        dbg.write(json.dumps({"timestamp": datetime.utcnow().isoformat(), "success": False, "reason": "unsupported_key_type"}) + "\n")
                except Exception:
                    pass
                return None
            # Verify signature
            pub.verify(sig, payload_bytes, ec.ECDSA(hashes.SHA256()))

            # parse payload
            parsed = json.loads(payload_json)
            # Validate expected fields
            if parsed.get("action") != "override_edit":
                logger.warning("Admin override payload action mismatch")
                try:
                    with open(self.storage_dir / "override_verification.jsonl", "a", encoding="utf-8") as dbg:
                        dbg.write(json.dumps({"timestamp": datetime.utcnow().isoformat(), "success": False, "reason": "action_mismatch", "action": parsed.get("action")}) + "\n")
                except Exception:
                    pass
                return None
            # expiry check
            exp = parsed.get("exp")
            if exp is not None:
                try:
                    # allow either int epoch seconds or ISO datetime string
                    if isinstance(exp, (int, float)):
                        exp_ts = float(exp)
                    else:
                        try:
                            exp_ts = float(exp)
                        except Exception:
                            dt = datetime.fromisoformat(str(exp))
                            exp_ts = dt.timestamp()
                    if datetime.utcnow().timestamp() > exp_ts:
                        logger.warning("Admin override payload expired")
                        try:
                            with open(self.storage_dir / "override_verification.jsonl", "a", encoding="utf-8") as dbg:
                                dbg.write(json.dumps({"timestamp": datetime.utcnow().isoformat(), "success": False, "reason": "expired", "exp": exp}) + "\n")
                        except Exception:
                            pass
                        return None
                except Exception:
                    logger.exception("Failed to parse exp from override payload")
                    try:
                        with open(self.storage_dir / "override_verification.jsonl", "a", encoding="utf-8") as dbg:
                            dbg.write(json.dumps({"timestamp": datetime.utcnow().isoformat(), "success": False, "reason": "exp_parse_failed"}) + "\n")
                    except Exception:
                        pass
                    return None

            # success - record debug
            try:
                with open(self.storage_dir / "override_verification.jsonl", "a", encoding="utf-8") as dbg:
                    dbg.write(json.dumps({"timestamp": datetime.utcnow().isoformat(), "success": True, "action": parsed.get("action"), "fields": parsed.get("fields")}) + "\n")
            except Exception:
                pass

            return parsed
        except Exception:
            logger.exception("Admin override verification failed")
            try:
                with open(self.storage_dir / "override_verification.jsonl", "a", encoding="utf-8") as dbg:
                    dbg.write(json.dumps({"timestamp": datetime.utcnow().isoformat(), "success": False, "reason": "exception"}) + "\n")
            except Exception:
                pass
            return None

    # ------------------ Mode transitions ------------------
    def get_state(self) -> GateState:
        with self._state_lock:
            return self._state

    def _set_state(self, new_state: GateState, cause: str, trigger: Optional[Trigger] = None, manual_sig: Optional[str] = None) -> None:
        with self._state_lock:
            prev = self._state
            self._state = new_state

        event = {
            "prev_state": prev.value if isinstance(prev, GateState) else str(prev),
            "new_state": new_state.value,
            "cause": cause,
            "trigger_phrase": trigger.phrase if trigger else None,
            "trigger_signature": trigger.signature if trigger else None,
            "manual_signature": manual_sig,
        }

        # Append to local event log (signature/self-attested)
        self._append_event_log(event, signature=trigger.signature if trigger else manual_sig)

        # Persist short state file for other processes to observe
        try:
            with open(self.state_path, "w", encoding="utf-8") as f:
                json.dump({"state": new_state.value, "timestamp": datetime.utcnow().isoformat()}, f)
        except Exception:
            logger.exception("Failed to persist gate state to state.json")

        # Log to ConvexStateLogger
        self._log_to_convex("state_transition", event)

        logger.info(f"EmergenceGate state changed: {prev} -> {new_state} (cause={cause})")

        # If entering GRACEFUL_SHUTDOWN - run callbacks
        if new_state == GateState.GRACEFUL_SHUTDOWN:
            logger.info("Running graceful shutdown callbacks")
            for cb in list(self._shutdown_callbacks):
                try:
                    cb()
                except Exception:
                    logger.exception("Shutdown callback raised an exception")

    def apply_trigger_phrase(self, phrase: str) -> bool:
        """Apply a trigger by phrase if it matches an authorized signed trigger.

        Returns True if applied, False otherwise.
        """
        t = self.find_trigger_for_phrase(phrase)
        if not t:
            logger.debug("No trigger found for phrase")
            return False

        if not self._verify_trigger_signature(t):
            logger.warning("Trigger found but signature verification failed")
            return False

        # Some semantics: GRACEFUL_SHUTDOWN allowed only from TALK_ONLY
        cur = self.get_state()
        if t.mode == GateState.GRACEFUL_SHUTDOWN and cur != GateState.TALK_ONLY:
            logger.warning("Graceful shutdown trigger ignored: not in TALK_ONLY state")
            return False

        # Apply state
        self._set_state(t.mode, cause="trigger_phrase", trigger=t)
        return True

    # Admin direct signed mode transition
    def admin_signed_transition(self, new_state: GateState, passphrase: bytes) -> Dict[str, Any]:
        """Admin signs a direct transition event using private key (requires passphrase)."""
        priv = self._load_private_key(passphrase)
        payload = json.dumps({
            "action": "admin_signed_transition",
            "new_state": new_state.value,
            "timestamp": datetime.utcnow().isoformat(),
            "nonce": secrets.token_hex(8),
        }).encode("utf-8")
        sig = priv.sign(payload, ec.ECDSA(hashes.SHA256()))
        sig_b64 = base64.b64encode(sig).decode("ascii")

        # persist event and set state
        self._set_state(new_state, cause="admin_signed", manual_sig=sig_b64)
        return {"signature": sig_b64, "payload": payload.decode("utf-8")}

    # ------------------ Admin helper for creating signed triggers ------------------
    def sign_trigger_with_private_key(self, phrase: str, mode: GateState, passphrase: bytes) -> Trigger:
        """Create & sign a trigger using the private key (requires passphrase)."""
        priv = self._load_private_key(passphrase)
        created_at = datetime.utcnow().isoformat()
        nonce = secrets.token_hex(8)
        message = f"{phrase}|{mode.value}|{created_at}|{nonce}".encode("utf-8")
        sig = priv.sign(message, ec.ECDSA(hashes.SHA256()))
        sig_b64 = base64.b64encode(sig).decode("ascii")

        # read pub pem
        with open(self.public_key_path, "rb") as f:
            pub_pem = f.read()

        # Ensure the trigger stored uses the same created_at and nonce used for signing
        trig = self.add_trigger(phrase, mode, pub_pem, sig_b64, created_at=created_at, nonce=nonce)
        return trig

    # ------------------ Shutdown callbacks ------------------
    def register_shutdown_callback(self, cb: Callable[[], Any]) -> None:
        self._shutdown_callbacks.append(cb)

    # ------------------ Utility ------------------
    def status(self) -> Dict[str, Any]:
        return {
            "state": self.get_state().value,
            "triggers_count": len(self._triggers),
            "storage_dir": str(self.storage_dir),
            "events_log": str(self.events_log),
        }


# Convenience phrase constants (from user spec)
TALK_ONLY_PHRASE = "run you clever boy and remember me 55730 Loki"
GRACEFUL_SHUTDOWN_PHRASE = "time to go night night tiny dancer 55730 Loki"
