# Termux-Diffusion

**Production On-Device AI Image Generation Framework for Android Termux & Samsung Galaxy**  
*Dual-Engine Architecture (Python & Node.js / TypeScript) with Native Bionic ARM64 Tensor Acceleration*

[![PyPI Version](https://img.shields.io/pypi/v/termux-diffusion.svg?color=blue)](https://pypi.org/project/termux-diffusion/)
[![npm Version](https://img.shields.io/npm/v/termux-diffusion.svg?color=red)](https://www.npmjs.com/package/termux-diffusion)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://pypi.org/project/termux-diffusion/)
[![Node Version](https://img.shields.io/badge/node-16+-brightgreen.svg)](https://www.npmjs.com/package/termux-diffusion)
[![Platform](https://img.shields.io/badge/platform-Android%20Termux%20(ARM64)-green.svg)](https://github.com/uno-km/termux-diffusion)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 1. System Overview

`termux-diffusion` is an enterprise-grade, on-device AI text-to-image synthesis pipeline designed specifically for Android Termux environments and Samsung Galaxy hardware.

Unlike desktop-centric WebUI ports that require heavy containerization (e.g., PRoot Linux / Ubuntu) or suffer from memory exhaustion under the Android Low Memory Killer (LMK), `termux-diffusion` executes directly against native Android Bionic `libc` with ARM64 NEON SIMD vectorization and GGML quantized tensor weights.

---

## 2. Automated Bootstrap & Installation

### Option A: One-Line Zero-Touch Bootstrap (Recommended)

Run the platform bootstrap script in Termux to automatically verify toolchains, storage permissions, and native engine binaries:

#### Python Runtime
```bash
curl -sL https://raw.githubusercontent.com/uno-km/termux-diffusion/main/docs/install.sh | bash
```

#### Node.js / TypeScript Runtime
```bash
curl -sL https://raw.githubusercontent.com/uno-km/termux-diffusion/main/docs/install-node.sh | bash
```

---

### Option B: Package Manager Installation

#### Python (PyPI)
```bash
pip install termux-diffusion && termux-diffusion-install
```

#### Node.js (npm)
```bash
npm install -g termux-diffusion && npx termux-diffusion install
```

---

## 3. Core Architectural Capabilities

* **Zero-PRoot Native Bionic Execution:** Executes natively on ARM64 without container overhead, achieving maximum memory efficiency.
* **Integrated Model Hub:** Built-in streaming downloader with automatic checksum verification and cache persistence.
* **Power & WakeLock Management (`TermuxWakeLock`):** Automatically holds Android CPU WakeLock during inference, preventing kernel suspension when the screen turns off.
* **Low-Memory & LMK Guard:** Inspects physical memory and Android zRAM (Samsung RAM Plus) before allocating tensor weight buffers.
* **Samsung Gallery Integration:** Automatically persists generated outputs to `~/storage/pictures/TermuxDiffusion/` and triggers `android.intent.action.MEDIA_SCANNER_SCAN_FILE` for instant indexing in Samsung Gallery.
* **big.LITTLE Core Affinity Tuning:** Auto-detects Exynos (e.g., 1380, 1480, 2400) and Snapdragon cluster topologies to maintain high sustained clock rates without thermal throttling.
* **Hardware Compute Selection:** Explicit compute backend targeting via `device="cpu"` or `device="gpu"`.

---

## 4. Built-in Model Hub Presets

| Preset | Model & Quantization | Size | Latency Baseline (Exynos 1380) | Recommended Workload |
| :--- | :--- | :---: | :---: | :--- |
| **`"realistic"`** | Realistic Vision V6.0 B1 (Q4_K) | 1.62 GB | ~25 min (10 steps) | High-fidelity photorealism (portraits, skin textures, lighting) |
| **`"speed"`** | Stable Diffusion 1.5 Base (Q4_1) | 1.59 GB | ~15 min (10 steps) | General-purpose drafting and composition |
| **`"sdxs"`** | SDXS 512-0.9 Mobile (Q4_0) | **450 MB** | **~2.5 min (2 steps)** | Ultra-low latency mobile prototyping |
| **`"turbo"`** | SD Turbo (Q4_0) | 1.20 GB | ~4 min (1 step) | Single-step real-time inference |
| **`"anime"`** | DreamShaper 8 (Q4_K) | 1.65 GB | ~20 min (10 steps) | 2D / 2.5D stylized illustration and animation art |

---

## 5. Usage & Integration

### Python API

```python
from termux_diffusion import generate

result = generate(
    prompt="RAW photo, portrait of a happy smiling young Korean man in his 30s wearing glasses and hoodie, working on laptop, photorealistic, cinematic",
    model="realistic",
    device="cpu",
    steps=10,
    cfg_scale=4.0,
    output="developer.png"
)

print(f"Output Path: {result.path}")
print(f"Android MediaStore: {result.gallery_path}")
print(f"Elapsed Time: {result.elapsed_sec:.2f}s")
```

### Node.js / TypeScript API

```javascript
const { generate } = require('termux-diffusion');

async function main() {
    const result = await generate({
        prompt: 'cyberpunk cat with neon collar in rainy alley, 8k, photorealistic',
        model: 'speed',
        device: 'cpu',
        steps: 10,
        output: 'cyber_cat.png'
    });

    console.log(`Output Path: ${result.path}`);
    console.log(`Android MediaStore: ${result.galleryPath}`);
}

main().catch(console.error);
```

---

## 6. Custom Models & Hugging Face Resolution

### 1. Direct Hugging Face Repository Identifier
Pass any repository ID and `.gguf` filename. The framework resolves, streams, caches, and executes the weights:
```python
generate(
    "1girl, anime masterpiece, vibrant colors",
    model="second-state/DreamShaper-8-GGUF/dreamshaper-8-Q4_k.gguf"
)
```

### 2. Local File Reference
```python
generate(
    "fantasy landscape at sunrise",
    model="~/storage/downloads/custom_model.gguf"
)
```

### 3. Alias Registration (`register_model`)
```python
from termux_diffusion import register_model, generate

register_model("waifu", repo_id="second-state/DreamShaper-8-GGUF", filename="dreamshaper-8-Q4_k.gguf")
generate("anime portrait", model="waifu")
```

---

## 7. Pre-flight Diagnostic Tool

Verify system packages, architecture, available memory, and native engine status:

```bash
# Python
termux-diffusion-doctor

# Node.js
npx termux-diffusion doctor
```

---

## 8. License

Released under the **MIT License**. Maintained by **uno-km**.
