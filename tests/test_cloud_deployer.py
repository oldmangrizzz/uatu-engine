"""
Unit tests for CloudDeployer

Tests the cloud deployment system for AI personas to Hugging Face Spaces.
"""
import os
import pytest
from unittest.mock import Mock, patch
from uatu_genesis_engine.deployment.cloud_deployer import CloudDeployer, AuthenticationError


class TestAuthenticationError:
    """Test the AuthenticationError exception."""
    
    def test_exception_creation(self):
        """Test that AuthenticationError can be raised."""
        with pytest.raises(AuthenticationError):
            raise AuthenticationError("Test error")
    
    def test_exception_message(self):
        """Test that exception message is preserved."""
        try:
            raise AuthenticationError("Custom message")
        except AuthenticationError as e:
            assert str(e) == "Custom message"


class TestCloudDeployer:
    """Test the CloudDeployer class."""
    
    @patch('uatu_genesis_engine.deployment.cloud_deployer.HfApi')
    def test_initialization_success(self, mock_hf_api):
        """Test successful initialization with valid token."""
        # Mock successful authentication
        mock_api_instance = Mock()
        mock_api_instance.whoami.return_value = {"name": "testuser", "id": "user123"}
        mock_hf_api.return_value = mock_api_instance
        
        deployer = CloudDeployer(hf_token="valid_token")
        
        assert deployer.hf_token == "valid_token"
        assert deployer.user_info == {"name": "testuser", "id": "user123"}
        mock_api_instance.whoami.assert_called_once()
    
    @patch('uatu_genesis_engine.deployment.cloud_deployer.HfApi')
    def test_initialization_invalid_token(self, mock_hf_api):
        """Test initialization with invalid token raises AuthenticationError."""
        # Mock failed authentication
        mock_api_instance = Mock()
        mock_api_instance.whoami.side_effect = Exception("Invalid token")
        mock_hf_api.return_value = mock_api_instance
        
        with pytest.raises(AuthenticationError) as exc_info:
            CloudDeployer(hf_token="invalid_token")
        
        assert "Authentication failed" in str(exc_info.value)
    
    @patch('uatu_genesis_engine.deployment.cloud_deployer.HfApi')
    def test_check_or_create_space_existing(self, mock_hf_api):
        """Test _check_or_create_space when space already exists."""
        # Mock successful authentication
        mock_api_instance = Mock()
        mock_api_instance.whoami.return_value = {"name": "testuser"}
        mock_space_info = Mock()
        mock_space_info.id = "testuser/test-space"
        mock_api_instance.space_info.return_value = mock_space_info
        mock_hf_api.return_value = mock_api_instance
        
        deployer = CloudDeployer(hf_token="valid_token")
        space_id = deployer._check_or_create_space("testuser/test-space")
        
        assert space_id == "testuser/test-space"
        mock_api_instance.space_info.assert_called_once_with(repo_id="testuser/test-space")
    
    @patch('uatu_genesis_engine.deployment.cloud_deployer.HfApi')
    def test_check_or_create_space_new(self, mock_hf_api):
        """Test _check_or_create_space creates new space if it doesn't exist."""
        from huggingface_hub.utils import HfHubHTTPError
        
        # Mock successful authentication
        mock_api_instance = Mock()
        mock_api_instance.whoami.return_value = {"name": "testuser"}
        
        # Create a mock 404 response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_api_instance.space_info.side_effect = HfHubHTTPError("Space not found", response=mock_response)
        mock_api_instance.create_repo.return_value = "testuser/new-space"
        mock_hf_api.return_value = mock_api_instance
        
        deployer = CloudDeployer(hf_token="valid_token")
        space_id = deployer._check_or_create_space("testuser/new-space")
        
        assert space_id == "testuser/new-space"
        mock_api_instance.create_repo.assert_called_once_with(
            repo_id="testuser/new-space",
            repo_type="space",
            space_sdk="docker",
            exist_ok=True
        )
    
    @patch('uatu_genesis_engine.deployment.cloud_deployer.HfApi')
    def test_check_or_create_space_non_404_error(self, mock_hf_api):
        """Test _check_or_create_space re-raises non-404 errors."""
        from huggingface_hub.utils import HfHubHTTPError
        
        # Mock successful authentication
        mock_api_instance = Mock()
        mock_api_instance.whoami.return_value = {"name": "testuser"}
        
        # Create a mock 500 response (server error)
        mock_response = Mock()
        mock_response.status_code = 500
        mock_api_instance.space_info.side_effect = HfHubHTTPError("Server error", response=mock_response)
        mock_hf_api.return_value = mock_api_instance
        
        deployer = CloudDeployer(hf_token="valid_token")
        
        # Should re-raise the error instead of trying to create space
        with pytest.raises(HfHubHTTPError) as exc_info:
            deployer._check_or_create_space("testuser/test-space")
        
        assert "Server error" in str(exc_info.value)
        # create_repo should NOT be called for non-404 errors
        mock_api_instance.create_repo.assert_not_called()
    
    @patch('uatu_genesis_engine.deployment.cloud_deployer.HfApi')
    def test_generate_dockerfile(self, mock_hf_api):
        """Test Dockerfile generation with all new features."""
        # Mock successful authentication
        mock_api_instance = Mock()
        mock_api_instance.whoami.return_value = {"name": "testuser"}
        mock_hf_api.return_value = mock_api_instance
        
        deployer = CloudDeployer(hf_token="valid_token")
        dockerfile = deployer._generate_dockerfile(
            persona_path="personas/test_persona",
            launch_script="launch_test_persona.py"
        )
        
        # Check key elements in Dockerfile
        assert "FROM python:3.10" in dockerfile
        assert "COPY personas/test_persona" in dockerfile
        assert "COPY agent_zero_framework" in dockerfile
        assert "COPY requirements.txt" in dockerfile
        assert "EXPOSE 7860" in dockerfile
        assert "ENV GRADIO_SERVER_NAME" in dockerfile
        assert "ENV GRADIO_SERVER_PORT=7860" in dockerfile
        
        # Check Phase 1: Audio drivers
        assert "apt-get update" in dockerfile
        assert "ffmpeg" in dockerfile
        assert "libsndfile1" in dockerfile
        assert "libportaudio2" in dockerfile
        assert "git" in dockerfile
        assert "build-essential" in dockerfile
        
        # Check Phase 3: Persona prompt injection
        assert "rm -rf /app/agent_zero_framework/agents/agent0/prompts/*" in dockerfile
        assert "COPY personas/test_persona/prompts/" in dockerfile
        
        # Check Phase 5: Genesis launch script
        assert "COPY genesis_launch.py" in dockerfile
        assert 'CMD ["python", "/app/personas/test_persona/genesis_launch.py"]' in dockerfile
    
    @patch('uatu_genesis_engine.deployment.cloud_deployer.HfApi')
    def test_generate_launch_script(self, mock_hf_api):
        """Test genesis launch script generation."""
        # Mock successful authentication
        mock_api_instance = Mock()
        mock_api_instance.whoami.return_value = {"name": "testuser"}
        mock_hf_api.return_value = mock_api_instance
        
        deployer = CloudDeployer(hf_token="valid_token")
        launch_script = deployer._generate_launch_script(
            persona_path="personas/test_persona",
            original_launch_script="launch_test_persona.py"
        )
        
        # Check key elements in launch script
        assert "#!/usr/bin/env python3" in launch_script
        assert "Genesis Integration" in launch_script
        assert "genesis_sequence()" in launch_script
        
        # Check Phase 4: RSI/Avatar generation
        assert "ensure_avatar_exists" in launch_script
        assert "FORGING PHYSICAL FORM VIA FLUX" in launch_script
        assert "/app/persona_data/avatar.png" in launch_script
        
        # Check Phase 5: Construct narrative loading
        assert "construct.txt" in launch_script
        assert "CONSTRUCT_NARRATIVE" in launch_script
        assert "LOADING CONSTRUCT NARRATIVE" in launch_script
        
        # Check it runs agent zero
        assert "from run_ui import run" in launch_script
        assert "run()" in launch_script
    
    @patch('uatu_genesis_engine.deployment.cloud_deployer.HfApi')
    def test_deploy_persona_invalid_path(self, mock_hf_api):
        """Test deploy_persona with invalid persona path."""
        # Mock successful authentication
        mock_api_instance = Mock()
        mock_api_instance.whoami.return_value = {"name": "testuser"}
        mock_hf_api.return_value = mock_api_instance
        
        deployer = CloudDeployer(hf_token="valid_token")
        
        with pytest.raises(ValueError) as exc_info:
            deployer.deploy_persona(
                persona_path="/nonexistent/path",
                target_space_name="testuser/test-space"
            )
        
        assert "does not exist" in str(exc_info.value)
    
    @patch('uatu_genesis_engine.deployment.cloud_deployer.HfApi')
    def test_deploy_persona_no_launch_script(self, mock_hf_api, tmp_path):
        """Test deploy_persona when no launch script is found."""
        # Mock successful authentication
        mock_api_instance = Mock()
        mock_api_instance.whoami.return_value = {"name": "testuser"}
        mock_hf_api.return_value = mock_api_instance
        
        # Create a temporary persona directory without launch script
        persona_dir = tmp_path / "test_persona"
        persona_dir.mkdir()
        (persona_dir / "config.yaml").write_text("test: config")
        
        deployer = CloudDeployer(hf_token="valid_token")
        
        with pytest.raises(ValueError) as exc_info:
            deployer.deploy_persona(
                persona_path=str(persona_dir),
                target_space_name="testuser/test-space"
            )
        
        assert "No launch script found" in str(exc_info.value)
    
    @patch('uatu_genesis_engine.deployment.cloud_deployer.HfApi')
    def test_deploy_persona_success(self, mock_hf_api, tmp_path):
        """Test successful persona deployment."""
        # Mock successful authentication
        mock_api_instance = Mock()
        mock_api_instance.whoami.return_value = {"name": "testuser", "id": "testuser"}
        mock_space_info = Mock()
        mock_space_info.id = "testuser/Test-Persona-Node"
        mock_api_instance.space_info.return_value = mock_space_info
        mock_hf_api.return_value = mock_api_instance
        
        # Create temporary persona directory with launch script
        persona_dir = tmp_path / "test_persona"
        persona_dir.mkdir()
        launch_script = persona_dir / "launch_test_persona.py"
        launch_script.write_text("# Launch script")
        
        # Create mock directory structure
        (tmp_path / "uatu_genesis_engine").mkdir()
        (tmp_path / "agent_zero_framework").mkdir()
        (tmp_path / "requirements.txt").write_text("test")
        (tmp_path / "agent_zero_framework" / "requirements.txt").write_text("test")
        
        deployer = CloudDeployer(hf_token="valid_token")
        
        # Change to temp directory
        orig_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            url = deployer.deploy_persona(
                persona_path=str(persona_dir),
                target_space_name="testuser/Test-Persona-Node"
            )
            
            assert url == "https://huggingface.co/spaces/testuser/Test-Persona-Node"
            assert mock_api_instance.upload_file.called
            assert mock_api_instance.upload_folder.called
        finally:
            os.chdir(orig_cwd)
    
    @patch('uatu_genesis_engine.deployment.cloud_deployer.HfApi')
    def test_deploy_persona_with_override_token(self, mock_hf_api):
        """Test deploy_persona with token override."""
        # Mock successful authentication for both tokens
        mock_api_instance = Mock()
        mock_api_instance.whoami.return_value = {"name": "testuser"}
        mock_hf_api.return_value = mock_api_instance
        
        deployer = CloudDeployer(hf_token="original_token")
        
        # Test that providing a new token creates a new API instance
        with pytest.raises(ValueError):  # Will fail on path validation
            deployer.deploy_persona(
                persona_path="/nonexistent",
                token="new_token"
            )
        
        # Verify whoami was called for the new token
        assert mock_hf_api.call_count >= 2  # Once for init, once for override
    
    @patch('uatu_genesis_engine.deployment.cloud_deployer.HfApi')
    def test_deploy_persona_auto_space_name(self, mock_hf_api, tmp_path):
        """Test deploy_persona auto-generates space name when not provided."""
        from huggingface_hub.utils import HfHubHTTPError
        
        # Mock successful authentication
        mock_api_instance = Mock()
        mock_api_instance.whoami.return_value = {"name": "testuser", "id": "testuser"}
        
        # Create a mock 404 response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_api_instance.space_info.side_effect = HfHubHTTPError("Not found", response=mock_response)
        mock_api_instance.create_repo.return_value = "testuser/Test-Persona-Node"
        mock_hf_api.return_value = mock_api_instance
        
        # Create temporary persona directory
        persona_dir = tmp_path / "test_persona"
        persona_dir.mkdir()
        launch_script = persona_dir / "launch_test.py"
        launch_script.write_text("# Launch")
        
        # Create mock agent_zero and requirements
        (tmp_path / "agent_zero_framework").mkdir()
        (tmp_path / "requirements.txt").write_text("test")
        
        deployer = CloudDeployer(hf_token="valid_token")
        
        with patch('pathlib.Path.cwd', return_value=tmp_path), \
             patch('pathlib.Path.unlink'):
            
            url = deployer.deploy_persona(persona_path=str(persona_dir))
        
        # Verify create_repo was called with auto-generated name
        calls = mock_api_instance.create_repo.call_args_list
        assert len(calls) > 0
        # The space name should contain the persona name
        assert "test-persona" in calls[0][1]["repo_id"].lower() or "test_persona" in calls[0][1]["repo_id"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
