# Termux-Diffusion

**Production On-Device AI Image Generation Framework for Android Termux & Samsung Galaxy**  
*Dual-Engine Architecture (Python & Node.js / TypeScript) with Native Bionic ARM64 Tensor Acceleration*

[![Official Documentation](https://img.shields.io/badge/Official_Docs-uno--km.vercel.app%2Flib%2Fdiffusion-004499?style=for-the-badge&logo=vercel&logoColor=white)](https://uno-km.vercel.app/lib/diffusion/)
[![PyPI Version](https://img.shields.io/pypi/v/termux-diffusion.svg?color=blue&style=for-the-badge)](https://pypi.org/project/termux-diffusion/)
[![npm Version](https://img.shields.io/npm/v/termux-diffusion.svg?color=red&style=for-the-badge)](https://www.npmjs.com/package/termux-diffusion)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg?style=for-the-badge)](LICENSE)
[![AMEVA Foundation](https://img.shields.io/badge/Foundation-AOSF_Tier_1-orange?style=for-the-badge)](https://uno-km.vercel.app/docs/foundation/)

<br/>

**[📖 Official Documentation Site (13 Languages)](https://uno-km.vercel.app/lib/diffusion/)** • **[🌌 AMEVA Foundation](https://uno-km.vercel.app/docs/foundation/)** • **[⚡ Quickstart](#1-quick-scenario-playbook)** • **[🏛️ Architecture](#2-why-termux-diffusion-architectural-pillars)** • **[📊 Benchmarks](#3-empirical-benchmarks)**

---

## 1. Quick Scenario Playbook

### [Install] Scenario 1: Clean Install (Fresh Setup on Android Termux)

Open the Termux application and execute the 2 commands for your preferred runtime:

#### [Python] Python:
```bash
# 1. Grant Android Storage Permission (Tap 'Allow' on the Android OS prompt)
termux-setup-storage

# 2. Install Toolchains & Provision Native Engine
pkg update -y && pkg install python clang make cmake git termux-api wget vulkan-loader vulkan-headers vulkan-tools -y
pip install termux-diffusion && termux-diffusion-install
```

#### [Node.js] Node.js / TypeScript:
```bash
# 1. Grant Android Storage Permission
termux-setup-storage

# 2. Install Toolchains & Provision Native Engine
pkg update -y && pkg install nodejs-lts clang make cmake git termux-api wget vulkan-loader vulkan-headers vulkan-tools -y
npm install -g termux-diffusion && npx termux-diffusion install
```

---

### [Instant] Scenario 2: Instant Generation (Ready to Run)

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

### [Models] Scenario 3: Custom Models & External Weights

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

#### [Engine] Hardware Acceleration Target (`device`):
```python
# Offload compute to mobile GPU (Adreno / Samsung Xclipse)
generate("speedy race car", model="speed", device="gpu")
```

---

## 2. Built-in Model Hub Presets & Golden Parameter Matrix

Each model architecture has distinct mathematical requirements for denoising steps, CFG scale, and samplers:

| Preset | Actual Model Checkpoint & Quantization | Architecture Type | Optimal Steps | Optimal CFG | Recommended Sampler & Scheduler | Workload & Visual Output |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| **`"sdxs"`** | `sdxs-512-tinySDdistilled_Q8_0` (651 MB) | 1-Step Distilled | **1 ~ 2** | **1.0** | `euler_a` (default) | **Ultra-Fast Mobile (1-2s): Clean & crisp, zero noise** |
| **`"anime"`** | `DreamShaper8_LCM_q4_0` (1.55 GB) | LCM 4~8-Step | **4 ~ 8** | **1.5 ~ 2.0** | `lcm` (default / karras) | **Sharp 2D/2.5D Anime: Clear line art & rich cel-shading** |
| **`"realistic"`** | `realisticVisionV60B1_v51HyperVAE_Q4_k` (1.55 GB) | Full SD1.5 Photoreal | **20 ~ 25** | **6.5 ~ 7.5** | `dpm2` / `euler_a` (karras) | **Ultra-Detailed Realism: Skin pores, realistic eyes, cinematic** |
| **`"speed"`** | `stable-diffusion-v1-5-Q4_1` (1.68 GB) | SD1.5 Base Q4_1 | **15 ~ 20** | **6.0 ~ 7.0** | `euler_a` / `dpm++2m` (karras) | **General Drafting: Balanced speed & composition fidelity** |
| **`"turbo"`** | `stable-diffusion-v1-5-pruned-emaonly_Q4_0` (1.49 GB) | SD1.5 Base Pruned | **15 ~ 20** | **6.0 ~ 7.0** | `euler_a` / `dpm++2m` (karras) | **Lightweight SD1.5: Fast base generation** |

> ⚠️ **Golden Rule for Distilled Models (`sdxs`, `turbo` ADD, `anime` LCM):**  
> Never use high CFG ($> 2.0$) or 2nd-order ODE samplers (`dpm2`, `heun`) on distilled 1~4 step models. Doing so breaks the compressed latent manifold and causes color blowout or over-smoothing blur. Keep `cfg_scale=1.0` with `euler_a` for crisp clarity!  
> 
> 💡 **Golden Rule for Full SD1.5 Models (`realistic`, `speed`, `turbo`):**  
> Full SD1.5 models require at least **15~20 steps** with `CFG=6.0~7.5` and quality-guard negative prompts to fully resolve high-frequency photorealistic details. Running them at 2~4 steps results in un-denoised noise.

---

## 3. Comprehensive 100% Function & API Reference

### 3.1 `generate(...)` - Primary Synthesis Function

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
    steps=10,                   # Sampling steps (default: 10, sdxs: 2, turbo: 8)
    cfg_scale=4.0,              # Classifier-Free Guidance scale (default: 4.0)
    seed=-1,                    # Random seed (-1 for randomized generation)
    threads=4,                  # Core allocation (default: auto-detected big cores)
    wake_lock=True,             # Hold Android CPU WakeLock to prevent sleep
    export_gallery=True,        # Sync to ~/storage/pictures/TermuxDiffusion & trigger MediaScanner
    timeout=1800,               # Max execution timeout in seconds
    auto_provision=False        # Auto-compile C++ engine if missing
)

# Return Object: GenerationResult
print("Local Path:", result.path)
print("Gallery Path:", result.gallery_path)
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
  threads: 4,
  wakeLock: true,
  exportGallery: true,
  timeout: 1800
});
```

### 3.2 High-Precision Controls & Advanced Parameters

`termux-diffusion` exposes full native C++ controls for fine-grained generation. For an exhaustive guide and all valid option lists, see **[ADVANCED_PARAMETERS.md](docs/ADVANCED_PARAMETERS.md)**.

```python
# 1. Advanced Sampler & Noise Schedule (dpm++2m + karras photorealism)
generate(
    "hyperrealistic portrait of a cyberpunk hacker, 8k",
    sampling_method="dpm++2m",
    schedule="karras",
    steps=12
)

# 2. VAE Tiling (Reduces peak RAM by ~70% on mobile devices)
generate("epic mountain landscape", width=768, height=768, vae_tiling=True)

# 3. Image-to-Image (Img2Img Transformation)
generate(
    "convert sketch into an oil painting of a castle",
    init_img="/sdcard/Pictures/my_sketch.png",
    strength=0.70
)

# 4. LoRA Adapter Weights Injection
generate(
    "cyberpunk warrior in battle armor <lora:cyber_armor:0.8>",
    lora_dir="/data/data/com.termux/files/home/loras"
)

# 5. CLIP Skip (Anime / DreamShaper Optimization)
generate("1girl, anime masterpiece, starry night", model="anime", clip_skip=2)

# 6. ControlNet Spatial Guidance
generate(
    "warrior posing heroically",
    control_net="~/models/cnet_openpose.gguf",
    control_image="~/pose_guide.png",
    control_strength=0.9
)
```

### 3.3 Model Cache & Storage Management APIs

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
    run_doctor,                 # Automated 7-tier system diagnostic health check
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
| `termux-diffusion generate` | `"<prompt>" [-m model] [--device cpu\|gpu] [-s steps] [-c cfg] [-t threads] [--sampler name] [--schedule name] [--vae-tiling] [-i img.png] [--strength 0.75] [--lora-dir dir] [--clip-skip 2] [--control-net cnet.gguf] [--control-image img.png] [--taesd taesd.gguf] [--seed N] [-o file.png]` | Executes diffusion inference with custom options |
| `termux-diffusion download` | `<model_name>` | Pre-downloads and caches model weights |
| `termux-diffusion models` | *(None)* | Displays catalog of available presets and cached models |
| `termux-diffusion doctor` | *(None)* | Runs automated 7-tier pre-flight diagnostic health check |
| `termux-diffusion install` | `[--force]` | Compiles native ARM64 Bionic engine binary |
| `termux-diffusion clear-cache` | *(None)* | Clears cached weights to free storage |

---

## 5. [Memory Optimization] Samsung RAM Plus & Low-Memory (RAM) Devices

For Android devices with 4GB - 8GB physical RAM, image synthesis models (1.5GB tensor graphs) require additional virtual swap space to prevent the Android Low Memory Killer (LMK) from terminating background tasks.

### 1. Enable Samsung RAM Plus (One UI 4 / 5 / 6)
1. Open **Settings** -> **Battery and device care** (or **Device Care**).
2. Tap **Memory** -> **RAM Plus**.
3. Select **+4 GB**, **+6 GB**, or **+8 GB** and restart your phone.
4. This expands available virtual memory (zRAM swap) to ensure Stable Diffusion runs seamlessly without memory pressure.

### 2. General Android / Non-Samsung Devices (zRAM Activation)
If your device does not have manufacturer RAM Plus, ensure zRAM swap is active:
```bash
# Verify active swap memory in Termux:
free -m
```

---

## 6. [Security] Android 12 / 13 / 14+ Phantom Process Killer Prevention

On Android 12 (API 31) and higher, the OS may kill background child processes (`sd-cli`) if the total process limit exceeds 32. Follow these recommended settings for 24/7 background stability:

### 1. Developer Options Configuration (Android 12L / 13 / 14+)
1. Open **Settings** -> **About phone** -> **Software information** -> Tap **Build number** 7 times to unlock Developer Options.
2. Go to **Settings** -> **Developer options**.
3. Enable **Disable child process restrictions**.

### 2. ADB One-Time Permanent Bypass (Optional via PC)
Connect phone to PC via USB debugging and run once:
```bash
adb shell "/system/bin/device_config set_sync_disabled_for_tests persistent"
adb shell "/system/bin/device_config put activity_manager max_phantom_processes 2147483647"
```

### 3. Battery Optimization & Background Notification
* **Unrestricted Battery:** Open **Settings** -> **Apps** -> **Termux** -> **Battery** -> Select **Unrestricted (Don't optimize)**.
* **WakeLock Notification:** Keep the Termux notification active and tap **Acquire wakelock** from the status bar dropdown.

---

## 7. Architecture & Security Isolation

* **Zero PRoot / Zero Root:** Executes directly against native Android Bionic `libc` with ARM64 NEON SIMD optimizations, avoiding virtual container memory amplification.
* **Zero Deception & Honest Diagnostics:** Zero fake logs. NPU/GPU/CPU hardware is probed transparently without deceptive rerouting.
* **Configurable Negative Prompt:** Negative prompt defaults to `None` with zero bias against subjects, configurable per-call or globally.
* **Process Reaper:** Intercepts `SIGINT` / `SIGTERM` / `KeyboardInterrupt` to forcefully clean up orphaned child `sd-cli` processes.
* **WakeLock Shield:** Automatically prevents CPU sleep states when the smartphone screen turns off during lengthy inference.

---

## 8. The AMEVA Mobile AI & Automation Ecosystem

* **[Termux-Playwright](https://github.com/uno-km/termux-playwright)** ([PyPI](https://pypi.org/project/termux-playwright/) | [npm](https://www.npmjs.com/package/termux-playwright) | [Official Docs](https://uno-km.github.io/termux-playwright/)): Production headless Chromium browser automation for Android Termux.
  * **Python:** `pip install termux-playwright && termux-playwright-install`
  * **Node.js:** `npm install -g termux-playwright && npx termux-playwright install`

---

## 9. Disclaimer (면책 조항)

> **Disclaimer:**  
> *Termux-Diffusion is an independent open-source project developed for the Android Termux environment and is not officially affiliated with, endorsed by, or sponsored by the Termux project.*  
> 
> *(본 프로젝트는 안드로이드 Termux 환경을 위해 개발된 독립적인 오픈소스 라이브러리이며, Termux 공식 프로젝트와 직접적인 제휴 관계가 아닙니다.)*

---

## 10. License

Released under the **MIT License**. Maintained by **uno-km (Eunho Kim)**.
