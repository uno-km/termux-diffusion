# 🎨 termux-diffusion

> **Production On-Device AI Image Generation Framework for Android Termux & Samsung Galaxy**  
> *Dual-Engine (Python & Node.js / TypeScript) Native Bionic ARM64 Diffusion Pipeline*

[![PyPI Version](https://img.shields.io/pypi/v/termux-diffusion.svg?color=blue)](https://pypi.org/project/termux-diffusion/)
[![npm Version](https://img.shields.io/npm/v/termux-diffusion.svg?color=red)](https://www.npmjs.com/package/termux-diffusion)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://pypi.org/project/termux-diffusion/)
[![Node Version](https://img.shields.io/badge/node-16+-brightgreen.svg)](https://www.npmjs.com/package/termux-diffusion)
[![Platform](https://img.shields.io/badge/platform-Android%20Termux%20(ARM64)-green.svg)](https://github.com/uno-km/termux-diffusion)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 💡 Overview

**`termux-diffusion`** is the world's first unified Python & Node.js on-device AI image generation framework tailored specifically for **Samsung Galaxy and Android Termux** devices.

Unlike desktop-centric WebUI ports that force users to install heavy PRoot Linux distributions (like Ubuntu) or suffer from memory leaks and Out-of-Memory (OOM) crashes, `termux-diffusion` runs directly on native **Android Bionic libc (ARM64)** using optimized C++ GGML quantization.

---

## ⚡ 1-Line Quick Installation

Select your preferred language runtime and run the 1-line command inside Termux:

### 🐍 Python (pip)
```bash
pip install termux-diffusion && termux-diffusion-install
```

### ☕ Node.js / TypeScript (npm)
```bash
npm install termux-diffusion && npx termux-diffusion install
```

---

## 🌟 Key Capabilities & Samsung Galaxy Protections

* **Zero-Root & Zero-PRoot Native Bionic Execution:**  
  Direct ARM64 NEON C++ inference without virtual Linux containers or root access.
* **Smart Model Hub (5 Built-in Presets):**  
  Automatic resumable downloading & caching for photorealistic, speed, and mobile-optimized GGUF models.
* **Samsung Galaxy Battery & Sleep Defense (`TermuxWakeLock`):**  
  Automatically holds Android CPU WakeLock during 10~25 minute inference so the OS never suspends generation when the screen turns off.
* **Low-RAM & OOM Guard (Samsung RAM Plus Integration):**  
  Pre-flight safety inspection of physical RAM and zRAM swap before model loading.
* **Samsung Gallery Auto-Synchronization:**  
  Renders directly to `~/storage/pictures/TermuxDiffusion/` and triggers Android `MEDIA_SCANNER` broadcast so new artwork immediately shows up in your Samsung Gallery app.
* **big.LITTLE CPU Core Cluster Auto-Tuning:**  
  Detects Exynos (e.g. 1380, 1480, 2400) and Snapdragon performance clusters, preventing thermal throttling.

---

## 📦 Built-in Model Hub Presets

| Preset | Model & Quantization | Size | Generation Time (A35 CPU) | Best For |
| :--- | :--- | :---: | :---: | :--- |
| **`"realistic"`** | Realistic Vision V6.0 B1 (Q4_K) | ~1.62 GB | ~25 min (10 steps) | Extreme photorealism (skin pores, lighting reflections, hair) |
| **`"speed"`** | Stable Diffusion 1.5 Base (Q4_1) | ~1.59 GB | ~15 min (10 steps) | General-purpose fast drafting and composition |
| **`"sdxs"`** | SDXS 512-0.9 Mobile (Q4_0) | **~450 MB** | **~2~3 min (2 steps)** | Ultra-lightweight mobile prototyping |
| **`"turbo"`** | SD Turbo (Q4_0) | ~1.20 GB | ~3~5 min (1 step) | 1-step real-time inference |
| **`"anime"`** | DreamShaper 8 (Q4_K) | ~1.65 GB | ~20 min (10 steps) | 2D / 2.5D stylized illustration and anime |

---

## 🚀 Quickstart Recipes

### 🐍 Python Recipe

```python
import asyncio
from termux_diffusion import generate, download_model, set_cache_dir

# 1. Generate Photorealistic Image in 1 Line
result = generate(
    prompt="RAW photo, portrait of a happy smiling young Korean man in his 30s wearing glasses and hoodie, working on laptop, photorealistic, cinematic",
    model="realistic",  # or 'speed', 'sdxs', 'turbo', 'anime'
    steps=10,
    cfg_scale=4.0,
    output="developer.png"
)

print(f"✅ Image saved: {result.path}")
print(f"📱 Samsung Gallery: {result.gallery_path}")
print(f"⏱️ Denoising took: {result.elapsed_sec:.1f}s")
```

### ☕ Node.js / JavaScript Recipe

```javascript
const { generate, downloadModel } = require('termux-diffusion');

async function main() {
    const result = await generate({
        prompt: 'cyberpunk cat with neon collar in rainy alley, 8k, photorealistic',
        model: 'speed',
        steps: 10,
        output: 'cyber_cat.png'
    });

    console.log('✅ Generated image:', result.path);
    console.log('📱 Samsung Gallery:', result.galleryPath);
}

main().catch(console.error);
```

---

## 🛠️ Advanced Model & Cache Management

```python
from termux_diffusion import (
    set_cache_dir,       # Set custom model storage (e.g. SD card)
    download_model,      # Pre-download models in background
    register_model,      # Register custom Hugging Face GGUF models
    list_cached_models,  # List downloaded models
    clear_cache          # Clean up storage
)

# Set custom storage directory (e.g. external SD card)
set_cache_dir("~/storage/external-1/ai_models")

# Pre-download preset
download_model("sdxs")

# Register custom Hugging Face model
register_model(
    name="my-waifu",
    repo_id="second-state/Realistic_Vision_V6.0_B1-GGUF",
    filename="realisticVisionV60B1_v51HyperVAE-Q4_k.gguf"
)

# View cached models
for m in list_cached_models():
    print(f"{m['name']} ({m['size_mb']} MB)")
```

---

## 🩺 Diagnostic Doctor

Run pre-flight diagnostics anytime to verify hardware, memory, build tools, and engine status:

```bash
# Python
termux-diffusion-doctor

# Node.js
npx termux-diffusion doctor
```

---

## 📄 License

Released under the **MIT License**. Maintained with ❤️ by **uno-km (쌩초보코딩단)**.
