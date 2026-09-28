# Termux-Diffusion (Python)

[![PyPI](https://img.shields.io/pypi/v/termux-diffusion.svg?style=flat-square&color=0369a1)](https://pypi.org/project/termux-diffusion/)
[![Python](https://img.shields.io/pypi/pyversions/termux-diffusion.svg?style=flat-square)](https://pypi.org/project/termux-diffusion/)
[![License](https://img.shields.io/badge/License-Apache_2.0-004499.svg?style=flat-square)](https://github.com/uno-km/termux-diffusion)

> **Official Z-Image Turbo (6.0B DiT) & Pure Native On-Device Diffusion Acceleration for Android Termux & Samsung Galaxy.**  
> *Zero PRoot. Zero Virtualization. 100% Native ARM64 Bionic libc, Khronos Vulkan 1.1+ GPU Shaders & NEON SIMD Vector Engine.*

---

## 🚀 Major Breakthrough: 6.0B DiT (Z-Image Turbo) Sovereign Mobile Execution

`termux-diffusion v1.8.0` introduces official production support for **Z-Image Turbo**, empowering mobile devices to execute modern **6.0 Billion Parameter Diffusion Transformers (DiT)** natively on-device.

### 🌟 Tri-Engine Asymmetric Architecture
* **Text Encoder (CPU 4-Core)**: 4.0B LLM (`Qwen3-4B-Instruct-2507-Q2_K.gguf`) performs dense context embedding on CPU Big/Prime cores (`clip_on_cpu=True`).
* **DiT Denoising Backbone (Vulkan GPU)**: 6.0B Diffusion Transformer (`z_image_turbo-Q2_K.gguf`) accelerated via Khronos Vulkan compute shaders with Tiled Flash Attention (`diffusion_fa=True`).
* **Ultra-Fast VAE Decoder (CPU)**: 10MB Tiny AutoEncoder for FLUX.1 (`taef1.safetensors`) completes latent decoding rapidly without memory spikes (`vae_on_cpu=True`).
* **Layer Streaming (`stream_layers=True`)**: Breaks through mobile memory limits by streaming layers into Vulkan VRAM sequentially, maintaining a strict **1.0 GB VRAM footprint** (`max_vram="vulkan0=1"`) and completely eliminating Android Low Memory Killer (LMK) aborts.

---

## 📸 Sovereign Physical Verification: Galaxy S21 DiT 8-Step Output

* **Verification Image**: [Galaxy S21 Z-Image Turbo 8-Step PNG Artifact](https://raw.githubusercontent.com/uno-km/termux-diffusion/main/docs/research/s21_z_image_turbo_8step.png)
* **Verification Prompt (Ground Truth)**:
  ```text
  "A cinematic photo of a neon cybernetic tiger walking in Seoul street at night"
  ```
* **Verified Input Parameter Engineering**:
  * `steps=8` (Full numerical convergence ODE solver)
  * `cfg_scale=1.0` (Optimal guidance for distilled DiT architecture)
  * `sampler="euler"` (1st-order Ordinary Differential Equation solver)
  * `device="vulkan"` (Physical GPU acceleration)
  * `diffusion_fa=True` (Tiled Flash Attention enabled)
  * `stream_layers=True` (Layer residency streaming over AXI bus)
  * `max_vram="vulkan0=1"` (Strict 1.0 GB VRAM ceiling, Zero-LMK protection)
  * `clip_on_cpu=True` (Offloads LLM prompt embedding to CPU Big/Prime cores)
  * `vae_on_cpu=True` (Prevents GPU VRAM allocation collisions during decoding)
  * `taesd="auto"` (Ultra-fast 10MB FLUX.1 latent decoder)
* **Optical Realism**: Specular light scattering from neon signboards on wet Seoul asphalt road surfaces, razor-sharp cybernetic armor plates, and micro-texture whiskers cleanly isolated from background noise.
* **Runtime Stability**: 100% completion achieved with zero Out-of-Memory (LMK) aborts and zero thermal throttling termination.

### 🔬 Academic Research & Lab Report Reference
* **Full Technical Research Report**: [Galaxy S21 Z-Image Turbo Vulkan Research Report](https://github.com/uno-km/termux-diffusion/blob/main/docs/research/s21_z_image_turbo_vulkan_research_report.md)
* **AMEVA Edge Systems Lab (AESL)**: [https://uno-km.vercel.app/labs/](https://uno-km.vercel.app/labs/)

---

## 💻 Python SDK Installation & Practical User Manual

### 1. Installation & Provisioning
```bash
pkg update && pkg install -y python clang termux-api
pip install termux-diffusion
termux-diffusion install
```

### 2. Python API Practical Code Example

```python
import termux_diffusion as td

# 1. Official Z-Image Turbo 6.0B DiT Synthesis via Python API
image_path = td.generate(
    prompt="A cinematic photo of a neon cybernetic tiger walking in Seoul street at night",
    preset="z-image-turbo",
    steps=8,
    cfg_scale=1.0,
    sampler="euler",
    device="vulkan",
    diffusion_fa=True,
    stream_layers=True,
    max_vram="vulkan0=1",
    clip_on_cpu=True,
    vae_on_cpu=True,
    taesd="auto",
    output_path="/sdcard/Pictures/TermuxDiffusion/cyber_tiger_dit.png"
)
print(f"Generated via 6.0B DiT Tri-Engine: {image_path}")

# 2. Fast UNet Standard Inference (DreamShaper 8 LCM 6-Step)
lcm_path = td.generate(
    prompt="A cinematic photo of a neon cybernetic tiger walking in Seoul street at night",
    model="anime",
    steps=6,
    cfg_scale=1.5,
    sampler="lcm",
    device="vulkan",
    diffusion_fa=True,
    vae_on_cpu=True,
    output_path="/sdcard/Pictures/TermuxDiffusion/cyber_tiger_lcm.png"
)
print(f"Generated via DreamShaper 8 LCM: {lcm_path}")
```

---

## 🎛️ Python API Parameter Reference

| Argument | Type | Default | Engineering Purpose |
| :--- | :---: | :---: | :--- |
| `prompt` | `str` | *Required* | Text conditioning prompt |
| `width`, `height` | `int` | `512` | Image dimensions (multiples of 64) |
| `steps` | `int` | `8` (DiT) / `6` (LCM) | Numerical solver sampling iterations |
| `cfg_scale` | `float` | `1.0` (DiT) / `1.5` (LCM) | Classifier-Free Guidance scale weight |
| `sampler` | `str` | `"euler"` | Denoising ODE solver algorithm |
| `device` | `str` | `"vulkan"` | Accelerator device (`"vulkan"`, `"cpu"`) |
| `preset` | `str` | `"z-image-turbo"` | Verified configuration bundle |
| `stream_layers` | `bool` | `True` (DiT) | Enables dynamic layer streaming over AXI bus |
| `max_vram` | `str` | `"vulkan0=1"` | GPU memory ceiling (1.0 GB) to avert OS LMK aborts |
| `diffusion_fa` | `bool` | `True` | Flash Attention $O(N)$ memory reduction |
| `clip_on_cpu` | `bool` | `True` | Keeps LLM text encoder on CPU cores |
| `vae_on_cpu` | `bool` | `True` | Offloads VAE decode from GPU to host CPU |
| `taesd` | `str` | `"auto"` | Tiny AutoEncoder for ultra-fast latent decoding |
| `output_path` | `str` | `None` | Path to save output PNG artifact |

---

## 🌐 Official Documentation & Ecosystem Links
- [Official Architecture & API Reference](https://uno-km.vercel.app/lib/diffusion/)
- [Advanced Parameters Handbook](https://uno-km.vercel.app/lib/diffusion/advanced-parameters.html)
- [GitHub Repository](https://github.com/uno-km/termux-diffusion)
- [AMEVA Open-Source Foundation Portal](https://uno-km.vercel.app/foundation/index.html)

---

## 📄 License
Licensed under the Apache-2.0 License. Copyright (c) 2026 Eunho Kim ([@uno-km](https://github.com/uno-km)).
