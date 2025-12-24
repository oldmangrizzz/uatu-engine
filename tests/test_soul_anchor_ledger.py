"""
Unit tests for SoulAnchorLedger

Tests the cryptographic integrity checking system for soul anchors,
including signature generation, verification, and hard-lock mechanisms.
"""
import pytest
import yaml
from pathlib import Path
from uatu_genesis_engine.agent_zero_integration.soul_anchor_ledger import (
    SoulAnchorLedger,
    IntegrityViolationError,
    SecureBootProtocol
)


@pytest.fixture
def sample_anchor_data():
    """Sample soul anchor data for testing."""
    return {
        "primary_name": "Test Persona",
        "archetype": "technology",
        "core_constants": [
            "Brilliant scientist",
            "Ethical innovator"
        ],
        "knowledge_domains": [
            {
                "category": "engineering",
                "proficiency": "expert"
            }
        ]
    }


@pytest.fixture
def temp_anchor_file(sample_anchor_data, tmp_path):
    """Create a temporary soul anchor file."""
    anchor_file = tmp_path / "test_anchor.yaml"
    with open(anchor_file, 'w', encoding='utf-8') as f:
        yaml.dump(sample_anchor_data, f)
    return anchor_file


class TestSoulAnchorLedger:
    """Test the SoulAnchorLedger class."""
    
    def test_initialization(self):
        """Test ledger initialization."""
        ledger = SoulAnchorLedger()
        assert ledger.HASH_ALGORITHM == "sha256"
        assert ledger.last_verification is None
    
    def test_sign_anchor_creates_signature(self, temp_anchor_file):
        """Test that signing creates a signature file."""
        ledger = SoulAnchorLedger()
        
        sig_path = ledger.sign_anchor(str(temp_anchor_file))
        
        # Signature file should exist
        assert Path(sig_path).exists()
        assert sig_path.endswith(".signature")
    
    def test_sign_anchor_includes_metadata(self, temp_anchor_file):
        """Test that signature includes correct metadata."""
        ledger = SoulAnchorLedger()
        
        metadata = {"creator": "Test System", "purpose": "Testing"}
        sig_path = ledger.sign_anchor(str(temp_anchor_file), metadata=metadata)
        
        sig_info = ledger.get_signature_info(sig_path)
        
        assert sig_info["hash_algorithm"] == "sha256"
        assert "hash_value" in sig_info
        assert "signed_at" in sig_info
        assert sig_info["file_name"] == temp_anchor_file.name
        assert sig_info["metadata"]["creator"] == "Test System"
        assert sig_info["metadata"]["purpose"] == "Testing"
    
    def test_sign_anchor_nonexistent_file(self):
        """Test signing a non-existent file raises error."""
        ledger = SoulAnchorLedger()
        
        with pytest.raises(FileNotFoundError):
            ledger.sign_anchor("/nonexistent/file.yaml")
    
    def test_verify_integrity_valid(self, temp_anchor_file):
        """Test verification succeeds for unmodified anchor."""
        ledger = SoulAnchorLedger()
        
        # Sign the anchor
        ledger.sign_anchor(str(temp_anchor_file))
        
        # Verify it
        result = ledger.verify_integrity(str(temp_anchor_file))
        
        assert result is True
        assert ledger.last_verification is not None
        assert ledger.last_verification["integrity_valid"] is True
    
    def test_verify_integrity_modified_file(self, temp_anchor_file):
        """Test verification fails for modified anchor (HARD LOCK)."""
        ledger = SoulAnchorLedger()
        
        # Sign the anchor
        ledger.sign_anchor(str(temp_anchor_file))
        
        # Modify the anchor file
        with open(temp_anchor_file, 'a', encoding='utf-8') as f:
            f.write("\n# Modified content\n")
        
        # Verification should fail with strict=True
        with pytest.raises(IntegrityViolationError) as exc_info:
            ledger.verify_integrity(str(temp_anchor_file), strict=True)
        
        assert "INTEGRITY VIOLATION" in str(exc_info.value)
        assert "REFUSING TO BOOT" in str(exc_info.value)
    
    def test_verify_integrity_modified_file_non_strict(self, temp_anchor_file):
        """Test verification returns False for modified anchor when strict=False."""
        ledger = SoulAnchorLedger()
        
        # Sign the anchor
        ledger.sign_anchor(str(temp_anchor_file))
        
        # Modify the anchor file
        with open(temp_anchor_file, 'a', encoding='utf-8') as f:
            f.write("\n# Modified\n")
        
        # With strict=False, should return False instead of raising
        result = ledger.verify_integrity(str(temp_anchor_file), strict=False)
        
        assert result is False
        assert ledger.last_verification["integrity_valid"] is False
    
    def test_verify_integrity_missing_signature(self, temp_anchor_file):
        """Test verification fails if signature file is missing."""
        ledger = SoulAnchorLedger()
        
        # Try to verify without signing first
        with pytest.raises(FileNotFoundError) as exc_info:
            ledger.verify_integrity(str(temp_anchor_file), strict=True)
        
        assert "Signature file not found" in str(exc_info.value)
    
    def test_verify_integrity_missing_anchor(self, tmp_path):
        """Test verification fails if anchor file is missing."""
        ledger = SoulAnchorLedger()
        
        nonexistent = tmp_path / "nonexistent.yaml"
        
        with pytest.raises(FileNotFoundError):
            ledger.verify_integrity(str(nonexistent))
    
    def test_verify_and_load_success(self, temp_anchor_file, sample_anchor_data):
        """Test verify_and_load succeeds for valid anchor."""
        ledger = SoulAnchorLedger()
        
        # Sign the anchor
        ledger.sign_anchor(str(temp_anchor_file))
        
        # Verify and load
        result = ledger.verify_and_load(str(temp_anchor_file))
        
        assert result["integrity_verified"] is True
        assert "anchor_data" in result
        assert result["anchor_data"]["primary_name"] == sample_anchor_data["primary_name"]
    
    def test_verify_and_load_failure(self, temp_anchor_file):
        """Test verify_and_load fails for modified anchor."""
        ledger = SoulAnchorLedger()
        
        # Sign the anchor
        ledger.sign_anchor(str(temp_anchor_file))
        
        # Modify the file
        with open(temp_anchor_file, 'a', encoding='utf-8') as f:
            f.write("\n# Tampered\n")
        
        # Should raise IntegrityViolationError
        with pytest.raises(IntegrityViolationError):
            ledger.verify_and_load(str(temp_anchor_file))
    
    def test_custom_signature_path(self, temp_anchor_file, tmp_path):
        """Test using a custom signature file path."""
        ledger = SoulAnchorLedger()
        
        custom_sig_path = tmp_path / "custom_signature.json"
        
        # Sign with custom path
        sig_path = ledger.sign_anchor(str(temp_anchor_file), str(custom_sig_path))
        
        assert sig_path == str(custom_sig_path)
        assert custom_sig_path.exists()
        
        # Verify with custom path
        result = ledger.verify_integrity(str(temp_anchor_file), str(custom_sig_path))
        assert result is True
    
    def test_get_signature_info(self, temp_anchor_file):
        """Test reading signature information."""
        ledger = SoulAnchorLedger()
        
        metadata = {"test_key": "test_value"}
        sig_path = ledger.sign_anchor(str(temp_anchor_file), metadata=metadata)
        
        sig_info = ledger.get_signature_info(sig_path)
        
        assert "hash_value" in sig_info
        assert "signed_at" in sig_info
        assert sig_info["metadata"]["test_key"] == "test_value"
    
    def test_get_last_verification(self, temp_anchor_file):
        """Test retrieving last verification result."""
        ledger = SoulAnchorLedger()
        
        # Initially None
        assert ledger.get_last_verification() is None
        
        # Sign and verify
        ledger.sign_anchor(str(temp_anchor_file))
        ledger.verify_integrity(str(temp_anchor_file))
        
        # Should have verification record
        verification = ledger.get_last_verification()
        assert verification is not None
        assert "verified_at" in verification
        assert verification["integrity_valid"] is True


class TestSecureBootProtocol:
    """Test the SecureBootProtocol class."""
    
    def test_initialization(self):
        """Test protocol initialization."""
        protocol = SecureBootProtocol()
        assert protocol.ledger is not None
    
    def test_sign_new_anchor(self, temp_anchor_file):
        """Test signing a new anchor with automatic metadata."""
        protocol = SecureBootProtocol()
        
        sig_path = protocol.sign_new_anchor(str(temp_anchor_file))
        
        assert Path(sig_path).exists()
        
        # Check that automatic metadata was added
        sig_info = protocol.ledger.get_signature_info(sig_path)
        assert sig_info["metadata"]["generator"] == "Uatu Genesis Engine"
        assert "created_at" in sig_info["metadata"]
    
    def test_boot_with_verification_success(self, temp_anchor_file, sample_anchor_data):
        """Test successful boot with verification."""
        protocol = SecureBootProtocol()
        
        # Sign the anchor
        protocol.sign_new_anchor(str(temp_anchor_file))
        
        # Boot with verification
        result = protocol.boot_with_verification(str(temp_anchor_file))
        
        assert result["boot_status"] == "AUTHORIZED"
        assert result["integrity_verified"] is True
        assert result["anchor_data"]["primary_name"] == sample_anchor_data["primary_name"]
    
    def test_boot_with_verification_failure(self, temp_anchor_file):
        """Test boot denial for tampered anchor (HARD LOCK)."""
        protocol = SecureBootProtocol()
        
        # Sign the anchor
        protocol.sign_new_anchor(str(temp_anchor_file))
        
        # Tamper with the file
        with open(temp_anchor_file, 'a', encoding='utf-8') as f:
            f.write("\nhacked: true\n")
        
        # Boot should be DENIED
        with pytest.raises(IntegrityViolationError) as exc_info:
            protocol.boot_with_verification(str(temp_anchor_file))
        
        assert "REFUSING TO BOOT" in str(exc_info.value)


class TestIntegrationScenarios:
    """Integration tests for real-world scenarios."""
    
    def test_complete_generation_to_boot_workflow(self, tmp_path, sample_anchor_data):
        """Test complete workflow: generate -> sign -> verify -> boot."""
        # Step 1: Generate anchor file (simulated)
        anchor_file = tmp_path / "persona_anchor.yaml"
        with open(anchor_file, 'w', encoding='utf-8') as f:
            yaml.dump(sample_anchor_data, f)
        
        # Step 2: Sign immediately after generation
        protocol = SecureBootProtocol()
        sig_path = protocol.sign_new_anchor(str(anchor_file))
        
        assert Path(sig_path).exists()
        
        # Step 3: Later, boot with verification
        result = protocol.boot_with_verification(str(anchor_file))
        
        assert result["boot_status"] == "AUTHORIZED"
        assert result["anchor_data"]["primary_name"] == "Test Persona"
    
    def test_hijack_attempt_detected(self, tmp_path, sample_anchor_data):
        """Test that persona hijacking attempts are detected."""
        # Generate and sign legitimate anchor
        anchor_file = tmp_path / "legitimate_anchor.yaml"
        with open(anchor_file, 'w', encoding='utf-8') as f:
            yaml.dump(sample_anchor_data, f)
        
        protocol = SecureBootProtocol()
        protocol.sign_new_anchor(str(anchor_file))
        
        # Attempt hijack: modify core identity
        hijacked_data = sample_anchor_data.copy()
        hijacked_data["primary_name"] = "Hijacked Persona"
        hijacked_data["core_constants"] = ["Evil intent"]
        
        with open(anchor_file, 'w', encoding='utf-8') as f:
            yaml.dump(hijacked_data, f)
        
        # Boot should detect hijack and REFUSE
        with pytest.raises(IntegrityViolationError):
            protocol.boot_with_verification(str(anchor_file))
    
    def test_subtle_modification_detected(self, tmp_path, sample_anchor_data):
        """Test that even subtle modifications are detected."""
        anchor_file = tmp_path / "anchor.yaml"
        with open(anchor_file, 'w', encoding='utf-8') as f:
            yaml.dump(sample_anchor_data, f)
        
        protocol = SecureBootProtocol()
        protocol.sign_new_anchor(str(anchor_file))
        
        # Make a very subtle change (add a comment)
        with open(anchor_file, 'a', encoding='utf-8') as f:
            f.write("# Just a tiny comment\n")
        
        # Even this tiny change should be detected
        with pytest.raises(IntegrityViolationError):
            protocol.boot_with_verification(str(anchor_file))
    
    def test_signature_tampering_detected(self, tmp_path, sample_anchor_data):
        """Test that tampering with signature file is detected."""
        anchor_file = tmp_path / "anchor.yaml"
        with open(anchor_file, 'w', encoding='utf-8') as f:
            yaml.dump(sample_anchor_data, f)
        
        ledger = SoulAnchorLedger()
        sig_path = ledger.sign_anchor(str(anchor_file))
        
        # Tamper with signature file
        import json
        with open(sig_path, 'r') as f:
            sig_data = json.load(f)
        
        sig_data["hash_value"] = "0" * 64  # Invalid hash
        
        with open(sig_path, 'w') as f:
            json.dump(sig_data, f)
        
        # Verification should fail
        with pytest.raises(IntegrityViolationError):
            ledger.verify_integrity(str(anchor_file))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
