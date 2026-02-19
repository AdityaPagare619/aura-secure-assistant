#!/bin/bash
# AURA 2.0 Launcher
# Starts the AGI assistant with persistent AI brain

echo "=========================================="
echo "🤖 AURA 2.0 - AGI Assistant"
echo "=========================================="

# Check if in right directory
if [ ! -f "main_v2.py" ]; then
    echo "❌ Error: Run this from aura-secure-assistant directory"
    exit 1
fi

# Check Python
if ! command -v python &> /dev/null; then
    echo "❌ Python not found!"
    exit 1
fi

# Check if llama-server exists
if [ ! -f "$HOME/llama.cpp/build/bin/llama-server" ]; then
    echo "❌ llama-server not found!"
    echo "Building now..."
    cd ~/llama.cpp/build
    cmake --build . --config Release
    cd ~/aura-secure-assistant
fi

# Create data directories
mkdir -p data/logs
mkdir -p data/memory

echo ""
echo "Starting AURA 2.0..."
echo "This will:"
echo "  1. Start LLM server (keep model in memory)"
echo "  2. Initialize memory system"
echo "  3. Start event watcher"
echo "  4. Connect to Telegram"
echo ""
echo "Press Ctrl+C to stop"
echo "=========================================="
echo ""

# Run AURA 2.0
python main_v2.py
