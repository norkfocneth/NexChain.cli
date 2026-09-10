#!/usr/bin/env bash
# ========================================================
# NexChain AI CLI — Universal 1-Line Installer
# Supported: Android Termux, Linux, macOS
# ========================================================

set -e

REPO_URL="https://github.com/norkfocneth/NexChain.cli.git"
INSTALL_DIR="$HOME/.nexchain"
BIN_DIR=""
GGUF_URL="https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/qwen2.5-0.5b-instruct-q4_k_m.gguf"

echo ""
echo "========================================================"
echo "  NexChain AI CLI — Universal 1-Line Installer"
echo "========================================================"

# Detect Termux vs standard Linux/macOS
if [ -n "$PREFIX" ] && [ -d "$PREFIX/bin" ]; then
    BIN_DIR="$PREFIX/bin"
    echo "[*] Detected Android Termux environment..."
    if ! command -v python3 &> /dev/null || ! command -v git &> /dev/null || ! command -v curl &> /dev/null; then
        echo "[*] Installing Python, Git & Curl in Termux..."
        pkg update -y && pkg install -y python git curl
    fi
elif [ -d "$HOME/.local/bin" ] && [[ ":$PATH:" == *":$HOME/.local/bin:"* ]]; then
    BIN_DIR="$HOME/.local/bin"
elif [ -w "/usr/local/bin" ]; then
    BIN_DIR="/usr/local/bin"
else
    mkdir -p "$HOME/.local/bin"
    BIN_DIR="$HOME/.local/bin"
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc" 2>/dev/null || true
    fi
fi

# Clone or update
if [ -d "$INSTALL_DIR/.git" ]; then
    echo "[*] Updating existing NexChain repository..."
    cd "$INSTALL_DIR" && git pull --quiet
else
    echo "[*] Cloning NexChain CLI to $INSTALL_DIR..."
    rm -rf "$INSTALL_DIR"
    git clone --depth 1 "$REPO_URL" "$INSTALL_DIR"
fi

cd "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR/models"

# Virtual environment & dependencies
echo "[*] Setting up Python dependencies (rich, typer, httpx)..."
if python3 -m venv .venv 2>/dev/null; then
    .venv/bin/pip install --quiet rich typer httpx
else
    pip install --quiet rich typer httpx 2>/dev/null || pip install --user --quiet rich typer httpx
fi

# Create executable global wrapper
WRAPPER="$BIN_DIR/nexchain"
cat << 'EOF' > "$WRAPPER"
#!/usr/bin/env bash
INSTALL_DIR="$HOME/.nexchain"
if [ -f "$INSTALL_DIR/.venv/bin/python" ]; then
    exec "$INSTALL_DIR/.venv/bin/python" "$INSTALL_DIR/nexchain.py" "$@"
else
    exec python3 "$INSTALL_DIR/nexchain.py" "$@"
fi
EOF
chmod +x "$WRAPPER"

# Also symlink 'nexsen' alias
ln -sf "$WRAPPER" "$BIN_DIR/nexsen" 2>/dev/null || true

# Parse flags or env for automated AI install
INSTALL_AI=""
for arg in "$@"; do
    case "$arg" in
        --with-ai|-y|--ai) INSTALL_AI="y" ;;
    esac
done

if [ -n "$AI" ] || [ -n "$WITH_AI" ]; then
    INSTALL_AI="y"
fi

if [ -z "$INSTALL_AI" ]; then
    echo ""
    echo "========================================================"
    echo "  🧠 Optional AI Brain Model Setup"
    echo "========================================================"
    echo "NexChain CLI includes an optional local AI Brain Model"
    echo "(Qwen2.5-0.5B GGUF, ~468MB) for natural conversational reasoning."
    echo "NO Ollama needed! Directly runs offline on your device."
    echo ""

    if [ -t 0 ]; then
        read -r -p "Do you want to install the AI Brain Model for a better experience? [y/N]: " INSTALL_AI
    elif [ -e /dev/tty ]; then
        read -r -p "Do you want to install the AI Brain Model for a better experience? [y/N]: " INSTALL_AI < /dev/tty
    else
        INSTALL_AI="n"
    fi
fi

if [[ "$INSTALL_AI" =~ ^[Yy]$ ]]; then
    MODEL_FILE="$INSTALL_DIR/models/qwen2.5-0.5b.gguf"
    TMP_FILE="$INSTALL_DIR/models/qwen2.5-0.5b.gguf.tmp"
    echo ""
    echo "[*] Downloading AI Brain Model directly from HuggingFace..."
    echo "[*] Target: $MODEL_FILE"
    
    if curl -L --progress-bar "$GGUF_URL" -o "$TMP_FILE"; then
        mv "$TMP_FILE" "$MODEL_FILE"
        echo "[✓] AI Brain Model downloaded successfully!"
        
        # Optional engine helper
        if [ -n "$PREFIX" ]; then
            echo "[*] Installing llama.cpp in Termux for native mobile acceleration..."
            pkg install -y llama.cpp 2>/dev/null || true
        else
            if [ -f "$INSTALL_DIR/.venv/bin/pip" ]; then
                "$INSTALL_DIR/.venv/bin/pip" install --quiet llama-cpp-python 2>/dev/null || true
            fi
        fi
        echo "[✓] AI Brain Model is configured and ready!"
    else
        rm -f "$TMP_FILE"
        echo "[!] Download failed. You can re-try later anytime using: nexchain setup-ai"
    fi
else
    echo "[-] Skipping AI Brain Model download."
    echo "    NexChain will operate in 100% offline deterministic rule-based mode."
    echo "    (You can install the AI model later anytime by typing: nexchain setup-ai)"
fi

echo ""
echo "========================================================"
echo "  ✓ NexChain AI CLI Installed Successfully!"
echo "  👉 Run 'nexchain' from ANY terminal to start!"
echo "========================================================"
echo ""
