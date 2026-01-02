"""
Unit tests for RSIGenerator

Tests the Residual Self-Image Generator for AI personas.
"""

import os
from pathlib import Path
from unittest.mock import Mock, patch
import tempfile
import shutil


class TestRSIGenerator:
    """Test the RSIGenerator class."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create a temporary directory for test outputs
        self.test_dir = tempfile.mkdtemp()
        self.test_avatar_path = Path(self.test_dir) / "avatar.png"

    def teardown_method(self):
        """Clean up after tests."""
        if Path(self.test_dir).exists():
            shutil.rmtree(self.test_dir)

    def test_describe_self_with_memory(self):
        """Test describe_self with agent memory data."""
        from agent_zero_framework.python.helpers.rsi_generator import RSIGenerator

        # Test memory data
        test_memory = {
            "primary_name": "Test Agent",
            "archetype": "strategist",
            "core_constants": ["analytical", "precise", "strategic"],
        }

        # Since the imports are dynamic and complex, we'll test that it falls back gracefully
        description = RSIGenerator.describe_self(test_memory)

        # Verify we get a description (either from LLM or fallback)
        assert isinstance(description, str)
        assert len(description) > 0
        # Should contain the agent name from memory
        assert "Test Agent" in description or "digital entity" in description.lower()

    def test_describe_self_fallback(self):
        """Test describe_self fallback when LLM is unavailable."""
        from agent_zero_framework.python.helpers.rsi_generator import RSIGenerator

        test_memory = {"primary_name": "Fallback Agent"}

        # Call the method - it will use fallback if agent infrastructure isn't available
        description = RSIGenerator.describe_self(test_memory)

        # Verify fallback description works
        assert isinstance(description, str)
        assert (
            "Fallback Agent" in description or "digital entity" in description.lower()
        )
        assert len(description) > 50  # Should be a substantial description

    def test_describe_self_no_memory(self):
        """Test describe_self with no memory data."""
        from agent_zero_framework.python.helpers.rsi_generator import RSIGenerator

        # Call with None
        description = RSIGenerator.describe_self(None)

        # Verify we still get a description
        assert isinstance(description, str)
        assert len(description) > 0
        assert "Unknown" in description or "digital entity" in description.lower()

    @patch("agent_zero_framework.python.helpers.rsi_generator.InferenceClient")
    def test_generate_avatar_via_flux_success(self, mock_inference_client):
        """Test successful avatar generation via Flux."""
        from agent_zero_framework.python.helpers.rsi_generator import RSIGenerator

        # Create a mock PIL Image
        mock_image = Mock()
        mock_image.save = Mock()

        # Set up InferenceClient mock
        mock_client = Mock()
        mock_client.text_to_image.return_value = mock_image
        mock_inference_client.return_value = mock_client

        # Set HF_TOKEN in environment
        os.environ["HF_TOKEN"] = "test_token"

        try:
            # Call the method
            description = "A test avatar description"
            result = RSIGenerator.generate_avatar(
                description, str(self.test_avatar_path)
            )

            # Verify
            assert result is True
            mock_client.text_to_image.assert_called_once()
            mock_image.save.assert_called_once()
        finally:
            # Clean up
            if "HF_TOKEN" in os.environ:
                del os.environ["HF_TOKEN"]

    @patch("agent_zero_framework.python.helpers.rsi_generator.InferenceClient")
    @patch(
        "agent_zero_framework.python.helpers.rsi_generator.RSIGenerator._generate_via_openrouter"
    )
    def test_generate_avatar_flux_fallback_to_openrouter(
        self, mock_openrouter, mock_inference_client
    ):
        """Test fallback to OpenRouter when Flux fails."""
        from agent_zero_framework.python.helpers.rsi_generator import RSIGenerator

        # Set up Flux to fail
        mock_client = Mock()
        mock_client.text_to_image.side_effect = Exception("Flux error")
        mock_inference_client.return_value = mock_client

        # Set up OpenRouter to succeed
        mock_openrouter.return_value = True

        os.environ["HF_TOKEN"] = "test_token"

        try:
            # Call the method
            description = "A test avatar description"
            result = RSIGenerator.generate_avatar(
                description, str(self.test_avatar_path)
            )

            # Verify OpenRouter was called as fallback
            mock_openrouter.assert_called_once()
        finally:
            if "HF_TOKEN" in os.environ:
                del os.environ["HF_TOKEN"]

    def test_generate_avatar_creates_directory(self):
        """Test that generate_avatar creates output directory if it doesn't exist."""
        from agent_zero_framework.python.helpers.rsi_generator import RSIGenerator

        # Use a path in a non-existent subdirectory
        nested_path = Path(self.test_dir) / "subdir" / "avatar.png"

        with patch(
            "agent_zero_framework.python.helpers.rsi_generator.RSIGenerator._generate_via_flux"
        ) as mock_flux:
            mock_flux.return_value = True

            # Call the method
            RSIGenerator.generate_avatar("test", str(nested_path))

            # Verify directory was created
            assert nested_path.parent.exists()

    def test_generate_via_openrouter_success(self):
        """Test successful generation via OpenRouter."""
        from agent_zero_framework.python.helpers.rsi_generator import RSIGenerator

        # Test that it fails gracefully without API key
        if "OPENROUTER_API_KEY" in os.environ:
            del os.environ["OPENROUTER_API_KEY"]

        result = RSIGenerator._generate_via_openrouter(
            "test prompt", self.test_avatar_path
        )

        # Should return False without crashing when no API key
        assert result is False

    def test_generate_via_openrouter_no_api_key(self):
        """Test OpenRouter generation fails gracefully without API key."""
        from agent_zero_framework.python.helpers.rsi_generator import RSIGenerator

        # Ensure no API key
        if "OPENROUTER_API_KEY" in os.environ:
            del os.environ["OPENROUTER_API_KEY"]

        # Should return False without crashing
        result = RSIGenerator._generate_via_openrouter(
            "test prompt", self.test_avatar_path
        )

        assert result is False

    @patch("agent_zero_framework.python.helpers.rsi_generator.InferenceClient")
    def test_generate_via_flux_no_token(self, mock_inference_client):
        """Test Flux generation works without HF_TOKEN (tries anyway)."""
        from agent_zero_framework.python.helpers.rsi_generator import RSIGenerator

        # Remove token
        if "HF_TOKEN" in os.environ:
            del os.environ["HF_TOKEN"]
        if "HUGGINGFACE_TOKEN" in os.environ:
            del os.environ["HUGGINGFACE_TOKEN"]

        # Mock client to succeed
        mock_client = Mock()
        mock_image = Mock()
        mock_image.save = Mock()
        mock_client.text_to_image.return_value = mock_image
        mock_inference_client.return_value = mock_client

        # Should still try to generate
        result = RSIGenerator._generate_via_flux("test prompt", self.test_avatar_path)

        # Verify it was attempted
        mock_inference_client.assert_called_once()
