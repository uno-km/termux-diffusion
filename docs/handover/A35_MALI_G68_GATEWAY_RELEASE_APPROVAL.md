# Galaxy A35 (Mali-G68) Gateway Release Approval & Publication Plan

## 1. Release Identification & Provenance
- **Repository**: `https://github.com/uno-km/termux-diffusion.git`
- **Source Validation Commit**: `4cb98487b32d207ee53dd716b1eef7343e86c04f` (`validation/galaxy-a35-vulkan`)
- **Integration dev Commit**: `39631b8a5b28d08595304b57c6c49842a222384a` (`dev`)
- **Production main Commit**: `df0625b306b3e8c1e95e7c37a6b7d1bb76d1e43e` (`main`)
- **Target Release Tag**: `v1.3.1` (Gateway Packaging)

---

## 2. Reused Canonical Release Assets
- **Public Package URL**: `https://github.com/uno-km/termux-diffusion/releases/download/v1.3.1-vulkan-mali-experimental/termux-diffusion-vulkan-prebuilt-v1.3.1-android-arm64-mali-compat-v2.tar.gz`
- **Canonical Package Size**: `56,678,669` bytes (Corrected metadata from legacy `58102374`)
- **Canonical Package SHA-256**: `65e4e305241b22385313e386afbcd12722061041280d00a44dfdc3ff23aa17b8`
- **Internal Binary Hashes**:
  - `bin/sd-cli-vulkan`: `1f10b3c91b34764cbeb79bc2a8360c8e2f1580cbd41d7160b028a0b512ced6db`
  - `bin/v10-self-test`: `c60280d65e75e8c089325979973386754f6eff0b831d3d1eae91bb488f45e110`

---

## 3. Galaxy A35 Ground Truth Verification Matrix
- **Device Model**: `SM-A356N` (Galaxy A35 5G / Exynos 1380 / Mali-G68 MP5)
- **V10 GGML MatMul**: `PASS` (32x32 FP32, Max Error `9.39369e-05`, RC=0)
- **V11 SDXS FAST (256p 1-step)**: `PASS` (15.72s, VRAM 651.92 MB, SHA256 `33d2c5cd...`)
- **CLI E2E Auto Mode**: `PASS` (18.65s, Auto-promoted to `vulkan`)
- **Explicit Vulkan (`--device vulkan`)**: `PASS` (18.41s)
- **Explicit CPU (`--device cpu`)**: `PASS` (22.50s)
- **Auto Fallback on GPU Failure**: `PASS` (Auto-recovered to CPU NEON, 22.09s, RC=0)
- **Explicit GPU Fail-Fast**: `PASS` (Raised `PlatformNotSupportedError`, RC=1, No Silent CPU Fallback)
- **A35 BALANCED Preset**: `PENDING_DEVICE_VALIDATION` (`auto_activation=false`)

---

## 4. Gateway Changes (PyPI & npm)
1. **Device Detection**: Added `SM-A356N` (`a35x`, `a35xks`) to `validated-vulkan-profiles.json`.
2. **Preset Gating**: `fast` enabled by default; `balanced` gated until dedicated on-device 512p validation.
3. **Download Router**: Streams existing 56.6MB Mali package on-demand; PyPI wheel (53KB) and npm package (85KB) remain ultra-lightweight.

---

## 5. Clean Installation Verification Plan
```bash
# 1. Clean Environment Pip Install
pip install --no-cache-dir -U termux-diffusion

# 2. Automated Engine Provisioning
termux-diffusion install --backend auto

# 3. FAST Preset Execution
termux-diffusion generate "a small red robot on workbench" --preset fast --device auto

# 4. Explicit Fail-Fast Verification
termux-diffusion generate "test prompt" --preset fast --device vulkan
```

---

## 6. Publication Gate Status
- `NATIVE_MALI_REBUILT`: `FALSE` (100% existing package reuse)
- `NEW_A35_TARBALL_CREATED`: `FALSE`
- `PYPI_PUBLISHED`: `FALSE` (Pending formal clean-install sign-off)
- `NPM_PUBLISHED`: `FALSE` (Pending formal clean-install sign-off)
