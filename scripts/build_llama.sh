#!/bin/bash
# Build llama.cpp binary

echo "=========================================="
echo "🔨 Building llama.cpp"
echo "=========================================="

cd ~/llama.cpp

# Check if already built
if [ -f "llama-cli" ]; then
    echo "✅ llama-cli already exists!"
    ls -la llama-cli
    exit 0
fi

# Build
echo "Building... (this takes 5-10 minutes)"
make -j$(nproc)

# Check result
if [ -f "llama-cli" ]; then
    echo "✅ Build successful!"
    ls -la llama-cli
else
    echo "❌ Build failed. Trying alternative..."
    # Try basic build
    make
fi
