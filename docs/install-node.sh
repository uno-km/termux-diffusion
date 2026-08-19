#!/data/data/com.termux/files/usr/bin/bash
# 1-Click Automated Zero-Touch Installer for termux-diffusion (Node.js Edition)
set -e

echo "==================================================================="
echo "🎨 termux-diffusion: 1-Click Automated Setup for Node.js on Termux"
echo "==================================================================="

# 1. Request Android storage access
echo "📱 [1/4] Checking Android storage permissions..."
termux-setup-storage 2>/dev/null || true

# 2. Install all required system toolchains in one batch
echo "📦 [2/4] Installing Node.js LTS, clang, cmake, git, termux-api via pkg..."
pkg update -y
pkg install -y nodejs-lts clang cmake git termux-api wget

# 3. Install termux-diffusion via npm
echo "☕ [3/4] Installing termux-diffusion npm package globally..."
npm install -g termux-diffusion

# 4. Provision native C++ ARM64 engine
echo "⚙️ [4/4] Provisioning and compiling native Bionic ARM64 engine..."
npx termux-diffusion install

echo "==================================================================="
echo "✨ [termux-diffusion] Setup Completed Successfully!"
echo "🚀 Try running:"
echo '   npx termux-diffusion generate "happy cat" -m speed'
echo "==================================================================="
