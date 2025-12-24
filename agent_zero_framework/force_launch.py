import os
import sys

# --- THE HARDWIRE SECTION ---
# Prefer environment or .env-managed secrets for API keys.
openrouter_key = os.environ.get("OPENROUTER_API_KEY")
if not openrouter_key:
    try:
        from dotenv import load_dotenv
        load_dotenv()
        openrouter_key = os.environ.get("OPENROUTER_API_KEY")
    except Exception:
        openrouter_key = None

if openrouter_key:
    os.environ["OPENROUTER_API_KEY"] = openrouter_key
    print(f"✅ DIAGNOSTIC: OPENROUTER_API_KEY loaded. First 10 chars: {openrouter_key[:10]}...")
else:
    print("⚠️ DIAGNOSTIC: OPENROUTER_API_KEY not set. Set OPENROUTER_API_KEY in environment or .env to enable OpenRouter integrations.")

# Default base and model; these may be overridden by environment variables
os.environ.setdefault("OPENROUTER_API_BASE", "https://openrouter.ai/api/v1")
os.environ.setdefault("CHAT_MODEL", "z-ai/glm-4.7")
os.environ.setdefault("WEB_UI_HOST", "0.0.0.0")
print(f"✅ DIAGNOSTIC: Target Model: {os.environ['CHAT_MODEL']}")

# --- THE PATHFINDER SECTION ---
# We force Python to see the framework
current_dir = os.getcwd()
sys.path.append(current_dir)
print(f"✅ DIAGNOSTIC: Working Directory: {current_dir}")

# --- THE LAUNCH ---
try:
    print("🚀 IGNITION SEQUENCE STARTING...")
    from personas.agent import launch_agent
    
    # Apply the "Main = Run" patch dynamically just in case
    import run_ui
    if not hasattr(run_ui, 'main'):
        run_ui.main = run_ui.run
        
    launch_agent.main()
except ImportError as e:
    print(f"❌ CRITICAL ERROR: {e}")
    print("Run this command first: export PYTHONPATH=$(pwd)")
except Exception as e:
    print(f"❌ RUNTIME ERROR: {e}")
