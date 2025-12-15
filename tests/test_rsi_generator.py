"""
Unit tests for RSI Generator

Tests the avatar generation system using High-Fidelity Flux via HF Space API.
"""
import os
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from agent_zero_framework.python.helpers import rsi_generator


class TestDescribeSelf:
    """Test the describe_self function."""
    
    def test_describe_self_returns_prompt(self):
        """Test that describe_self returns a valid prompt."""
        result = rsi_generator.describe_self()
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "physical appearance" in result.lower()
        assert "Construct" in result
    
    def test_describe_self_with_memory(self):
        """Test describe_self with memory parameter."""
        memory = {"test": "data"}
        result = rsi_generator.describe_self(memory)
        
        assert isinstance(result, str)
        assert len(result) > 0


class TestGenerateAvatar:
    """Test the generate_avatar function."""
    
    @patch('huggingface_hub.InferenceClient')
    @patch('agent_zero_framework.python.helpers.rsi_generator.Path')
    def test_generate_avatar_success(self, mock_path, mock_client_class):
        """Test successful avatar generation."""
        # Mock the InferenceClient
        mock_client = Mock()
        mock_image = Mock()
        mock_client.text_to_image.return_value = mock_image
        mock_client_class.return_value = mock_client
        
        # Mock Path operations
        mock_output_path = Mock()
        mock_output_path.parent.mkdir = Mock()
        mock_path.return_value = mock_output_path
        
        # Call function
        result = rsi_generator.generate_avatar(
            prompt="A test description",
            output_path="/tmp/test_avatar.png"
        )
        
        assert result is True
        mock_client.text_to_image.assert_called_once()
        mock_image.save.assert_called_once()
        
        # Verify parameters
        call_kwargs = mock_client.text_to_image.call_args[1]
        assert "model" in call_kwargs
        assert call_kwargs["model"] == "black-forest-labs/FLUX.1-dev"
        assert "num_inference_steps" in call_kwargs
        assert "guidance_scale" in call_kwargs
    
    def test_generate_avatar_import_error(self):
        """Test handling of import errors."""
        # Temporarily remove huggingface_hub from sys.modules
        import sys
        original_module = sys.modules.get('huggingface_hub')
        
        try:
            # Hide the module
            if 'huggingface_hub' in sys.modules:
                del sys.modules['huggingface_hub']
            
            # Patch the import to fail
            with patch.dict('sys.modules', {'huggingface_hub': None}):
                result = rsi_generator.generate_avatar(
                    prompt="Test prompt",
                    output_path="/tmp/test.png"
                )
                
                assert result is False
        finally:
            # Restore the module
            if original_module is not None:
                sys.modules['huggingface_hub'] = original_module
    
    @patch('huggingface_hub.InferenceClient')
    @patch('agent_zero_framework.python.helpers.rsi_generator.Path')
    def test_generate_avatar_api_error(self, mock_path, mock_client_class):
        """Test handling of API errors."""
        # Mock client that throws an error
        mock_client = Mock()
        mock_client.text_to_image.side_effect = Exception("API Error")
        mock_client_class.return_value = mock_client
        
        # Mock Path operations
        mock_output_path = Mock()
        mock_path.return_value = mock_output_path
        
        result = rsi_generator.generate_avatar(
            prompt="Test prompt",
            output_path="/tmp/test.png"
        )
        
        assert result is False
    
    @patch('huggingface_hub.InferenceClient')
    @patch('agent_zero_framework.python.helpers.rsi_generator.Path')
    def test_generate_avatar_with_custom_parameters(self, mock_path, mock_client_class):
        """Test avatar generation with custom parameters."""
        mock_client = Mock()
        mock_image = Mock()
        mock_client.text_to_image.return_value = mock_image
        mock_client_class.return_value = mock_client
        
        mock_output_path = Mock()
        mock_output_path.parent.mkdir = Mock()
        mock_path.return_value = mock_output_path
        
        # Call with custom parameters
        result = rsi_generator.generate_avatar(
            prompt="Custom description",
            output_path="/custom/path.png",
            steps=30,
            guidance=4.0,
            width=512,
            height=512
        )
        
        assert result is True
        
        # Verify custom parameters were used
        call_kwargs = mock_client.text_to_image.call_args[1]
        assert call_kwargs["num_inference_steps"] == 30
        assert call_kwargs["guidance_scale"] == 4.0
        assert call_kwargs["width"] == 512
        assert call_kwargs["height"] == 512
    
    @patch('huggingface_hub.InferenceClient')
    @patch('agent_zero_framework.python.helpers.rsi_generator.Path')
    def test_generate_avatar_adds_style_prefix(self, mock_path, mock_client_class):
        """Test that avatar generation adds style prefix to prompt."""
        mock_client = Mock()
        mock_image = Mock()
        mock_client.text_to_image.return_value = mock_image
        mock_client_class.return_value = mock_client
        
        mock_output_path = Mock()
        mock_output_path.parent.mkdir = Mock()
        mock_path.return_value = mock_output_path
        
        original_prompt = "A simple description"
        result = rsi_generator.generate_avatar(
            prompt=original_prompt,
            output_path="/tmp/test.png"
        )
        
        assert result is True
        
        # Verify style prefix was added
        call_args = mock_client.text_to_image.call_args
        used_prompt = call_args[1]["prompt"]
        assert "Cinematic lighting" in used_prompt
        assert "hyper-realistic" in used_prompt
        assert original_prompt in used_prompt


class TestEnsureAvatarExists:
    """Test the ensure_avatar_exists function."""
    
    @patch('agent_zero_framework.python.helpers.rsi_generator.Path')
    def test_ensure_avatar_exists_already_exists(self, mock_path_class):
        """Test when avatar already exists."""
        # Mock avatar path that exists
        mock_avatar_path = Mock()
        mock_avatar_path.exists.return_value = True
        mock_path_class.return_value = mock_avatar_path
        
        result = rsi_generator.ensure_avatar_exists()
        
        assert result is True
        # Should not attempt to generate
        mock_avatar_path.exists.assert_called_once()
    
    @patch('agent_zero_framework.python.helpers.rsi_generator.generate_avatar')
    @patch('agent_zero_framework.python.helpers.rsi_generator.Path')
    def test_ensure_avatar_exists_generates_new(self, mock_path_class, mock_generate):
        """Test when avatar needs to be generated."""
        # Mock avatar path that doesn't exist
        mock_avatar_path = Mock()
        mock_avatar_path.exists.return_value = False
        mock_path_class.return_value = mock_avatar_path
        
        # Mock successful generation
        mock_generate.return_value = True
        
        result = rsi_generator.ensure_avatar_exists()
        
        assert result is True
        mock_generate.assert_called_once()
    
    @patch('agent_zero_framework.python.helpers.rsi_generator.generate_avatar')
    @patch('agent_zero_framework.python.helpers.rsi_generator.Path')
    def test_ensure_avatar_exists_generation_fails(self, mock_path_class, mock_generate):
        """Test when avatar generation fails."""
        mock_avatar_path = Mock()
        mock_avatar_path.exists.return_value = False
        mock_path_class.return_value = mock_avatar_path
        
        # Mock failed generation
        mock_generate.return_value = False
        
        result = rsi_generator.ensure_avatar_exists()
        
        assert result is False
    
    @patch('agent_zero_framework.python.helpers.rsi_generator.generate_avatar')
    @patch('agent_zero_framework.python.helpers.rsi_generator.Path')
    def test_ensure_avatar_exists_force_regenerate(self, mock_path_class, mock_generate):
        """Test force regeneration even when avatar exists."""
        mock_avatar_path = Mock()
        mock_avatar_path.exists.return_value = True
        mock_path_class.return_value = mock_avatar_path
        
        mock_generate.return_value = True
        
        result = rsi_generator.ensure_avatar_exists(force_regenerate=True)
        
        assert result is True
        # Should generate even though it exists
        mock_generate.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
