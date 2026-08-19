#!/data/data/com.termux/files/usr/bin/bash
# 1-Click Automated Zero-Touch Installer for termux-diffusion (Python Edition)
set -e

echo "==================================================================="
echo "🎨 termux-diffusion: 1-Click Automated Setup for Samsung Galaxy & Termux"
echo "==================================================================="

# 1. Request Android storage access
echo "📱 [1/4] Checking Android storage permissions..."
termux-setup-storage 2>/dev/null || true

# 2. Install all required system toolchains in one batch
echo "📦 [2/4] Installing Python, clang, cmake, git, termux-api via pkg..."
pkg update -y
pkg install -y python clang cmake git termux-api wget

# 3. Install termux-diffusion via pip
echo "🐍 [3/4] Installing termux-diffusion Python package..."
pip install --upgrade termux-diffusion

# 4. Provision native C++ ARM64 engine
echo "⚙️ [4/4] Provisioning and compiling native Bionic ARM64 engine..."
termux-diffusion-install

echo "==================================================================="
echo "✨ [termux-diffusion] Setup Completed Successfully!"
echo "🚀 Try running:"
echo '   termux-diffusion generate "happy cat" -m speed'
echo "==================================================================="
