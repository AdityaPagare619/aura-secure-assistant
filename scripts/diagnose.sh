#!/bin/bash
# Aura Diagnostic Script for Termux

echo "========================================="
echo "🔍 Aura Diagnostics"
echo "========================================="

# 1. Check Python
echo "[1/7] Checking Python..."
python --version
if [ $? -eq 0 ]; then
    echo "✅ Python is installed"
else
    echo "❌ Python is NOT installed"
    exit 1
fi

# 2. Check Dependencies
echo ""
echo "[2/7] Checking Python packages..."
pip list | grep -E "python-telegram-bot|aiohttp|pyyaml|dotenv"
if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed"
else
    echo "❌ Missing dependencies. Run: pip install python-telegram-bot aiohttp pyyaml python-dotenv"
fi

# 3. Check Git Clone
echo ""
echo "[3/7] Checking Aura code..."
if [ -d "$HOME/aura-secure-assistant/aura-backend" ]; then
    echo "✅ Aura code exists"
    cd $HOME/aura-secure-assistant/aura-backend
else
    echo "❌ Aura code NOT found"
    exit 1
fi

# 4. Check Config
echo ""
echo "[4/7] Checking Config..."
if [ -f "config.yaml" ]; then
    echo "✅ config.yaml exists"
    cat config.yaml
else
    echo "❌ config.yaml NOT found"
    exit 1
fi

# 5. Check Ollama/Sarvam
echo ""
echo "[5/7] Checking Ollama (Sarvam Brain)..."
curl -s http://localhost:11434 | head -5
if [ $? -eq 0 ]; then
    echo "✅ Ollama is RUNNING"
else
    echo "❌ Ollama is NOT running"
    echo "   Start with: nohup ollama serve > /dev/null 2>&1 &"
fi

# 6. Check Bot Process
echo ""
echo "[6/7] Checking Aura Bot Process..."
ps aux | grep "python main.py" | grep -v grep
if [ $? -eq 0 ]; then
    echo "✅ Aura Bot is RUNNING"
else
    echo "❌ Aura Bot is NOT running"
    echo "   Start with: cd ~/aura-secure-assistant/aura-backend && python main.py"
fi

# 7. Check Logs
echo ""
echo "[7/7] Checking Logs..."
if [ -f "aura.log" ]; then
    echo "📝 Last 10 lines of aura.log:"
    tail -10 aura.log
else
    echo "⚠️ No aura.log found"
fi

echo ""
echo "========================================="
echo "✅ Diagnostics Complete"
echo "========================================="
