# ==============================================================================
# Dockerfile: termux-diffusion Linux / Container Test & Production Environment
# ==============================================================================

FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# 1. Install toolchain: Clang, CMake, Git, Make, Python 3, Node.js, Vulkan SDK headers
RUN apt-get update && apt-get install -y \
    clang \
    cmake \
    git \
    make \
    python3 \
    python3-pip \
    python3-venv \
    nodejs \
    npm \
    libvulkan-dev \
    vulkan-tools \
    curl \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# 2. Copy repository into container
COPY . /workspace

# 3. Setup Python testing tools and install termux-diffusion in editable mode
RUN pip3 install --no-cache-dir pytest pytest-asyncio build
RUN pip3 install -e .

# 4. Link CLI for global access
RUN npm link

# 5. Default entrypoint: Run Doctor, Python PyTest, Node.js Test, and Model Catalog
CMD ["bash", "-c", "echo '===================================================' && echo '[Docker] Running termux-diffusion Doctor Diagnostic...' && echo '===================================================' && termux-diffusion doctor && echo '' && echo '===================================================' && echo '[Docker] Running Python PyTest Test Suite...' && echo '===================================================' && pytest tests/ -v && echo '' && echo '===================================================' && echo '[Docker] Running Node.js Engine Unit Tests...' && echo '===================================================' && npm test && echo '' && echo '===================================================' && echo '[Docker] Testing CLI Model Catalog Inspection...' && echo '===================================================' && npx termux-diffusion models && echo '' && echo '[SUCCESS] All Docker/Linux Tests Passed 100% Cleanly! Ready for inference.'"]
