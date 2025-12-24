"""
SoulAnchorLedger - Cryptographic Integrity for Soul Anchors

Implements SHA-256 hash-based integrity checking for soul anchor files.
This module ensures that the soul anchor (the immutable identity core) cannot
be tampered with after generation.

The ledger creates a cryptographic signature at anchor generation time and
verifies it at boot time. If the signature doesn't match, the agent REFUSES
to boot (Hard Lock), preventing persona hijacking.
"""
import hashlib
import json
import logging
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class IntegrityViolationError(Exception):
    """
    Raised when soul anchor integrity check fails.
    
    This is a critical security error - the anchor has been modified
    and the agent should refuse to boot.
    """
    pass


class SoulAnchorLedger:
    """
    Cryptographic ledger for soul anchor integrity verification.
    
    This implements the "Security Lock" - ensuring that the soul anchor
    remains immutable through cryptographic hashing.
    
    Boot Protocol:
    1. Load soul anchor file
    2. Calculate current hash
    3. Compare with stored signature
    4. If mismatch: REFUSE TO BOOT (Hard Lock)
    5. If match: Proceed with initialization
    """
    
    SIGNATURE_EXTENSION = ".signature"
    HASH_ALGORITHM = "sha256"
    
    def __init__(self):
        """Initialize the soul anchor ledger."""
        self.last_verification: Optional[Dict[str, Any]] = None
        logger.info("SoulAnchorLedger initialized")
    
    def sign_anchor(
        self,
        anchor_file_path: str,
        signature_file_path: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a cryptographic signature for a soul anchor file.
        
        This should be called immediately after generating a soul anchor
        to create its immutable signature.
        
        Args:
            anchor_file_path: Path to the soul anchor YAML file
            signature_file_path: Optional custom path for signature file
                                (defaults to anchor_file_path + .signature)
            metadata: Optional metadata to include in signature (e.g., creator, timestamp)
            
        Returns:
            Path to the generated signature file
            
        Raises:
            FileNotFoundError: If anchor file doesn't exist
        """
        anchor_path = Path(anchor_file_path)
        
        if not anchor_path.exists():
            raise FileNotFoundError(f"Soul anchor file not found: {anchor_file_path}")
        
        # Read anchor file content
        with open(anchor_path, 'rb') as f:
            anchor_content = f.read()
        
        # Calculate SHA-256 hash
        hash_value = self._calculate_hash(anchor_content)
        
        # Create signature record
        signature_data = {
            "file_path": str(anchor_path.absolute()),
            "file_name": anchor_path.name,
            "hash_algorithm": self.HASH_ALGORITHM,
            "hash_value": hash_value,
            "file_size": len(anchor_content),
            "signed_at": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        # Determine signature file path
        if signature_file_path is None:
            sig_path = Path(str(anchor_path) + self.SIGNATURE_EXTENSION)
        else:
            sig_path = Path(signature_file_path)
        
        # Write signature file
        with open(sig_path, 'w', encoding='utf-8') as f:
            json.dump(signature_data, f, indent=2)
        
        logger.info(f"Soul anchor signed: {anchor_file_path}")
        logger.info(f"Signature saved: {sig_path}")
        logger.debug(f"Hash: {hash_value}")
        
        return str(sig_path)
    
    def verify_integrity(
        self,
        anchor_file_path: str,
        signature_file_path: Optional[str] = None,
        strict: bool = True
    ) -> bool:
        """
        Verify the integrity of a soul anchor file against its signature.
        
        This is the BOOT PROTOCOL - called before loading a soul anchor.
        If verification fails and strict=True, raises IntegrityViolationError.
        
        Args:
            anchor_file_path: Path to the soul anchor YAML file
            signature_file_path: Optional custom path to signature file
                                (defaults to anchor_file_path + .signature)
            strict: If True, raises exception on failure. If False, returns False.
            
        Returns:
            True if integrity check passes, False if fails (when strict=False)
            
        Raises:
            FileNotFoundError: If anchor or signature file doesn't exist
            IntegrityViolationError: If integrity check fails (when strict=True)
        """
        anchor_path = Path(anchor_file_path)
        
        if not anchor_path.exists():
            raise FileNotFoundError(f"Soul anchor file not found: {anchor_file_path}")
        
        # Determine signature file path
        if signature_file_path is None:
            sig_path = Path(str(anchor_path) + self.SIGNATURE_EXTENSION)
        else:
            sig_path = Path(signature_file_path)
        
        if not sig_path.exists():
            error_msg = f"Signature file not found: {sig_path}"
            logger.error(error_msg)
            if strict:
                raise FileNotFoundError(error_msg)
            return False
        
        # Read signature data
        with open(sig_path, 'r', encoding='utf-8') as f:
            signature_data = json.load(f)
        
        # Read current anchor content
        with open(anchor_path, 'rb') as f:
            current_content = f.read()
        
        # Calculate current hash
        current_hash = self._calculate_hash(current_content)
        
        # Get stored hash
        stored_hash = signature_data.get("hash_value")
        
        # Compare hashes
        integrity_valid = current_hash == stored_hash
        
        # Store verification result
        self.last_verification = {
            "file_path": str(anchor_path.absolute()),
            "verified_at": datetime.now().isoformat(),
            "integrity_valid": integrity_valid,
            "current_hash": current_hash,
            "stored_hash": stored_hash,
            "signed_at": signature_data.get("signed_at"),
            "file_size": len(current_content),
            "stored_file_size": signature_data.get("file_size")
        }
        
        if integrity_valid:
            logger.info(f"✅ Soul anchor integrity verified: {anchor_file_path}")
            logger.debug(f"Hash match: {current_hash}")
            return True
        else:
            error_msg = (
                f"❌ INTEGRITY VIOLATION DETECTED ❌\n"
                f"Soul anchor has been modified: {anchor_file_path}\n"
                f"Expected hash: {stored_hash}\n"
                f"Current hash:  {current_hash}\n"
                f"Signed at:     {signature_data.get('signed_at')}\n"
                f"File size:     Expected {signature_data.get('file_size')}, "
                f"Found {len(current_content)}\n"
                f"REFUSING TO BOOT - Persona integrity compromised"
            )
            logger.error(error_msg)
            
            if strict:
                raise IntegrityViolationError(error_msg)
            
            return False
    
    def _calculate_hash(self, content: bytes) -> str:
        """
        Calculate SHA-256 hash of content.
        
        Args:
            content: Raw bytes to hash
            
        Returns:
            Hexadecimal hash string
        """
        hasher = hashlib.sha256()
        hasher.update(content)
        return hasher.hexdigest()
    
    def get_signature_info(self, signature_file_path: str) -> Dict[str, Any]:
        """
        Read signature information without verification.
        
        Useful for inspecting signature metadata.
        
        Args:
            signature_file_path: Path to signature file
            
        Returns:
            Dictionary containing signature information
            
        Raises:
            FileNotFoundError: If signature file doesn't exist
        """
        sig_path = Path(signature_file_path)
        
        if not sig_path.exists():
            raise FileNotFoundError(f"Signature file not found: {signature_file_path}")
        
        with open(sig_path, 'r', encoding='utf-8') as f:
            signature_data = json.load(f)
        
        return signature_data
    
    def get_last_verification(self) -> Optional[Dict[str, Any]]:
        """
        Get the results of the last verification performed.
        
        Returns:
            Dictionary with verification details, or None if no verification performed
        """
        return self.last_verification
    
    def verify_and_load(
        self,
        anchor_file_path: str,
        signature_file_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Verify integrity and load soul anchor in one operation.
        
        This is the recommended boot sequence method.
        
        Args:
            anchor_file_path: Path to soul anchor YAML file
            signature_file_path: Optional custom signature file path
            
        Returns:
            Dictionary containing both verification status and anchor data
            
        Raises:
            IntegrityViolationError: If integrity check fails
            FileNotFoundError: If files don't exist
        """
        # First, verify integrity (raises exception if fails)
        integrity_valid = self.verify_integrity(anchor_file_path, signature_file_path, strict=True)
        
        # If we get here, integrity is valid - safe to load
        anchor_path = Path(anchor_file_path)
        with open(anchor_path, 'r', encoding='utf-8') as f:
            anchor_data = yaml.safe_load(f)
        
        logger.info("Soul anchor loaded after successful integrity verification")
        
        return {
            "integrity_verified": True,
            "anchor_data": anchor_data,
            "verification_details": self.last_verification
        }


class SecureBootProtocol:
    """
    High-level secure boot protocol for Agent Zero personas.
    
    This class orchestrates the complete boot sequence with integrity checking.
    """
    
    def __init__(self):
        """Initialize secure boot protocol."""
        self.ledger = SoulAnchorLedger()
        logger.info("SecureBootProtocol initialized")
    
    def boot_with_verification(
        self,
        anchor_file_path: str,
        signature_file_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute secure boot protocol with integrity verification.
        
        This is the HARD LOCK implementation:
        1. Verify anchor integrity
        2. If verification fails, REFUSE TO BOOT
        3. If verification succeeds, load anchor and proceed
        
        Args:
            anchor_file_path: Path to soul anchor file
            signature_file_path: Optional signature file path
            
        Returns:
            Dictionary with boot status and anchor data
            
        Raises:
            IntegrityViolationError: If integrity check fails (HARD LOCK)
        """
        logger.info("=" * 80)
        logger.info("SECURE BOOT PROTOCOL - Soul Anchor Integrity Check")
        logger.info("=" * 80)
        
        try:
            # Attempt verification and load
            result = self.ledger.verify_and_load(anchor_file_path, signature_file_path)
            
            logger.info("✅ BOOT AUTHORIZED - Integrity verified")
            logger.info("Persona identity is cryptographically secured")
            logger.info("=" * 80)
            
            return {
                "boot_status": "AUTHORIZED",
                "integrity_verified": True,
                "anchor_data": result["anchor_data"],
                "verification_details": result["verification_details"]
            }
            
        except IntegrityViolationError:
            logger.error("=" * 80)
            logger.error("❌ BOOT DENIED - HARD LOCK ENGAGED ❌")
            logger.error("Soul anchor integrity compromised")
            logger.error("Refusing to load persona")
            logger.error("=" * 80)
            
            raise  # Re-raise to prevent boot
        
        except Exception as e:
            logger.error(f"Boot protocol error: {e}")
            raise
    
    def sign_new_anchor(
        self,
        anchor_file_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Sign a newly generated soul anchor.
        
        This should be called immediately after anchor generation.
        
        Args:
            anchor_file_path: Path to the soul anchor file
            metadata: Optional metadata (e.g., generator version, timestamp)
            
        Returns:
            Path to generated signature file
        """
        logger.info(f"Signing new soul anchor: {anchor_file_path}")
        
        # Add automatic metadata
        auto_metadata = {
            "generator": "Uatu Genesis Engine",
            "ledger_version": "1.0",
            "created_at": datetime.now().isoformat()
        }
        
        if metadata:
            auto_metadata.update(metadata)
        
        signature_path = self.ledger.sign_anchor(anchor_file_path, metadata=auto_metadata)
        
        logger.info("✅ Soul anchor signed and secured")
        logger.info(f"Signature: {signature_path}")
        
        return signature_path
