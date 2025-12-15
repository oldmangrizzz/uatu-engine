"""
Unit tests for RSIGenerator

Tests the Residual Self-Image Generator for AI personas.
"""
import os
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open
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
        # Import here to avoid issues if module isn't available yet
        from agent_zero_framework.python.helpers.rsi_generator import RSIGenerator
        
        # Test memory data
        test_memory = {
            "primary_name": "Test Agent",
            "archetype": "strategist",
            "core_constants": ["analytical", "precise", "strategic"]
        }
        
        # Mock the LLM response
        with patch('agent_zero_framework.python.helpers.rsi_generator.AgentContext') as mock_context, \
             patch('agent_zero_framework.python.helpers.rsi_generator.models') as mock_models:
            
            # Set up mocks
            mock_model = Mock()
            mock_response = Mock()
            mock_response.content = "A detailed physical description of the agent..."
            mock_model.invoke.return_value = mock_response
            mock_models.get_chat_model.return_value = mock_model
            
            mock_ctx = Mock()
            mock_ctx.config = Mock()
            mock_context.current.return_value = mock_ctx
            
            # Call the method
            description = RSIGenerator.describe_self(test_memory)
            
            # Verify
            assert isinstance(description, str)
            assert len(description) > 0
            assert "A detailed physical description" in description
    
    def test_describe_self_fallback(self):
        """Test describe_self fallback when LLM is unavailable."""
        from agent_zero_framework.python.helpers.rsi_generator import RSIGenerator
        
        test_memory = {
            "primary_name": "Fallback Agent"
        }
        
        # Mock to raise exception, forcing fallback
        with patch('agent_zero_framework.python.helpers.rsi_generator.AgentContext') as mock_context:
            mock_context.current.side_effect = Exception("LLM unavailable")
            
            # Call the method
            description = RSIGenerator.describe_self(test_memory)
            
            # Verify fallback description
            assert isinstance(description, str)
            assert "Fallback Agent" in description
            assert "digital entity" in description.lower()
    
    def test_describe_self_no_memory(self):
        """Test describe_self with no memory data."""
        from agent_zero_framework.python.helpers.rsi_generator import RSIGenerator
        
        # Mock to force fallback
        with patch('agent_zero_framework.python.helpers.rsi_generator.AgentContext') as mock_context:
            mock_context.current.side_effect = Exception("No context")
            
            # Call with None
            description = RSIGenerator.describe_self(None)
            
            # Verify
            assert isinstance(description, str)
            assert len(description) > 0
    
    @patch('agent_zero_framework.python.helpers.rsi_generator.InferenceClient')
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
        os.environ['HF_TOKEN'] = 'test_token'
        
        try:
            # Call the method
            description = "A test avatar description"
            result = RSIGenerator.generate_avatar(description, str(self.test_avatar_path))
            
            # Verify
            assert result is True
            mock_client.text_to_image.assert_called_once()
            mock_image.save.assert_called_once()
        finally:
            # Clean up
            if 'HF_TOKEN' in os.environ:
                del os.environ['HF_TOKEN']
    
    @patch('agent_zero_framework.python.helpers.rsi_generator.InferenceClient')
    @patch('agent_zero_framework.python.helpers.rsi_generator.RSIGenerator._generate_via_dalle')
    def test_generate_avatar_flux_fallback_to_dalle(self, mock_dalle, mock_inference_client):
        """Test fallback to DALL-E when Flux fails."""
        from agent_zero_framework.python.helpers.rsi_generator import RSIGenerator
        
        # Set up Flux to fail
        mock_client = Mock()
        mock_client.text_to_image.side_effect = Exception("Flux error")
        mock_inference_client.return_value = mock_client
        
        # Set up DALL-E to succeed
        mock_dalle.return_value = True
        
        os.environ['HF_TOKEN'] = 'test_token'
        
        try:
            # Call the method
            description = "A test avatar description"
            result = RSIGenerator.generate_avatar(description, str(self.test_avatar_path))
            
            # Verify DALL-E was called as fallback
            mock_dalle.assert_called_once()
        finally:
            if 'HF_TOKEN' in os.environ:
                del os.environ['HF_TOKEN']
    
    def test_generate_avatar_creates_directory(self):
        """Test that generate_avatar creates output directory if it doesn't exist."""
        from agent_zero_framework.python.helpers.rsi_generator import RSIGenerator
        
        # Use a path in a non-existent subdirectory
        nested_path = Path(self.test_dir) / "subdir" / "avatar.png"
        
        with patch('agent_zero_framework.python.helpers.rsi_generator.RSIGenerator._generate_via_flux') as mock_flux:
            mock_flux.return_value = True
            
            # Call the method
            RSIGenerator.generate_avatar("test", str(nested_path))
            
            # Verify directory was created
            assert nested_path.parent.exists()
    
    @patch('agent_zero_framework.python.helpers.rsi_generator.OpenAI')
    @patch('agent_zero_framework.python.helpers.rsi_generator.requests')
    def test_generate_via_dalle_success(self, mock_requests, mock_openai_class):
        """Test successful generation via DALL-E."""
        from agent_zero_framework.python.helpers.rsi_generator import RSIGenerator
        
        # Mock OpenAI client
        mock_client = Mock()
        mock_response = Mock()
        mock_image_data = Mock()
        mock_image_data.url = "https://example.com/image.png"
        mock_response.data = [mock_image_data]
        mock_client.images.generate.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        # Mock requests.get
        mock_img_response = Mock()
        mock_img_response.content = b"fake_image_data"
        mock_img_response.raise_for_status = Mock()
        mock_requests.get.return_value = mock_img_response
        
        os.environ['OPENAI_API_KEY'] = 'test_key'
        
        try:
            # Call the method
            result = RSIGenerator._generate_via_dalle(
                "test prompt",
                self.test_avatar_path
            )
            
            # Verify
            assert result is True
            mock_client.images.generate.assert_called_once()
            mock_requests.get.assert_called_once()
        finally:
            if 'OPENAI_API_KEY' in os.environ:
                del os.environ['OPENAI_API_KEY']
    
    def test_generate_via_dalle_no_api_key(self):
        """Test DALL-E generation fails gracefully without API key."""
        from agent_zero_framework.python.helpers.rsi_generator import RSIGenerator
        
        # Ensure no API key
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        
        # Should return False without crashing
        result = RSIGenerator._generate_via_dalle(
            "test prompt",
            self.test_avatar_path
        )
        
        assert result is False
    
    @patch('agent_zero_framework.python.helpers.rsi_generator.InferenceClient')
    def test_generate_via_flux_no_token(self, mock_inference_client):
        """Test Flux generation works without HF_TOKEN (tries anyway)."""
        from agent_zero_framework.python.helpers.rsi_generator import RSIGenerator
        
        # Remove token
        if 'HF_TOKEN' in os.environ:
            del os.environ['HF_TOKEN']
        if 'HUGGINGFACE_TOKEN' in os.environ:
            del os.environ['HUGGINGFACE_TOKEN']
        
        # Mock client to succeed
        mock_client = Mock()
        mock_image = Mock()
        mock_image.save = Mock()
        mock_client.text_to_image.return_value = mock_image
        mock_inference_client.return_value = mock_client
        
        # Should still try to generate
        result = RSIGenerator._generate_via_flux(
            "test prompt",
            self.test_avatar_path
        )
        
        # Verify it was attempted
        mock_inference_client.assert_called_once()
