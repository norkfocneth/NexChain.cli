#!/usr/bin/env bash
# ========================================================
# NexChain AI CLI ? Universal 1-Line Installer
# Supported: Android Termux, Linux, macOS
# ========================================================

set -e

REPO_URL="https://github.com/norkfocneth/NexChain.cli.git"
INSTALL_DIR="$HOME/.nexchain"
BIN_DIR=""

echo ""
echo "========================================================"
echo "  NexChain AI CLI ? Universal 1-Line Installer"
echo "========================================================"

# Detect Termux vs standard Linux/macOS
if [ -n "$PREFIX" ] && [ -d "$PREFIX/bin" ]; then
    BIN_DIR="$PREFIX/bin"
    echo "[*] Detected Android Termux environment..."
    if ! command -v python3 &> /dev/null || ! command -v git &> /dev/null; then
        echo "[*] Installing Python & Git in Termux..."
        pkg update -y && pkg install -y python git
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

# Interactive AI Brain Model Prompt
echo ""
echo "========================================================"
echo "  ?? Optional AI Brain Model Setup"
echo "========================================================"
echo "NexChain CLI includes an optional local AI Brain Model"
echo "(Qwen2.5-0.5B, ~397MB) for conversational natural reasoning."
echo ""

INSTALL_AI="n"
if [ -t 0 ]; then
    read -r -p "Do you want to install the AI Brain Model for a better experience? [y/N]: " INSTALL_AI
elif [ -e /dev/tty ]; then
    read -r -p "Do you want to install the AI Brain Model for a better experience? [y/N]: " INSTALL_AI < /dev/tty
fi

if [[ "$INSTALL_AI" =~ ^[Yy]$ ]]; then
    echo "[*] Checking for Ollama..."
    if ! command -v ollama &> /dev/null; then
        echo "[*] Installing Ollama..."
        if [ -n "$PREFIX" ]; then
            echo "[!] In Termux: run 'pkg install ollama' or use Python fallback."
        else
            curl -fsSL https://ollama.com/install.sh | sh || true
        fi
    fi
    if command -v ollama &> /dev/null; then
        echo "[*] Downloading Qwen2.5-0.5B (~397MB)..."
        ollama pull qwen2.5:0.5b
        echo "[?] Local AI Brain Model installed & ready!"
    else
        echo "[!] Ollama not found. You can install it later with: nexchain setup-ai"
    fi
else
    echo "[-] Skipping AI Brain Model download."
    echo "    NexChain will operate in 100% offline deterministic rule-based mode."
    echo "    (You can install the AI model later anytime by typing: nexchain setup-ai)"
fi

echo ""
echo "========================================================"
echo "  ? NexChain AI CLI Installed Successfully!"
echo "  ?? Run 'nexchain' from ANY terminal to start!"
echo "========================================================"
echo ""
