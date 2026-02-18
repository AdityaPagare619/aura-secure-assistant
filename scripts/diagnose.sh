#!/bin/bash
# Aura Diagnostic Script - FIND THE EXACT PROBLEM

echo "=========================================="
echo "🔍 AURA DIAGNOSTIC - FINDING ROOT CAUSE"
echo "=========================================="

# Test 1: Check if code exists
echo ""
echo "[1/7] Checking Aura code..."
if [ -f "main.py" ]; then
    echo "✅ main.py exists"
else
    echo "❌ main.py NOT FOUND"
    exit 1
fi

# Test 2: Check Python
echo ""
echo "[2/7] Checking Python..."
python --version
if [ $? -eq 0 ]; then
    echo "✅ Python works"
else
    echo "❌ Python broken"
    exit 1
fi

# Test 3: Check dependencies
echo ""
echo "[3/7] Checking dependencies..."
python -c "import telegram" 2>/dev/null && echo "✅ telegram installed" || echo "❌ telegram missing"
python -c "import yaml" 2>/dev/null && echo "✅ yaml installed" || echo "❌ yaml missing"

# Test 4: Check llama.cpp
echo ""
echo "[4/7] Checking llama.cpp..."
if [ -f "~/llama.cpp/llama-cli" ]; then
    echo "✅ llama-cli exists at ~/llama.cpp/llama-cli"
    ls -la ~/llama.cpp/llama-cli
elif [ -f "~/llama.cpp/build/llama-cli" ]; then
    echo "✅ llama-cli exists at ~/llama.cpp/build/llama-cli"
    ls -la ~/llama.cpp/build/llama-cli
else
    echo "❌ llama-cli NOT FOUND"
    echo "   Looking for it..."
    find ~/llama.cpp -name "llama-cli" 2>/dev/null
fi

# Test 5: Check model
echo ""
echo "[5/7] Checking Sarvam model..."
if [ -f "~/llama.cpp/models/sarvam-1.bin" ]; then
    echo "✅ Model exists"
    ls -lh ~/llama.cpp/models/sarvam-1.bin
elif [ -f "~/llama.cpp/models/sarvam-1" ]; then
    echo "✅ Model exists (no .bin)"
    ls -lh ~/llama.cpp/models/sarvam-1
else
    echo "❌ Model NOT FOUND"
    echo "   Contents of models folder:"
    ls -la ~/llama.cpp/models/ 2>/dev/null
fi

# Test 6: Test llama.cpp directly
echo ""
echo "[6/7] Testing llama.cpp directly..."
cd ~/llama.cpp
if [ -f "llama-cli" ]; then
    echo "Testing basic run..."
    echo "Hello, who are you?" | timeout 30 ./llama-cli -m models/sarvam-1.bin -p "You are a helpful assistant. User: Hello, who are you?" -n 20 2>&1 | head -20
elif [ -f "build/llama-cli" ]; then
    echo "Testing from build..."
    echo "Hello" | timeout 30 ./build/llama-cli -m models/sarvam-1.bin -p "You are helpful. User: Hello" -n 20 2>&1 | head -20
else
    echo "❌ Cannot test - llama-cli not found"
fi

# Test 7: Run Aura in test mode
echo ""
echo "[7/7] Testing Aura Python imports..."
cd ~/aura-secure-assistant
python -c "
import sys(
sys.path.insert0, '.')
print('Testing imports...')
try:
    from src.agent.agent import AuraAgent
    print('✅ Agent imported')
except Exception as e:
    print(f'❌ Agent import error: {e}')

try:
    from src.agent.llm import LLMInterface
    print('✅ LLM imported')
except Exception as e:
    print(f'❌ LLM import error: {e}')

try:
    from src.interface.telegram_bot import AuraBot
    print('✅ TelegramBot imported')
except Exception as e:
    print(f'❌ TelegramBot import error: {e}')
"

echo ""
echo "=========================================="
echo "✅ DIAGNOSTIC COMPLETE"
echo "=========================================="
