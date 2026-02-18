# Aura Auto-Start Script for Termux
# Place in ~/.termux/boot.sh or use termux-autostart

# Change to Aura directory
cd ~/aura-secure-assistant/aura-backend

# Start Ollama in background (Sarvam Brain)
nohup ollama serve > /dev/null 2>&1 &
echo "🧠 Ollama (Sarvam Brain) started..."

# Wait for Ollama to be ready
sleep 5

# Start Aura Bot
nohup python main.py > aura.log 2>&1 &
echo "🤖 Aura Assistant started!"
echo "📱 Check Telegram to chat with Aura"
