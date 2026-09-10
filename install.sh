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
    # Suggest adding to PATH if missing
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

echo ""
echo "========================================================"
echo "  ? NexChain AI CLI Installed Successfully!"
echo "  ?? Run 'nexchain' from ANY terminal to start!"
echo "========================================================"
echo ""

