"""
Cloud Deployer for Uatu Genesis Engine

Handles deployment of AI personas to Hugging Face Spaces.
This module performs actual cloud deployments, not simulations.

**OPERATIONAL CONTEXT:**
Converting local AI persona generators into cloud-deployment engines.
This code executes real uploads to Hugging Face Spaces.
"""
import os
import tempfile
from pathlib import Path
from typing import Optional
from huggingface_hub import HfApi
from huggingface_hub.utils import HfHubHTTPError


class AuthenticationError(Exception):
    """Raised when Hugging Face authentication fails."""
    pass


class CloudDeployer:
    """
    Cloud deployment engine for AI personas.
    
    Deploys AI personas to Hugging Face Spaces as containerized applications.
    """
    
    def __init__(self, hf_token: str):
        """
        Initialize CloudDeployer with Hugging Face authentication.
        
        Args:
            hf_token: Hugging Face API token
            
        Raises:
            AuthenticationError: If token is invalid
        """
        self.api = HfApi(token=hf_token)
        self.hf_token = hf_token
        
        # Validate token immediately
        try:
            self.user_info = self.api.whoami()
        except HfHubHTTPError as e:
            raise AuthenticationError(f"Invalid Hugging Face token: {e}")
        except Exception as e:
            raise AuthenticationError(f"Authentication failed: {e}")
    
    def _check_or_create_space(self, space_name: str) -> str:
        """
        Check if Space exists, create if it doesn't.
        
        Args:
            space_name: Full space name (e.g., 'username/space-name')
            
        Returns:
            Space ID (repo_id)
        """
        try:
            # Try to get space info
            space_info = self.api.space_info(repo_id=space_name)
            return space_info.id
        except HfHubHTTPError as e:
            # Space doesn't exist (404), create it
            if e.response.status_code == 404:
                space_info = self.api.create_repo(
                    repo_id=space_name,
                    repo_type="space",
                    space_sdk="docker",
                    exist_ok=True
                )
                return space_name
            else:
                # Other HTTP errors should be re-raised
                raise
    
    def _generate_dockerfile(self, persona_path: str, launch_script: str) -> str:
        """
        Generate Dockerfile for persona deployment.
        
        Args:
            persona_path: Relative path to persona directory (e.g., 'personas/lucius_fox')
            launch_script: Name of the launch script (e.g., 'launch_lucius_fox.py')
            
        Returns:
            Dockerfile content as string
        """
        dockerfile = f"""FROM python:3.10

# Set working directory
WORKDIR /app

# Copy persona files
COPY {persona_path} /app/{persona_path}

# Copy agent zero framework
COPY agent_zero_framework /app/agent_zero_framework

# Copy requirements
COPY requirements.txt /app/requirements.txt
COPY agent_zero_framework/requirements.txt /app/agent_zero_framework_requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt
RUN pip install --no-cache-dir -r /app/agent_zero_framework_requirements.txt

# Expose Hugging Face default port
EXPOSE 7860

# Set environment variable for Hugging Face Spaces
ENV GRADIO_SERVER_NAME="0.0.0.0"
ENV GRADIO_SERVER_PORT=7860

# Run the launch script
CMD ["python", "/app/{persona_path}/{launch_script}"]
"""
        return dockerfile
    
    def deploy_persona(
        self, 
        persona_path: str, 
        token: Optional[str] = None, 
        target_space_name: Optional[str] = None
    ) -> str:
        """
        Deploy a persona to Hugging Face Spaces.
        
        This method performs the actual deployment:
        1. Validates authentication
        2. Creates or verifies the Space
        3. Generates Dockerfile
        4. Uploads all required files
        
        Args:
            persona_path: Path to persona directory (e.g., 'agent_zero_framework/personas/lucius_fox')
            token: Optional override token (uses instance token if None)
            target_space_name: Target space name (e.g., 'username/Lucius-Fox-Node')
                              If None, auto-generates from persona name
            
        Returns:
            URL of the deployed Space
            
        Raises:
            ValueError: If persona path doesn't exist
            AuthenticationError: If authentication fails
        """
        # Use provided token or instance token
        if token:
            # Validate new token
            try:
                api = HfApi(token=token)
                user_info = api.whoami()
            except Exception as e:
                raise AuthenticationError(f"Invalid token: {e}")
        else:
            api = self.api
            user_info = self.user_info
        
        # Validate persona path
        full_persona_path = Path(persona_path)
        if not full_persona_path.exists():
            raise ValueError(f"Persona path does not exist: {persona_path}")
        
        # Get persona name from path
        persona_name = full_persona_path.name
        
        # Generate space name if not provided
        if not target_space_name:
            username = user_info.get('name') or user_info.get('id')
            target_space_name = f"{username}/{persona_name.replace('_', '-').title()}-Node"
        
        # Check or create space
        space_id = self._check_or_create_space(target_space_name)
        
        # Find launch script
        launch_scripts = list(full_persona_path.glob("launch_*.py"))
        if not launch_scripts:
            raise ValueError(f"No launch script found in {persona_path}")
        launch_script = launch_scripts[0].name
        
        # Generate Dockerfile
        # Use relative path for Dockerfile
        rel_persona_path = str(full_persona_path)
        dockerfile_content = self._generate_dockerfile(rel_persona_path, launch_script)
        
        # Create temporary Dockerfile using secure tempfile
        temp_dockerfile = None
        try:
            # Use tempfile for secure cross-platform temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.Dockerfile', delete=False) as tf:
                tf.write(dockerfile_content)
                temp_dockerfile = Path(tf.name)
            
            # Get repo root (assumes we're running from repo root or subdirectory)
            repo_root = Path.cwd()
            if not (repo_root / "uatu_genesis_engine").exists():
                # Try parent directories
                for parent in Path.cwd().parents:
                    if (parent / "uatu_genesis_engine").exists():
                        repo_root = parent
                        break
            
            # Upload Dockerfile
            api.upload_file(
                path_or_fileobj=str(temp_dockerfile),
                path_in_repo="Dockerfile",
                repo_id=space_id,
                repo_type="space"
            )
        finally:
            # Clean up temp file
            if temp_dockerfile and temp_dockerfile.exists():
                temp_dockerfile.unlink()
        
        # Upload persona directory
        api.upload_folder(
            folder_path=str(full_persona_path),
            path_in_repo=rel_persona_path,
            repo_id=space_id,
            repo_type="space"
        )
        
        # Upload agent_zero_framework
        agent_zero_path = repo_root / "agent_zero_framework"
        if agent_zero_path.exists():
            api.upload_folder(
                folder_path=str(agent_zero_path),
                path_in_repo="agent_zero_framework",
                repo_id=space_id,
                repo_type="space",
                ignore_patterns=[".*", "__pycache__", "*.pyc", "logs/", "memory/", "tmp/", "usr/"]
            )
        
        # Upload requirements.txt from repo root
        requirements_path = repo_root / "requirements.txt"
        if requirements_path.exists():
            api.upload_file(
                path_or_fileobj=str(requirements_path),
                path_in_repo="requirements.txt",
                repo_id=space_id,
                repo_type="space"
            )
        
        # Upload agent_zero requirements if it exists
        agent_zero_requirements = agent_zero_path / "requirements.txt"
        if agent_zero_requirements.exists():
            api.upload_file(
                path_or_fileobj=str(agent_zero_requirements),
                path_in_repo="agent_zero_framework/requirements.txt",
                repo_id=space_id,
                repo_type="space"
            )
        
        # Return Space URL
        space_url = f"https://huggingface.co/spaces/{space_id}"
        return space_url
