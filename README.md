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

## 1. Quick Scenario Playbook (사용자 상황별 초간단 가이드)

### 🐣 Scenario 1: Clean Install (아무것도 설치되지 않은 사용자 / Termux 처음)

Open the Termux application and execute the 2 commands for your preferred runtime:

#### 🐍 Python:
```bash
# 1. Grant Android Storage Permission (Tap 'Allow' on the Android OS prompt)
termux-setup-storage

# 2. Install Toolchains & Provision Native Engine
pkg update -y && pkg install python clang cmake git termux-api wget -y
pip install termux-diffusion && termux-diffusion-install
```

#### ☕ Node.js / TypeScript:
```bash
# 1. Grant Android Storage Permission
termux-setup-storage

# 2. Install Toolchains & Provision Native Engine
pkg update -y && pkg install nodejs-lts clang cmake git termux-api wget -y
npm install -g termux-diffusion && npx termux-diffusion install
```

---

### ⚡ Scenario 2: Instant Generation (이미 설치된 사용자)

#### Option A: One-Line CLI Generation (No Coding Required)
* **Python CLI:**
  ```bash
  termux-diffusion generate "RAW photo, portrait of happy Korean developer wearing hoodie, photorealistic" -m realistic
  ```
* **Node.js CLI:**
  ```bash
  npx termux-diffusion generate "RAW photo, portrait of happy Korean developer wearing hoodie, photorealistic" -m realistic
  ```
  *(Output images are automatically synchronized to **Samsung Gallery / Google Photos** upon completion).*

#### Option B: Programmatic SDK Integration
* **Python (`generate_demo.py`):**
  ```python
  from termux_diffusion import generate

  result = generate("cyberpunk cat with neon collar in rainy alley", model="speed")
  print(f"Output saved to: {result.path}")
  print(f"Samsung Gallery Path: {result.gallery_path}")
  ```
* **Node.js (`generate_demo.js`):**
  ```javascript
  const { generate } = require('termux-diffusion');

  async function main() {
    const result = await generate({
      prompt: 'cyberpunk cat with neon collar in rainy alley',
      model: 'speed'
    });
    console.log('Output Path:', result.path);
    console.log('Gallery Path:', result.galleryPath);
  }
  main();
  ```

---

### 🎨 Scenario 3: Custom Models & External Weights (커스텀 모델 사용)

#### Case A: Direct Hugging Face Repository
Provide any Hugging Face repo ID and `.gguf` file path. The engine auto-streams, caches, and runs it:
```python
from termux_diffusion import generate

generate(
    "1girl, anime masterpiece, vibrant colors",
    model="second-state/DreamShaper-8-GGUF/dreamshaper-8-Q4_k.gguf"
)
```

#### Case B: Local File Reference (Internal Storage or SD Card)
```python
generate(
    "beautiful fantasy castle at sunrise",
    model="~/storage/downloads/my_custom_model.gguf"
)
```

#### Case C: Model Aliasing (`register_model`)
```python
from termux_diffusion import register_model, generate

# Register alias once
register_model("waifu", repo_id="second-state/DreamShaper-8-GGUF", filename="dreamshaper-8-Q4_k.gguf")

# Invoke cleanly anytime
generate("magical forest with fairies", model="waifu")
```

#### 🚀 Hardware Acceleration Target (`device`):
```python
# Offload compute to mobile GPU (Adreno / Samsung Xclipse)
generate("speedy race car", model="speed", device="gpu")
```

---

## 2. Built-in Model Hub Presets

| Preset | Model & Quantization | Size | Steps | Latency (Exynos 1380) | Key Workload |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **`"realistic"`** | Realistic Vision V6.0 B1 (Q4_K) | 1.62 GB | 10 | ~25 min | High-fidelity photorealism (portraits, skin, lighting) |
| **`"speed"`** | Stable Diffusion 1.5 Base (Q4_1) | 1.59 GB | 10 | ~15 min | General drafting and rapid composition |
| **`"sdxs"`** | SDXS 512-0.9 Mobile (Q4_0) | **450 MB** | **2 - 3** | **~2.5 min** | Ultra-low latency mobile prototyping |
| **`"turbo"`** | SD Turbo (Q4_0) | 1.20 GB | 1 | ~4 min | Single-step real-time inference |
| **`"anime"`** | DreamShaper 8 (Q4_K) | 1.65 GB | 10 | ~20 min | 2D / 2.5D stylized illustration and animation art |

---

## 3. Comprehensive 100% Function & API Reference

### 3.1 `generate(...)` — Primary Synthesis Function

Full parameter specification for Python and Node.js:

```python
from termux_diffusion import generate

result = generate(
    prompt="A majestic lion standing on a cliff at sunset, 8k, photorealistic",
    negative_prompt="blurry, low quality, distorted, bad anatomy",
    model="realistic",          # Preset name ('realistic', 'speed', 'sdxs', 'turbo', 'anime'), HuggingFace ID, or local file
    device="cpu",               # 'cpu', 'gpu', 'opencl', or 'vulkan'
    output="lion.png",          # Custom destination file path (default: output_<timestamp>.png)
    width=512,                  # Image width in pixels (multiple of 64, default: 512)
    height=512,                 # Image height in pixels (multiple of 64, default: 512)
    steps=10,                   # Sampling steps (default: 10, sdxs: 2, turbo: 1)
    cfg_scale=4.0,              # Classifier-Free Guidance scale (default: 4.0)
    seed=-1,                    # Random seed (-1 for randomized generation)
    threads=6,                  # Core allocation (default: max(1, cpu_count - 2))
    wake_lock=True,             # Hold Android CPU WakeLock to prevent sleep
    export_gallery=True,        # Sync to ~/storage/pictures/TermuxDiffusion & trigger MediaScanner
    timeout=3600.0,             # Max execution timeout in seconds
    model_cache_dir=None        # Custom cache directory path
)

# Return Object: GenerationResult
print("Local Path:", result.path)
print("Gallery Path:", result.gallery_path)
print("Elapsed Seconds:", result.elapsed_sec)
print("Seed Used:", result.seed)
```

```javascript
// Node.js Equivalent
const { generate } = require('termux-diffusion');

const result = await generate({
  prompt: 'A majestic lion standing on a cliff at sunset, 8k, photorealistic',
  negativePrompt: 'blurry, low quality, distorted',
  model: 'realistic',
  device: 'cpu',
  output: 'lion.png',
  width: 512,
  height: 512,
  steps: 10,
  cfgScale: 4.0,
  seed: -1,
  threads: 6,
  wakeLock: true,
  exportGallery: true,
  timeout: 3600
});
```

---

### 3.2 Model Cache & Storage Management APIs

```python
from termux_diffusion import (
    set_cache_dir,       # Route cache to external storage / SD card
    get_cache_dir,       # Inspect active cache directory
    download_model,      # Pre-download models in background with progress
    register_model,      # Register custom Hugging Face model presets
    list_cached_models,  # List all downloaded .gguf files and sizes
    clear_cache          # Delete cached weights to reclaim storage
)

# 1. Configure custom cache path (e.g. SD Card)
set_cache_dir("~/storage/external-1/ai_models")

# 2. Pre-fetch weights with real-time streaming progress
download_model("sdxs", force=False)

# 3. Register custom alias
register_model(
    name="cyber-waifu",
    repo_id="second-state/DreamShaper-8-GGUF",
    filename="dreamshaper-8-Q4_k.gguf",
    description="DreamShaper 8 Q4_K model for stylized anime portraits"
)

# 4. Inspect downloaded models
cached = list_cached_models()
for item in cached:
    print(f"Model: {item['name']}, Size: {item['size_mb']:.1f}MB, Path: {item['path']}")

# 5. Purge model cache
# clear_cache()
```

---

### 3.3 Hardware Diagnostics & Platform Inspection APIs

```python
from termux_diffusion import (
    get_memory_info,            # RAM and zRAM (Samsung RAM Plus) stats
    get_optimal_thread_count,   # Optimal CPU thread affinity count
    is_android_termux,          # True if running inside Android Termux
    run_doctor,                 # Automated 6-point system diagnostic health check
    export_to_android_gallery,  # Manually broadcast any image to Android Gallery
    TermuxWakeLock              # Context manager for holding CPU WakeLock
)

# Inspect memory safety
mem = get_memory_info()
print(f"Total RAM: {mem.total_mb}MB, Free: {mem.free_mb}MB, Swap: {mem.swap_total_mb}MB")

# Run full system diagnostic
report = run_doctor()
print(f"Doctor Health Status: {'PASSED' if report.is_ready else 'FAILED'}")
```

---

## 4. CLI Command Reference Manual

| Command | Arguments | Description |
| :--- | :--- | :--- |
| `termux-diffusion generate` | `"<prompt>" [-m model] [--device cpu\|gpu] [--steps N] [--cfg N] [-o file.png] [-W 512] [-H 512] [-t threads] [-s seed] [--no-wakelock] [--no-gallery]` | Executes diffusion inference with custom options |
| `termux-diffusion download` | `<model_name>` | Pre-downloads and caches model weights |
| `termux-diffusion models` | *(None)* | Displays catalog of available presets and cached models |
| `termux-diffusion doctor` | *(None)* | Runs automated 6-phase pre-flight diagnostic health check |
| `termux-diffusion install` | `[--force]` | Compiles native ARM64 Bionic engine binary |
| `termux-diffusion clear` | *(None)* | Clears cached weights to free storage |

---

## 5. Architecture & Security Isolation

* **Zero PRoot / Zero Root:** Executes directly against native Android Bionic `libc` with ARM64 NEON SIMD optimizations, avoiding virtual container memory amplification.
* **Low Memory Killer (LMK) Guard:** Validates physical RAM and Android zRAM (Samsung RAM Plus) before allocating tensor graphs.
* **Process Reaper:** Intercepts `SIGINT` / `SIGTERM` / `KeyboardInterrupt` to forcefully clean up orphaned child `sd-cli` processes.
* **WakeLock Shield:** Automatically prevents CPU sleep states when the smartphone screen turns off during lengthy inference.

---

## 6. The AMEVA Mobile AI & Automation Ecosystem

* **📱 [Termux-Playwright](https://github.com/uno-km/termux-playwright-demo)** ([PyPI](https://pypi.org/project/termux-playwright/) | [npm](https://www.npmjs.com/package/termux-playwright) | [📖 Official Docs](https://uno-km.github.io/termux-playwright-demo/)): Production headless Chromium browser automation for Android Termux.
  * **Python:** `pip install termux-playwright && termux-playwright-install`
  * **Node.js:** `npm install termux-playwright && npx termux-playwright install`

---

## 7. License

Released under the **MIT License**. Maintained by **uno-km (Eunho Kim)**.
