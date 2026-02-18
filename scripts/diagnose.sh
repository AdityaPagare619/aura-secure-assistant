#!/bin/bash
# Simple Aura Diagnostic

echo "=========================================="
echo "🔍 AURA DIAGNOSTIC"
echo "=========================================="

AURA_DIR="$HOME/aura-secure-assistant"
LLAMA_DIR="$HOME/llama.cpp"

# 1. Check Aura code
echo ""
echo "[1] Checking Aura code..."
if [ -f "$AURA_DIR/main.py" ]; then
    echo "✅ main.py exists"
else
    echo "❌ main.py NOT FOUND"
    echo "   Run: git clone https://github.com/AdityaPagare619/aura-secure-assistant.git"
    exit 1
fi

# 2. Check Python
echo ""
echo "[2] Python..."
python --version

# 3. Check llama-cli
echo ""
echo "[3] Checking llama-cli..."
if [ -f "$LLAMA_DIR/llama-cli" ]; then
    echo "✅ Found: $LLAMA_DIR/llama-cli"
elif [ -f "$LLAMA_DIR/build/llama-cli" ]; then
    echo "✅ Found: $LLAMA_DIR/build/llama-cli"
else
    echo "❌ llama-cli NOT FOUND"
    echo "   Looking in $LLAMA_DIR..."
    ls -la $LLAMA_DIR/ 2>/dev/null
fi

# 4. Check model
echo ""
echo "[4] Checking model..."
ls $LLAMA_DIR/models/ 2>/dev/null

# 5. Test LLM import
echo ""
echo "[5] Testing Python imports..."
cd $AURA_DIR
python -c "
import sys
sys.path.insert(0, '.')
try:
    from src.agent.llm import LLMInterface
    print('✅ LLM Interface imported')
except Exception as e:
    print(f'❌ LLM Error: {e}')
"

echo ""
echo "=========================================="
