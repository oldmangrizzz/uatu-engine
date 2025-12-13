#!/usr/bin/env python3
"""
Example usage of CloudDeployer

This script demonstrates how to deploy a persona to Hugging Face Spaces.
Note: You need a valid Hugging Face token to actually deploy.
"""
import os
from pathlib import Path
from uatu_genesis_engine.deployment import CloudDeployer, AuthenticationError


def main():
    """
    Example: Deploy Lucius Fox persona to Hugging Face Spaces
    """
    # Get token from environment (never hardcode tokens!)
    hf_token = os.environ.get("HF_TOKEN")
    
    if not hf_token:
        print("❌ HF_TOKEN environment variable not set")
        print("   Set it with: export HF_TOKEN='your_token_here'")
        print("   Get a token from: https://huggingface.co/settings/tokens")
        return
    
    try:
        # Initialize deployer
        print("🔐 Authenticating with Hugging Face...")
        deployer = CloudDeployer(hf_token=hf_token)
        print(f"✅ Authenticated as: {deployer.user_info.get('name')}")
        
        # Deploy persona
        persona_path = "agent_zero_framework/personas/lucius_fox"
        
        # Check if persona exists
        if not Path(persona_path).exists():
            print(f"❌ Persona not found at: {persona_path}")
            print("   Make sure you're running from the repository root")
            return
        
        print(f"\n🚀 Deploying persona from: {persona_path}")
        print("   This will:")
        print("   1. Create/verify Hugging Face Space")
        print("   2. Generate Dockerfile")
        print("   3. Upload persona files")
        print("   4. Upload agent framework")
        print("   5. Configure container")
        
        # Note: This would actually deploy if uncommented
        # url = deployer.deploy_persona(
        #     persona_path=persona_path,
        #     target_space_name=None  # Auto-generates name
        # )
        # print(f"\n✅ Deployment complete!")
        # print(f"   Space URL: {url}")
        
        print("\n⚠️  Actual deployment is commented out in this example")
        print("   Uncomment the deploy_persona() call to perform real deployment")
        
    except AuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
