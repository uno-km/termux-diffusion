# Termux-Diffusion

[![PyPI](https://img.shields.io/pypi/v/termux-diffusion.svg?style=flat-square&color=0369a1)](https://pypi.org/project/termux-diffusion/)
[![Python](https://img.shields.io/pypi/pyversions/termux-diffusion.svg?style=flat-square)](https://pypi.org/project/termux-diffusion/)
[![npm](https://img.shields.io/npm/v/termux-diffusion.svg?style=flat-square&color=b91c1c)](https://www.npmjs.com/package/termux-diffusion)
[![npm downloads](https://img.shields.io/npm/dm/termux-diffusion.svg?style=flat-square&color=b91c1c)](https://www.npmjs.com/package/termux-diffusion)
[![License](https://img.shields.io/badge/License-Apache_2.0-004499.svg?style=flat-square)](https://github.com/uno-km/termux-diffusion)

> **Pure CPU Native On-Device Stable Diffusion Runtime for Android Termux & Samsung Galaxy.**  
> *Zero PRoot. Zero Virtualization. 100% Native ARM64 Bionic libc & NEON SIMD Vector Acceleration.*

---

## 1. Architecture & Key Engineering Features

`termux-diffusion` is a standalone on-device image synthesis engine engineered specifically for Android smartphones running Termux. It operates directly against Android's native Bionic libc ABI with zero virtualization layers.

* **Pure CPU Native Bionic Execution**: Bypasses heavy PRoot Linux containers and virtualization overhead, binding directly to native ARM64 CPU instructions.
* **One-Touch Prebuilt Provisioning**: Provisions precompiled native binaries (`sd-cli-cpu`) and the OpenMP runtime (`libomp.so`) in seconds via a single command, completely eliminating 20-minute on-device C++ compilation cycles.
* **ARMv8.2-A DotProd & FP16 NEON SIMD**: Employs optimized vector matrix multiplication kernels tailored for modern mobile microarchitectures (Cortex-X, Cortex-A78, Oryon).
* **Built-in VAE Tiling**: Eliminates the ~1.2 GB memory spike during latent-to-pixel decoding, reducing peak RAM consumption by ~70% and preventing Android low-memory killer (LMK) aborts.
* **Automated Android MediaStore Indexing**: Synchronizes synthesized images directly to `Pictures/TermuxDiffusion` and broadcasts media scan intents for real-time visibility in the Samsung Gallery app.
* **Fail-Fast Thermal Protection**: On-device compilation on Termux is blocked by default without explicit opt-in (`TERMUX_DIFFUSION_ALLOW_SOURCE_BUILD=1`), guarding the device against excessive thermal throttling.

---

## 2. Installation & One-Touch Native Provisioning

### 2.1 System Prerequisites (Termux)
In the Termux terminal, install the core runtime dependencies:
```bash
pkg update && pkg install -y python nodejs clang termux-api
```

### 2.2 Package Installation

* **Python SDK (PyPI)**:
  ```bash
  pip install termux-diffusion
  termux-diffusion install
  ```

* **Node.js SDK & CLI (NPM)**:
  ```bash
  npm install -g termux-diffusion
  npx termux-diffusion install
  ```

> The `install` command provisions the standalone CPU native engine (`sd-cli-cpu`) and companion OpenMP runtime (`libomp.so`) directly into `~/.cache/termux-diffusion/bin`.

---

## 3. Quickstart & Usage

### 3.1 CLI Interface
```bash
# Generate image using pure CPU with default LCM anime preset (6 steps)
termux-diffusion generate "cute polar bear, high quality illustration" -m anime --cpu -o polar_bear.png

# Custom dimensions, steps, and threads
termux-diffusion generate "cute dolphin, vibrant ocean, 8k resolution" -W 512 -H 512 --steps 6 -t 4 -o dolphin.png
```

### 3.2 Python SDK
```python
import termux_diffusion as td

# Synthesize image via Pure CPU Native Engine
image_path = td.generate(
    prompt="cute polar bear in snow, high quality illustration",
    model="anime",
    steps=6,
    device="cpu",
    output_path="polar_bear.png"
)
print(f"Generated artifact: {image_path}")
```

### 3.3 Node.js / TypeScript SDK
```typescript
import { generate } from "termux-diffusion";

async function main() {
  const result = await generate({
    prompt: "cute dolphin leaping through waves, high quality illustration",
    model: "anime",
    steps: 6,
    device: "cpu",
    outputPath: "dolphin.png"
  });
  console.log("Image synthesized:", result.outputPath);
}

main();
```

---

## 4. Verified Hardware Benchmarks (Ground Truth)

All benchmarks measured on physical Android hardware using pure CPU execution (`sd-cli-cpu`, 4 threads, NEON SIMD) with the `anime` preset (DreamShaper 8 LCM Q4_0, 512x512, 6 steps):

| Device | SoC & CPU Architecture | Total Time (Wall Time) | Sampling Time | Peak RAM (VmRSS) | Output Resolution |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Samsung Galaxy S25** | Snapdragon 8 Elite (Oryon CPU) | **15m 52s (951s)** | **11m 37s (697s)** | **~2.5 GB** | 512 × 512 PNG |
| **Samsung Galaxy S21** | Exynos 2100 (Cortex-X1 + A78) | **53m 45s (3221s)** | **7m 47s (467s)** | **~2.4 GB** | 512 × 512 PNG |

*Both devices completed end-to-end inference and synchronized outputs to the Android MediaStore without memory leaks or crash events.*

---

## 5. Official Ecosystem Documentation
- [Official Architecture & API Reference](https://uno-km.vercel.app/lib/diffusion/)
- [Ecosystem Metrics & Registry Stats](https://uno-km.vercel.app/foundation/metrics)
- [AMEVA Open-Source Foundation Portal](https://uno-km.vercel.app/foundation/index.html)

---

## 6. License
Licensed under the Apache-2.0 License. Copyright (c) 2026 Eunho Kim ([@uno-km](https://github.com/uno-km)).

