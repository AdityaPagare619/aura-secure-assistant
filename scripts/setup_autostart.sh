#!/bin/bash
# Aura Auto-Start Script for Termux
# This makes Aura start automatically when phone boots

# Create the boot script
mkdir -p ~/.termux

cat > ~/.termux/boot.sh << 'EOF'
# Change to Aura directory
cd ~/aura-secure-assistant

# Start Aura Bot in background
nohup python main.py > ~/aura.log 2>&1 &

# Optional: Start Ollama if you have Sarvam AI installed
# nohup ~/ollama serve > /dev/null 2>&1 &

echo "🤖 Aura started!"
EOF

# Make it executable
chmod +x ~/.termux/boot.sh

echo "=========================================="
echo "✅ Auto-start configured!"
echo "=========================================="
echo ""
echo "Aura will now start automatically when:"
echo "1. You open Termux app, OR"
echo "2. Your phone reboots"
echo ""
echo "To start manually now:"
echo "cd ~/aura-secure-assistant && python main.py"
