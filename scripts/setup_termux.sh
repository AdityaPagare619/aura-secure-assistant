#!/bin/bash
# Aura Setup Script for Termux

echo "Updating Termux..."
pkg update -y
pkg upgrade -y

echo "Installing Python and Git..."
pkg install -y python git curl

echo "Installing termux-api for hardware access..."
pkg install -y termux-api

echo "Installing Python libraries..."
pip install python-telegram-bot llama-cpp-python flask requests

echo "Downloading Sarvam Model (2B)..."
# This is a placeholder. In reality, user should download the GGUF file manually or via script
mkdir -p ~/aura/models
echo "Please place your Sarvam-1.gguf file in ~/aura/models/"

echo "Installing Voice Dependencies..."
# FFmpeg for audio conversion
pkg install -y ffmpeg

# Whisper.cpp or Faster-Whisper
# pip install faster-whisper # Optional, if using python wrapper

echo "Creating startup script..."
cat > ~/aura/start.sh << 'EOF'
#!/bin/bash
cd ~/aura
source ~/miniconda3/etc/profile 2>/dev/null || true
python -m src.interface.telegram_bot
EOF
chmod +x ~/aura/start.sh

echo "To run Aura in background (24/7), use:"
echo "  nohup bash ~/aura/start.sh &"
echo "Or use 'termux-services' to run as a daemon."

echo "Setup Complete!"
echo "Run 'bash ~/aura/start.sh' to start."
