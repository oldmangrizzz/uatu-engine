# Cloud Deployer

Deployment module for Uatu Genesis Engine that handles cloud deployment of AI personas to Hugging Face Spaces.

## Features

- **Authentication**: Validates Hugging Face tokens immediately via `HfApi.whoami()`
- **Space Management**: Automatically creates or verifies Hugging Face Spaces
- **Containerization**: Programmatically generates Dockerfiles for persona deployment
- **Secure File Handling**: Uses `tempfile` for cross-platform secure temporary file creation
- **Complete Upload**: Uploads persona files, agent framework, and dependencies to Hugging Face

## Usage

### Basic Example

```python
from uatu_genesis_engine.deployment import CloudDeployer, AuthenticationError
import os

# Get your Hugging Face token
hf_token = os.environ.get("HF_TOKEN")

try:
    # Initialize deployer (validates token immediately)
    deployer = CloudDeployer(hf_token=hf_token)
    
    # Deploy a persona to Hugging Face Spaces
    url = deployer.deploy_persona(
        persona_path="agent_zero_framework/personas/lucius_fox",
        target_space_name="username/Lucius-Fox-Node"  # Optional, auto-generates if None
    )
    
    print(f"Deployment complete: {url}")
    
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
```

### Getting a Hugging Face Token

1. Go to https://huggingface.co/settings/tokens
2. Create a new token with write access
3. Set it as an environment variable: `export HF_TOKEN='your_token_here'`

### Auto-Generated Space Names

If you don't provide a `target_space_name`, the deployer will automatically generate one based on:
- Your Hugging Face username
- The persona name from the directory

Example: `personas/lucius_fox` → `username/Lucius-Fox-Node`

## Technical Details

### Generated Dockerfile

The deployer creates a Dockerfile that:
- Uses `python:3.10` as the base image
- Copies persona files and agent framework
- Installs all dependencies from `requirements.txt`
- Exposes port 7860 (Hugging Face Spaces default)
- Sets up Gradio server configuration
- Runs the persona's launch script

### Uploaded Files

The deployment process uploads:
1. Generated Dockerfile
2. Persona directory (with config, prompts, launch script)
3. Agent Zero framework (excluding logs, memory, temp files)
4. Repository requirements.txt
5. Agent Zero framework requirements.txt

## Error Handling

The CloudDeployer raises specific exceptions for different error scenarios:

- `AuthenticationError`: Invalid or expired Hugging Face token
- `ValueError`: Invalid persona path or missing launch script
- `HfHubHTTPError`: Hugging Face API errors (re-raised for non-404 errors)

## Security

- Uses `tempfile.NamedTemporaryFile()` for secure temporary file creation
- Validates tokens immediately during initialization
- Properly handles and re-raises API errors
- Cleans up temporary files automatically

## Testing

Run the test suite:

```bash
pytest tests/test_cloud_deployer.py -v
```

Current test coverage: 13 test cases covering:
- Authentication (valid/invalid tokens)
- Space creation and verification
- Dockerfile generation
- Deployment workflow
- Error handling
- Auto-generated space names

## Example Script

See `example_deploy.py` for a complete example with error handling and best practices.
