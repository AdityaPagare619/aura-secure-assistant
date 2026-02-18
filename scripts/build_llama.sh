#!/bin/bash
# Build llama.cpp using CMake (new build system)

echo "=========================================="
echo "🔨 Building llama.cpp (CMake)"
echo "=========================================="

cd ~/llama.cpp

# Create build directory
mkdir -p build
cd build

# Configure with CMake
cmake .. -DCMAKE_BUILD_TYPE=Release

# Build
cmake --build . --config Release -j$(nproc)

# Check if built
if [ -f "bin/llama-cli" ]; then
    echo "✅ Built successfully!"
    echo "Location: ~/llama.cpp/build/bin/llama-cli"
    ls -la bin/llama-cli
else
    echo "Checking for alternative locations..."
    find ~/llama.cpp/build -name "llama-cli" 2>/dev/null
fi
