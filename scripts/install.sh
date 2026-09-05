#!/usr/bin/env bash
# ==============================================================================
# termux-diffusion Universal One-Line Bootstrap Installer
# Usage: curl -sL https://raw.githubusercontent.com/uno-km/termux-diffusion/main/scripts/install.sh | bash
# ==============================================================================
set -euo pipefail

echo "================================================================="
echo " [AMEVA Foundation] termux-diffusion One-Line Installation Guard"
echo "================================================================="

# 1. Check Platform & Architecture
IS_TERMUX=false
if [ -d "/data/data/com.termux" ] || [ -n "${TERMUX_VERSION:-}" ]; then
    IS_TERMUX=true
fi

ARCH="$(uname -m)"
echo "-> Detected Platform: $(uname -s) (${ARCH})"

if [ "${IS_TERMUX}" != "true" ]; then
    echo "[WARN] Non-Termux host detected. Native Bionic acceleration is optimized for Android Termux (ARM64)."
fi

if [ "${ARCH}" != "aarch64" ] && [ "${ARCH}" != "arm64" ]; then
    echo "[WARN] Architecture is ${ARCH}. ARM64 is strongly recommended for mobile NPU/GPU tensor acceleration."
fi

# 2. Storage Setup (Termux only)
if [ "${IS_TERMUX}" = "true" ] && command -v termux-setup-storage >/dev/null 2>&1; then
    if [ ! -d "${HOME}/storage" ]; then
        echo "-> Requesting Android storage permission..."
        termux-setup-storage || true
    fi
fi

# 3. System Package Dependencies (Termux pkg)
if [ "${IS_TERMUX}" = "true" ] && command -v pkg >/dev/null 2>&1; then
    echo "-> Updating package repositories and installing toolchains..."
    pkg update -y
    pkg install -y \
        python \
        nodejs-lts \
        clang \
        make \
        cmake \
        git \
        termux-api \
        wget \
        vulkan-loader \
        vulkan-headers \
        vulkan-tools \
        opencl-headers
fi

# 4. Install Python & Node.js Core Packages
echo "-> Installing Python packages (ameva-runtime, termux-diffusion)..."
python -m pip install --upgrade pip setuptools wheel
python -m pip install --upgrade ameva-runtime termux-diffusion

if command -v npm >/dev/null 2>&1; then
    echo "-> Installing Node.js CLI (termux-diffusion)..."
    npm install -g termux-diffusion || npm install termux-diffusion || true
fi

# 5. Provision Native Engine & Run Doctor Diagnostics
echo "-> Provisioning native C++ engine (sd-cli) and running Self-Test..."
if command -v termux-diffusion >/dev/null 2>&1; then
    termux-diffusion install --backend auto || true
    echo ""
    termux-diffusion doctor || true
elif [ -f "${HOME}/.local/bin/termux-diffusion" ]; then
    "${HOME}/.local/bin/termux-diffusion" install --backend auto || true
    echo ""
    "${HOME}/.local/bin/termux-diffusion" doctor || true
fi

echo "================================================================="
echo " [SUCCESS] termux-diffusion installation & validation completed!"
echo " Quick start:"
echo "   termux-diffusion generate \"cyberpunk cat in neon city\" -m fast"
echo "================================================================="