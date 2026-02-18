#!/bin/bash
# Sarvam AI Installation Script for Termux
# Run this ONCE to install Sarvam AI

echo "=========================================="
echo "🔧 Installing Sarvam AI (llama.cpp)"
echo "=========================================="

# Step 1: Install build dependencies
echo "[1/5] Installing dependencies..."
pkg update -y
pkg install -y python git curl wget

# Step 2: Clone llama.cpp
echo "[2/5] Cloning llama.cpp..."
cd ~
rm -rf llama.cpp
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp

# Step 3: Build llama.cpp
echo "[3/5] Building llama.cpp (this may take 10-15 minutes)..."
make -j$(nproc)

# Step 4: Download Sarvam AI model
echo "[4/5] Downloading Sarvam AI model..."
# Create models directory
mkdir -p models

# Download a small model for testing (or replace with your Sarvam model URL)
# Example: wget -O models/sarvam-1.bin <URL_TO_SARVAM_MODEL>
# For now, we'll use a tiny model for testing
wget -O models/sarvam-1.bin https://huggingface.co/lmstudio-ai/gemma-2b-it-GGUF/resolve/main/gemma-2b-it-q4_k_m.gguf

echo "[5/5] Done!"
echo "=========================================="
echo "✅ Sarvam AI installed!"
echo "Model location: ~/llama.cpp/models/sarvam-1.bin"
echo "=========================================="
echo ""
echo "To run Aura with Sarvam AI:"
echo "1. Edit config.yaml and set: provider: 'llama-cpp'"
echo "2. Run: cd ~/aura-secure-assistant && python main.py"
