#!/bin/bash
# ONE COMMAND TO FIX & RUN AURA

# 1. Fix main.py (download correct version)
cd ~/aura-secure-assistant/aura-backend

# Check if main.py has issues
if grep -q "asyncio.run" main.py; then
    echo "⚠️ Fixing main.py..."
    # Download fixed main.py
    curl -s -o main.py "https://raw.githubusercontent.com/AdityaPagare619/aura-secure-assistant/main/aura-backend/main.py"
fi

# 2. Start Ollama (Sarvam Brain)
echo "🧠 Starting Ollama..."
nohup ollama serve > /dev/null 2>&1 &
sleep 3

# 3. Start Aura Bot
echo "🤖 Starting Aura Bot..."
nohup python main.py > aura.log 2>&1 &

# 4. Wait for startup
sleep 5

# 5. Verify
echo ""
echo "✅ Aura should be running!"
echo "📱 Open Telegram and message your bot."
echo ""
echo "📝 Logs:"
tail -20 aura.log
