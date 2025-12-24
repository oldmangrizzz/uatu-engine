#!/bin/bash

echo "================================================================"
echo "🔥 UATU ENGINE - AESTHETIC ENHANCEMENT"
echo "================================================================"
echo ""

# Check if HF_TOKEN is set
if [ -z "$HF_TOKEN" ]; then
    echo "⚠️  HF_TOKEN not set in environment"
    echo "   To enable RSI generation (avatar images), set:"
    echo "   export HF_TOKEN=your_huggingface_token_here"
    echo ""
    echo "   Get your token from: https://huggingface.co/settings/tokens"
    echo "   (Requires 'read' permissions)"
    echo ""
else
    echo "✓ HF_TOKEN is set - RSI generation enabled"
fi

echo ""
echo "🎨 Aesthetic Updates Applied:"
echo "  ✓ Login page redesigned with Workshop branding"
echo "  ✓ Dynamic persona loading (name, archetype, avatar)"
echo "  ✓ Enhanced CSS with glowing effects and gradients"
echo "  ✓ Persona info API endpoint created"
echo ""

echo "📋 Next Steps:"
echo "  1. Restart the server to see new login page:"
echo "     source venv/bin/activate"
echo "     python agent_zero_framework/personas/anthony_edward_stark/launch_anthony_edward_stark.py"
echo ""
echo "  2. Generate Tony Stark's RSI (avatar):"
echo "     export HF_TOKEN=your_token"
echo "     python test_rsi_generation.py"
echo ""
echo "  3. Open browser to http://localhost:8000"
echo "================================================================"
