#!/bin/bash
# AURA 2.0 - Complete AGI Engine Launcher
# This is the REAL assistant with autonomy

echo "=========================================="
echo "🤖 AURA 2.0 - AGI Engine"
echo "=========================================="
echo ""

# Check if in right directory
if [ ! -f "aura_engine.py" ]; then
    echo "❌ Error: Run from aura-secure-assistant directory"
    exit 1
fi

# Check dependencies
echo "Checking system..."
python -c "import requests, yaml, networkx" 2>/dev/null || {
    echo "Installing dependencies..."
    pip install -q requests pyyaml networkx
}

echo "✅ Dependencies OK"
echo ""

# Create data directories
mkdir -p data/logs
mkdir -p data/memory

echo "Starting AURA 2.0 AGI Engine..."
echo ""
echo "This system can:"
echo "  • Answer calls and talk to people"
echo "  • Open apps and perform actions"
echo "  • Reason autonomously"
echo "  • Handle notifications"
echo "  • Execute tasks"
echo ""
echo "Press Ctrl+C to stop"
echo "=========================================="
echo ""

# Run the engine
python aura_engine.py
