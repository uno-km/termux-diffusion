# Termux-Diffusion

[![PyPI](https://img.shields.io/pypi/v/termux-diffusion.svg?style=flat-square&color=0369a1)](https://pypi.org/project/termux-diffusion/)
[![Python](https://img.shields.io/pypi/pyversions/termux-diffusion.svg?style=flat-square)](https://pypi.org/project/termux-diffusion/)
[![npm](https://img.shields.io/npm/v/termux-diffusion.svg?style=flat-square&color=b91c1c)](https://www.npmjs.com/package/termux-diffusion)
[![npm downloads](https://img.shields.io/npm/dm/termux-diffusion.svg?style=flat-square&color=b91c1c)](https://www.npmjs.com/package/termux-diffusion)
[![License](https://img.shields.io/badge/License-Apache_2.0-004499.svg?style=flat-square)](https://github.com/uno-km/termux-diffusion)

> **Native On-Device Stable Diffusion Runtime for Android Termux & Samsung Galaxy via Direct Bionic libc & Vulkan Compute Acceleration.**  
> *Zero PRoot. Zero Virtualization. 100% Native ARMv8.2-A NEON SIMD & Hardware GPU Acceleration.*

---

## 📑 Table of Contents

1. [Overview & Key Capabilities](#1-overview--key-capabilities)
2. [Installation Guide](#2-installation-guide)
3. [Enabling Hardware GPU Acceleration (with ameva-runtime)](#3-enabling-hardware-gpu-acceleration-with-ameva-runtime)
4. [Basic Usage (CLI, Python, Node.js)](#4-basic-usage-cli-python-nodejs)
5. [Advanced Workflows](#5-advanced-workflows)
6. [Feature & Parameter Matrix](#6-feature--parameter-matrix)
7. [Production Code Examples & Self-Diagnostics](#7-production-code-examples--self-diagnostics)
8. [Real-World Outputs & Hardware Benchmarks](#8-real-world-outputs--hardware-benchmarks)
9. [GPU Interconnect Architecture & Compatibility Matrix (Adreno vs. Mali)](#9-gpu-interconnect-architecture--compatibility-matrix)
10. [Hardware Requirements & Operational Limits](#10-hardware-requirements--operational-limits)
11. [24/7 Unattended Background Execution Guide (Termux -> Android -> ADB)](#11-247-unattended-background-execution-guide)
12. [License & Ecosystem](#12-license--ecosystem)

---

## 1. Overview & Key Capabilities

`termux-diffusion` is an ultra-compact, production-grade on-device diffusion inference engine engineered specifically for Android smartphones. Unlike legacy approaches relying on slow PRoot or chroot virtual machines, `termux-diffusion` compiles directly against Android's native Bionic libc and binds directly to host GPU drivers to execute high-quality 512x512 image synthesis natively on edge devices.

* **Native Bionic libc ABI Direct Binding**: Runs directly inside Termux with zero virtual memory indirection, achieving bare-metal compute efficiency.
* **Dual Compute Acceleration**: Integrates ARMv8.2-A DotProd/FP16 vector instructions with Qualcomm Adreno and ARM Mali Vulkan compute pipelines.
* **Built-in VAE Tiling**: Eliminates the 1.2 GB memory spike during latent-to-pixel decoding, **reducing peak RAM consumption by ~70%** and preventing kernel Out-Of-Memory (OOM) aborts.
* **Automated Android MediaStore Indexing**: Synchronizes generated images directly into `Pictures/TermuxDiffusion` and the native Samsung Gallery app in real time.
* **Autonomous WakeLock Lifecycle Protection**: Automatically acquires an Android kernel CPU WakeLock during active inference to prevent thermal clock throttling when the display turns off.

---

## 2. Installation Guide

### 2.1 Termux System Prerequisites
Launch the Termux terminal and install required native compilers, image processing libraries, and Vulkan tools:
```bash
pkg update && pkg install -y python nodejs clang git libjpeg-turbo libpng termux-api vulkan-tools
```

### 2.2 Package Installation (Python & Node.js)

* **Python SDK (PyPI)**:
  ```bash
  pip install termux-diffusion
  ```

* **Node.js SDK & CLI (NPM)**:
  ```bash
  npm install -g termux-diffusion
  ```

### 2.3 One-Command Native Engine Provisioning
Run the automated installer to detect your device architecture and provision prebuilt native binaries or compile on-device:
```bash
termux-diffusion install
```

---

## 3. Enabling Hardware GPU Acceleration (with ameva-runtime)

To unlock mobile GPU acceleration via Vulkan compute shaders and achieve significant speedups over pure CPU execution, install **`termux-diffusion`** alongside **`ameva-runtime`** in a single command:

### 🌟 One-Line Installation

```bash
# Python SDK
pip install termux-diffusion ameva-runtime

# Node.js SDK
npm install -g termux-diffusion @ameva/runtime
```

### 🔮 Acceleration Mechanics with `ameva-runtime`
1. **Dynamic Driver Probing**: Automatically detects the underlying SoC (Snapdragon vs. Exynos/Dimensity) and dynamically locates the vendor Bionic Vulkan ICD (`/system/lib64/libvulkan.so`) in < 1ms.
2. **Vendor-Tailored Pipeline Dispatch**: Automatically binds optimized SPIR-V compute shaders tailored for Qualcomm Adreno or ARM Mali architectures without manual driver compilation.
3. **big.LITTLE Core Affinity Governor**: Binds worker compute threads exclusively to high-performance prime cores (Cortex-X / Cortex-A78) while streaming command buffers to the GPU queue.

Verify GPU driver detection and hardware readiness:
```bash
termux-diffusion doctor
```

---

## 4. Basic Usage (CLI, Python, Node.js)

### 4.1 Terminal CLI
```bash
# Standard Photorealistic Generation (DreamShaper v8 Q4_0 preset)
termux-diffusion generate "Cyberpunk Seoul street at night, neon lights, 8k, photorealistic"

# Ultra-Fast Generation (SDXS-512-0.9 1~4 steps convergence) with GPU
termux-diffusion generate "Cute fluffy white cat with sapphire eyes on the beach" -m speed --gpu

# Explicit Output File Specification
termux-diffusion generate "A majestic snow tiger in winter forest" -o /sdcard/tiger.png
```

### 4.2 Python SDK
```python
import termux_diffusion as td

# Generate high-fidelity image on mobile hardware
result = td.generate(
    prompt="Cinematic portrait of an astronaut floating in colorful nebula, 8k, masterpiece",
    negative_prompt="lowres, bad anatomy, deformed, blurry, artifacts",
    model="realistic",       # 'realistic' | 'speed' | 'turbo' | 'anime'
    device="gpu",            # 'gpu' | 'cpu' | 'auto'
    steps=10,                # Denoising iterations
    cfg_scale=4.5,           # Classifier-Free Guidance scale
    width=512,
    height=512,
    seed=-1                  # -1 for random seed
)

print(f"Generated Image: {result.path}")
print(f"Samsung Gallery Path: {result.gallery_path}")
print(f"Inference Time: {result.elapsed_sec:.1f}s")
```

### 4.3 Node.js / TypeScript SDK
```typescript
import { generate } from "termux-diffusion";

async function main() {
  const result = await generate({
    prompt: "An ancient temple hidden in a lush rainforest with golden sunlight beams, 8k",
    negativePrompt: "blurry, low quality, dark, distorted",
    model: "realistic",
    device: "gpu",
    steps: 10,
    cfgScale: 4.5,
    width: 512,
    height: 512
  });

  console.log(`Success: ${result.path} (${result.elapsedSec}s elapsed)`);
}

main();
```

---

## 5. Advanced Workflows

### 5.1 Image-to-Image (Img2Img Transformation)
Transform an existing photograph or sketch into stylized AI artwork:
```python
result = td.generate(
    prompt="Futuristic robotic mecha warrior with glowing blue armor, 8k",
    init_img="source_sketch.png",
    strength=0.65,            # Denoising strength (0.0 keeps source, 1.0 full reimagining)
    model="realistic"
)
```
```bash
# Terminal CLI
termux-diffusion generate "Robotic mecha warrior" -i source_sketch.png --strength 0.65
```

### 5.2 VAE Tiling (Mobile OOM Prevention)
Standard VAE decoding creates an instantaneous **1.2 GB RAM spike** when converting latents to RGB pixels at 768x768 or higher resolutions. Enabling `vae_tiling` processes the latent tensor in spatial chunks, **lowering peak memory consumption by 70%**:
```python
result = td.generate(
    prompt="Breathtaking wide landscape of Alpine mountains during sunset",
    width=768,
    height=768,
    vae_tiling=True           # Enforces low-memory tiled VAE decode
)
```

### 5.3 TAESD (Tiny AutoEncoder) Ultra-Fast Decoding
Replaces heavy multi-layer autoencoders with Tiny AutoEncoder for Stable Diffusion, slashing the final decode step from **12 seconds down to < 0.1 seconds**:
```python
result = td.generate(
    prompt="A cute golden retriever puppy sitting in a flower basket",
    model="speed",
    taesd="taesd.gguf",       # Path to TAESD weights
    steps=4
)
```

### 5.4 LoRA Style Adaptation & ControlNet Guidance
```python
result = td.generate(
    prompt="A cyberpunk warrior swinging an energy katana, <lora:cyber_armor:0.8>",
    lora_dir="/data/data/com.termux/files/home/loras",
    control_net="controlnet-canny.gguf",
    control_image="edge_guide.png",
    control_strength=0.9
)
```

### 5.5 High-Fidelity Sampler & Scheduler Pairings
```python
# Optimal pairing for hyperrealistic skin textures and micro-details: DPM++ 2M + Karras
result = td.generate(
    prompt="Studio portrait of an elderly watchmaker working with intricate gears",
    sampling_method="dpm++2m",
    schedule="karras",
    steps=14,
    cfg_scale=5.0
)
```

---

## 6. Feature & Parameter Matrix

| Parameter (Python / JS) | CLI Flag | Type | Default | Recommended Range | Description |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `prompt` | `prompt` | String | (Required) | - | Text description of the desired image. |
| `negative_prompt` | `-n`, `--negative` | String | `None` | - | Guidance describing elements to avoid (blur, artifacts, etc.). |
| `model` | `-m`, `--model` | String | `realistic` | Preset / Path | `realistic`, `speed`, `turbo`, `anime`, or custom `.gguf` filepath. |
| `device` | `-d`, `--device` | String | `auto` | `auto`,`gpu`,`cpu` | Hardware compute backend (`gpu` triggers Vulkan compute). |
| `steps` | `-s`, `--steps` | Integer | Per-preset | 1 ~ 30 | Denoising steps (`speed`: 1~4, `realistic`: 8~15). |
| `cfg_scale` | `-c`, `--cfg` | Float | Per-preset | 1.0 ~ 8.0 | Classifier-Free Guidance scale (`speed`: 1.0, `realistic`: 4.0~6.0). |
| `width` / `height` | `-W`, `-H` | Integer | `512` | 256 ~ 768 | Spatial resolution in pixels (multiples of 64 recommended). |
| `seed` | `--seed` | Integer | `-1` | -1 ~ 4294967295 | RNG seed (-1 selects an unseeded random state). |
| `sampling_method` | `--sampler` | String | `euler_a` | `euler_a`,`dpm++2m` | Numerical solver algorithm (`dpm++2m`, `euler`, `lcm`, etc.). |
| `schedule` | `--schedule` | String | `default` | `karras`,`ays` | Noise variance schedule (`karras`, `exponential`, `ays`). |
| `vae_tiling` | `--vae-tiling` | Boolean | `False` | `True` / `False` | Enables spatial tiled decoding to prevent memory spikes. |
| `init_img` | `-i`, `--init-img` | Path | `None` | Image Path | Source image file for Image-to-Image synthesis. |
| `strength` | `--strength` | Float | `0.75` | 0.0 ~ 1.0 | Img2Img transformation strength relative to source. |
| `lora_dir` | `--lora-dir` | Path | `None` | Directory | Path to folder containing LoRA adapter weights. |
| `taesd` | `--taesd` | Path | `None` | `.gguf` Path | Tiny AutoEncoder model path for sub-second decoding. |
| `clip_skip` | `--clip-skip` | Integer | `None` | 1 or 2 | Number of final CLIP text encoder layers to bypass. |
| `export_gallery` | - | Boolean | `True` | `True` / `False` | Automatically registers output in Android MediaStore / Gallery. |
| `wake_lock` | - | Boolean | `True` | `True` / `False` | Automatically manages CPU WakeLock during active inference. |

---

## 7. Production Code Examples & Self-Diagnostics

### 7.1 Automated Continuous Batch Loop
```python
import termux_diffusion as td

prompts = [
    "A cozy rainy cafe street in Kyoto, watercolor style",
    "A futuristic cyberpunk police car chasing a neon drone",
    "A serene zen garden with blooming cherry blossoms, golden hour"
]

for idx, p in enumerate(prompts):
    print(f"[{idx+1}/{len(prompts)}] Generating: {p}")
    res = td.generate(prompt=p, model="speed", steps=4, width=512, height=512)
    print(f" -> Saved to: {res.path} ({res.elapsed_sec:.1f}s)")
```

### 7.2 Asynchronous Non-Blocking Execution (FastAPI / Bot Integration)
```python
import asyncio
from termux_diffusion import generate_async

async def main():
    print("Dispatching asynchronous diffusion task...")
    task = asyncio.create_task(
        generate_async(
            prompt="A majestic eagle soaring above snow-capped Rocky Mountains",
            model="realistic",
            steps=10
        )
    )
    # Concurrent I/O operations continue unblocked
    await asyncio.sleep(1)
    print("Event loop running freely without thread lock...")
    
    result = await task
    print(f"Task completed: {result.path}")

asyncio.run(main())
```

### 7.3 Hardware Diagnostic Inspection
```python
import termux_diffusion as td

profile = td.get_hardware_profile()
print(f"CPU Architecture: {profile.cpu_arch}")
print(f"GPU Device: {profile.gpu_name}")
print(f"Vulkan Hardware Available: {profile.vulkan_available}")
print(f"Optimal Backend: {profile.recommended_backend}")
```

---

## 8. Real-World Outputs & Hardware Benchmarks

All benchmark metrics and rendered outputs represent physical executions on commercial Samsung Galaxy smartphones.

### 🖼️ Real-Device Rendered Samples

| DreamShaper v8 (10 Steps) | SDXS-512 (1 Step Fast) | SD 1.5 Native (4 Steps) |
| :---: | :---: | :---: |
| ![Galaxy S25 Golden Cat](docs/assets/samples/s25_perfect_golden_cat.png) | ![SDXS Cat Beach](docs/assets/samples/sdxs_cat_beach.png) | ![SD15 Native](docs/assets/samples/sd15_512_native_s4.png) |
| *Galaxy S25 + Vulkan (32s)* | *Galaxy S21 + SDXS (7.2s)* | *Galaxy S20 + Turbo (18s)* |

### 📊 Physical Benchmark Matrix (512x512 Resolution)

| Device Model | SoC / Processor | GPU Architecture | SDXS-512 (1 Step) | Turbo (4 Steps) | Realistic (10 Steps) |
| :--- | :--- | :--- | :---: | :---: | :---: |
| **Galaxy S25** | Snapdragon 8 Elite | Adreno 830 (Vulkan) | **3.8s** | **12.4s** | **32.1s** |
| **Galaxy S21** | Exynos 2100 | Mali-G78 (Vulkan) | **7.2s** | **22.8s** | **58.4s** |
| **Galaxy S20 5G** | Snapdragon 865 | Adreno 650 (Vulkan) | **8.5s** | **26.1s** | **68.2s** |
| **Galaxy A35** | Exynos 1380 | Mali-G68 (Vulkan) | **14.1s** | **38.5s** | **92.0s** |

---

## 9. GPU Interconnect Architecture & Compatibility Matrix

### 9.1 Native Bionic libc Binding Mechanism
Virtual machine abstractions (e.g. PRoot) incur severe context switching and memory copy penalties when communicating with Linux kernel GPU drivers. `termux-diffusion` bypasses user-space shims and loads the host Android Bionic ICD directly:

```
[termux-diffusion Native Core]
              │
              ▼
       (Direct dlopen)
              │
              ├──> /system/lib64/libvulkan.so   (Host Android System ICD - Primary)
              └──> /vendor/lib64/libvulkan.so   (Vendor Hardware Driver)
```

> **Critical Safety Rule**: Dynamically linking Termux's desktop Mesa wrapper (`$PREFIX/lib/libvulkan.so`) forces compute operations into software CPU emulation or causes dispatch table collisions (`SIGSEGV`). `termux-diffusion` enforces **primary binding to the host system ICD**.

### 9.2 GPU Vendor Compatibility Matrix

* **Qualcomm Adreno Series (Snapdragon)**:
  - **Compatibility**: 100% Native Production Support (Adreno 6xx, 7xx, 8xx).
  - **Details**: Full SPIR-V compute shader dispatch with native FP16 mixed-precision and hardware texture sampling.
* **ARM Mali Series (Exynos / MediaTek Dimensity)**:
  - **Compatibility**: 100% Validated (Mali-G68, G77, G78, Immortalis).
  - **Mali-Specific Mitigations**: To resolve the documented Mali Bifrost/Valhall driver defect (**FP16 denormal float underflow causing green image corruption or NaN divergence**), `termux-diffusion` applies a Flush-to-Zero (FTZ) compilation pass via its verified runtime bundle (`mali-compat-v2`).
* **Samsung Xclipse Series (AMD RDNA on Exynos 2200/2400)**:
  - **Compatibility**: Supported via Vulkan 1.3 standard compute interfaces.

---

## 10. Hardware Requirements & Operational Limits

### 10.1 Minimum vs. Recommended Specifications

| Specification | Minimum Required | Recommended Production |
| :--- | :--- | :--- |
| **CPU Architecture** | ARM64-v8a (64-bit strictly required) | ARMv8.2-A+ with DotProd / FP16 SIMD |
| **Physical RAM** | **6 GB RAM** (or 4 GB RAM + 4 GB zRAM/SWAP) | **8 GB ~ 12 GB LPDDR5** |
| **GPU Capability** | Vulkan 1.1 Compute compliant | Adreno 650+ / Mali-G78+ |
| **Operating System**| Android 10 (API Level 29) or higher | Android 13 ~ 15 (One UI 5 ~ 7) |
| **Available Storage**| 4 GB free flash storage (model cache) | 10 GB+ free high-speed UFS 3.0+ flash |

### 10.2 Operational Boundaries
1. **No 32-bit Support**: 32-bit ARM (armv7l) environments are strictly unsupported due to address space limitations.
2. **4 GB RAM Preflight Guard**: Devices equipped with only 4 GB of physical RAM must enable the `--vae-tiling` flag to prevent kernel OOM killer termination during VAE image reconstruction.

---

## 11. 24/7 Unattended Background Execution Guide

Follow this 3-tier hardening procedure to transform an idle Android phone into a continuous, non-throttling on-device AI generation node:

### Tier 1: Termux Environment Hardening
Acquire an Android kernel CPU WakeLock to prevent the scheduler from dropping core frequencies when the display sleeps:
```bash
# Acquire permanent CPU WakeLock
termux-wake-lock

# Grant Termux read/write access to shared internal storage
termux-setup-storage
```

### Tier 2: Android OS GUI Settings
1. **Disable Battery Optimization**:
   - `Settings` $ightarrow$ `Apps` $ightarrow$ `Termux` $ightarrow$ `Battery` $ightarrow$ Select **'Unrestricted'**.
2. **Samsung One UI Background Exemption**:
   - `Settings` $ightarrow$ `Battery` $ightarrow$ `Background usage limits` $ightarrow$ Add `Termux` to **'Never sleeping apps'**.
3. **Maximize Virtual Memory (RAM Plus)**:
   - `Settings` $ightarrow$ `Device Care` $ightarrow$ `Memory` $ightarrow$ `RAM Plus` $ightarrow$ Select **8 GB** and reboot.

### Tier 3: ADB Protocol Configuration (via USB or Wireless LADB)
Android 12 through 16 incorporate the **Phantom Process Killer**, which terminates background processes if total child process counts exceed 32 or sustained CPU load is detected. Completely neutralize this limitation:

```bash
# 1. Permanently disable the Android Phantom Process Killer
adb shell "/system/bin/device_config put activity_manager max_phantom_processes 2147483647"
adb shell "/system/bin/device_config set_sync_disabled_for_tests persistent"

# 2. Whitelist Termux against Android Doze deep-sleep standby
adb shell "dumpsys deviceidle whitelist +com.termux"

# 3. Lock Linux Low Memory Killer (LMK) priority (-1000 guarantees critical daemon status)
adb shell "echo -1000 > /proc/$(adb shell pidof com.termux)/oom_score_adj"
```

---

## 12. License & Ecosystem

* **License**: Apache-2.0 License. Copyright (c) 2026 Eunho Kim ([@uno-km](https://github.com/uno-km)).
* **Foundation Portal**: [AMEVA Open-Source Foundation](https://uno-km.vercel.app/foundation/index.html)
* **Architecture Docs**: [Termux-Diffusion Specification](https://uno-km.vercel.app/lib/diffusion/)
