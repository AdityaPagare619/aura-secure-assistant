#!/bin/bash
# AURA 2.0 - Professional Setup Script
# One-command setup that verifies and installs everything automatically

set -e  # Exit on error

echo "=========================================="
echo "🤖 AURA 2.0 - Professional Setup"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track overall status
SETUP_SUCCESS=true

# Function to print status
print_status() {
    echo -e "${GREEN}✅${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
    SETUP_SUCCESS=false
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

# ==========================================
# STEP 1: Check Python
# ==========================================
echo "[1/8] Checking Python..."
if command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
    print_status "Python found: $PYTHON_VERSION"
else
    print_error "Python not found! Installing..."
    pkg update -y
    pkg install -y python
fi

# ==========================================
# STEP 2: Install/Update Dependencies
# ==========================================
echo ""
echo "[2/8] Installing dependencies..."

# Required packages
PACKAGES="requests aiohttp pyyaml python-dotenv networkx telegram"

for package in $PACKAGES; do
    echo "  Checking $package..."
    python -c "import $package" 2>/dev/null || {
        echo "    Installing $package..."
        pip install --quiet $package
    }
done

print_status "All dependencies installed"

# ==========================================
# STEP 3: Check llama.cpp Installation
# ==========================================
echo ""
echo "[3/8] Checking llama.cpp installation..."

LLAMA_DIR="$HOME/llama.cpp"
LLAMA_BUILD_DIR="$LLAMA_DIR/build"
LLAMA_SERVER="$LLAMA_BUILD_DIR/bin/llama-server"
LLAMA_CLI="$LLAMA_BUILD_DIR/bin/llama-cli"

if [ -d "$LLAMA_DIR" ]; then
    print_status "llama.cpp directory found"
    
    # Check for server binary
    if [ -f "$LLAMA_SERVER" ]; then
        print_status "llama-server binary found"
    else
        print_warning "llama-server not found, checking for cli..."
        
        if [ -f "$LLAMA_CLI" ]; then
            print_status "llama-cli found (server mode not built)"
            print_warning "Building server mode now..."
            
            cd "$LLAMA_BUILD_DIR"
            cmake --build . --config Release -j$(nproc)
            cd - > /dev/null
            
            if [ -f "$LLAMA_SERVER" ]; then
                print_status "llama-server built successfully"
            else
                print_error "Failed to build llama-server"
                exit 1
            fi
        else
            print_error "llama.cpp not properly built!"
            echo "Building from source..."
            
            cd "$LLAMA_DIR"
            mkdir -p build
            cd build
            cmake .. -DCMAKE_BUILD_TYPE=Release
            cmake --build . --config Release -j$(nproc)
            cd - > /dev/null
            
            if [ -f "$LLAMA_SERVER" ]; then
                print_status "llama.cpp built successfully"
            else
                print_error "Build failed!"
                exit 1
            fi
        fi
    fi
else
    print_error "llama.cpp not found! Installing..."
    
    cd "$HOME"
    git clone https://github.com/ggerganov/llama.cpp.git
    cd llama.cpp
    mkdir -p build
    cd build
    cmake .. -DCMAKE_BUILD_TYPE=Release
    cmake --build . --config Release -j$(nproc)
    cd - > /dev/null
    
    print_status "llama.cpp installed and built"
fi

# ==========================================
# STEP 4: Check AI Model
# ==========================================
echo ""
echo "[4/8] Checking AI model..."

MODEL_DIR="$LLAMA_DIR/models"
MODEL_FILE="$MODEL_DIR/sarvam-1.bin"

if [ -f "$MODEL_FILE" ]; then
    MODEL_SIZE=$(ls -lh "$MODEL_FILE" | awk '{print $5}')
    print_status "Model found: sarvam-1.bin ($MODEL_SIZE)"
else
    print_warning "Model not found at $MODEL_FILE"
    echo "Checking for other models..."
    
    # List available models
    if [ -d "$MODEL_DIR" ]; then
        echo "Available models:"
        ls -lh "$MODEL_DIR"/*.bin 2>/dev/null || echo "  (No .bin files found)"
        ls -lh "$MODEL_DIR"/*.gguf 2>/dev/null || echo "  (No .gguf files found)"
    fi
    
    echo ""
    echo "⚠️  Please download your AI model and place it at:"
    echo "   $MODEL_FILE"
    echo ""
    echo "Or update config.yaml with the correct model path"
fi

# ==========================================
# STEP 5: Create Data Directories
# ==========================================
echo ""
echo "[5/8] Creating data directories..."

mkdir -p data/logs
mkdir -p data/memory
mkdir -p data/cache

print_status "Data directories created"

# ==========================================
# STEP 6: Check Configuration
# ==========================================
echo ""
echo "[6/8] Checking configuration..."

if [ -f "config.yaml" ]; then
    print_status "config.yaml found"
    
    # Check if bot token is set
    if grep -q "YOUR_BOT_TOKEN" config.yaml; then
        print_warning "Bot token not set in config.yaml"
        echo "Please edit config.yaml and add your Telegram bot token"
    else
        print_status "Bot token configured"
    fi
else
    print_warning "config.yaml not found, creating..."
    cat > config.yaml << 'EOF'
telegram:
  bot_token: "7573691331:AAFTsne004fhKUgQQT6ydRVh6mazfkl7Ks0"
  admin_user_ids: []

llm:
  provider: "llama-cpp"
  model_path: "~/llama.cpp/models/sarvam-1.bin"
  server_host: "127.0.0.1"
  server_port: 8080
  max_tokens: 512
  temperature: 0.7

memory:
  ephemeral_ttl: 300
  working_db_path: "data/memory/working.db"
  graph_db_path: "data/memory/graph.db"

security:
  verify_actions: true
  log_all_actions: true
  auto_learn_privacy: true

debug: false
EOF
    print_status "config.yaml created"
fi

# ==========================================
# STEP 7: Verify Python Imports
# ==========================================
echo ""
echo "[7/8] Verifying Python imports..."

python << 'PYTHON_CHECK'
import sys
sys.path.insert(0, '.')

checks = [
    ('requests', 'HTTP library'),
    ('yaml', 'YAML parser'),
    ('networkx', 'Graph library'),
    ('aiohttp', 'Async HTTP'),
]

all_good = True
for module, desc in checks:
    try:
        __import__(module)
        print(f"  ✅ {module} ({desc})")
    except ImportError as e:
        print(f"  ❌ {module}: {e}")
        all_good = False

sys.exit(0 if all_good else 1)
PYTHON_CHECK

if [ $? -eq 0 ]; then
    print_status "All Python imports working"
else
    print_error "Some Python imports failed"
fi

# ==========================================
# STEP 8: Final Verification
# ==========================================
echo ""
echo "[8/8] Final verification..."
echo ""
echo "System Check Summary:"
echo "---------------------"
echo "Python: $(python --version 2>&1)"
echo "llama.cpp: $(ls $LLAMA_BUILD_DIR/bin/llama-* 2>/dev/null | wc -l) binaries found"
echo "Model: $(ls $MODEL_FILE 2>/dev/null && echo 'Found' || echo 'Not found')"
echo "Data dirs: $(ls data/ 2>/dev/null | tr '\n' ' ')"
echo ""

if [ "$SETUP_SUCCESS" = true ]; then
    echo -e "${GREEN}==========================================${NC}"
    echo -e "${GREEN}✅ Setup Complete!${NC}"
    echo -e "${GREEN}==========================================${NC}"
    echo ""
    echo "To start AURA 2.0, run:"
    echo "  bash scripts/run_aura_v2.sh"
    echo ""
    echo "Or directly:"
    echo "  python main_v2.py"
    echo ""
else
    echo -e "${RED}==========================================${NC}"
    echo -e "${RED}⚠️  Setup completed with warnings${NC}"
    echo -e "${RED}==========================================${NC}"
    echo ""
    echo "Please check the errors above and fix them"
    echo "Then run this setup script again"
    echo ""
fi
