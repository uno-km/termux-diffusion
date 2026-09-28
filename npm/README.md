# Termux-Diffusion (Node.js & TypeScript)

[![npm](https://img.shields.io/npm/v/termux-diffusion.svg?style=flat-square&color=b91c1c)](https://www.npmjs.com/package/termux-diffusion)
[![npm downloads](https://img.shields.io/npm/dm/termux-diffusion.svg?style=flat-square&color=b91c1c)](https://www.npmjs.com/package/termux-diffusion)
[![License](https://img.shields.io/badge/License-Apache_2.0-004499.svg?style=flat-square)](https://github.com/uno-km/termux-diffusion)

> **Official Z-Image Turbo (6.0B DiT) & Pure Native On-Device Diffusion Acceleration for Android Termux & Samsung Galaxy.**  
> *Zero PRoot. Zero Virtualization. 100% Native ARM64 Bionic libc, Khronos Vulkan 1.1+ GPU Shaders & NEON SIMD Vector Engine.*

---

## 🚀 Major Breakthrough: 6.0B DiT (Z-Image Turbo) Sovereign Mobile Execution

`termux-diffusion v1.8.0` introduces official production support for **Z-Image Turbo**, empowering mobile devices to execute modern **6.0 Billion Parameter Diffusion Transformers (DiT)** natively on-device.

### 🌟 Tri-Engine Asymmetric Architecture
* **Text Encoder (CPU 4-Core)**: 4.0B LLM (`Qwen3-4B-Instruct-2507-Q2_K.gguf`) performs dense context embedding on CPU Big/Prime cores (`clipOnCpu: true`).
* **DiT Denoising Backbone (Vulkan GPU)**: 6.0B Diffusion Transformer (`z_image_turbo-Q2_K.gguf`) accelerated via Khronos Vulkan compute shaders with Tiled Flash Attention (`diffusionFa: true`).
* **Ultra-Fast VAE Decoder (CPU)**: 10MB Tiny AutoEncoder for FLUX.1 (`taef1.safetensors`) completes latent decoding rapidly without memory spikes (`vaeOnCpu: true`).
* **Layer Streaming (`streamLayers: true`)**: Breaks through mobile memory limits by streaming layers into Vulkan VRAM sequentially, maintaining a strict **1.0 GB VRAM footprint** (`maxVram: "vulkan0=1"`) and completely eliminating Android Low Memory Killer (LMK) aborts.

---

## 📸 Sovereign Physical Verification: Galaxy S21 DiT 8-Step Output

* **Verification Image**: [Galaxy S21 Z-Image Turbo 8-Step PNG Artifact](https://raw.githubusercontent.com/uno-km/termux-diffusion/main/docs/research/s21_z_image_turbo_8step.png)
* **Verification Prompt (Ground Truth)**:
  ```text
  "A cinematic photo of a neon cybernetic tiger walking in Seoul street at night"
  ```
* **Verified Input Parameter Engineering**:
  * `steps: 8` (Full numerical convergence ODE solver)
  * `cfgScale: 1.0` (Optimal guidance for distilled DiT architecture)
  * `sampler: "euler"` (1st-order Ordinary Differential Equation solver)
  * `device: "vulkan"` (Physical GPU acceleration)
  * `diffusionFa: true` (Tiled Flash Attention enabled)
  * `streamLayers: true` (Layer residency streaming over AXI bus)
  * `maxVram: "vulkan0=1"` (Strict 1.0 GB VRAM ceiling, Zero-LMK protection)
  * `clipOnCpu: true` (Offloads LLM prompt embedding to CPU Big/Prime cores)
  * `vaeOnCpu: true` (Prevents GPU VRAM allocation collisions during decoding)
  * `taesd: "auto"` (Ultra-fast 10MB FLUX.1 latent decoder)
* **Optical Realism**: Specular light scattering from neon signboards on wet Seoul asphalt road surfaces, razor-sharp cybernetic armor plates, and micro-texture whiskers cleanly isolated from background noise.
* **Runtime Stability**: 100% completion achieved with zero Out-of-Memory (LMK) aborts and zero thermal throttling termination.

### 🔬 Academic Research & Lab Report Reference
* **Full Technical Research Report**: [Galaxy S21 Z-Image Turbo Vulkan Research Report](https://github.com/uno-km/termux-diffusion/blob/main/docs/research/s21_z_image_turbo_vulkan_research_report.md)
* **Academic Research Paper**: [AMEVA Labs | Sovereign On-Device AI Research, Newsletter & Discussion](https://uno-km.vercel.app/labs/index.html?menu=research-papers&post=32)

---

## 💻 Node.js / TypeScript SDK Installation & Practical User Manual

### 1. Installation & Provisioning
```bash
pkg update && pkg install -y nodejs clang termux-api
npm install -g termux-diffusion
npx termux-diffusion install
```

### 2. TypeScript / Node.js API Practical Code Example

```typescript
import { generate, TermuxDiffusion } from "termux-diffusion";

async function runSynthesis(): Promise<void> {
  // 1. Official Z-Image Turbo 6.0B DiT Synthesis via Node.js API
  const ditResult = await generate({
    prompt: "A cinematic photo of a neon cybernetic tiger walking in Seoul street at night",
    preset: "z-image-turbo",
    steps: 8,
    cfgScale: 1.0,
    sampler: "euler",
    device: "vulkan",
    diffusionFa: true,
    streamLayers: true,
    maxVram: "vulkan0=1",
    clipOnCpu: true,
    vaeOnCpu: true,
    taesd: "auto",
    outputPath: "/sdcard/Pictures/TermuxDiffusion/cyber_tiger_dit.png"
  });
  console.log("6.0B DiT Output saved to Samsung Gallery:", ditResult.outputPath);

  // 2. Fast UNet Standard Inference (DreamShaper 8 LCM 6-Step)
  const lcmResult = await generate({
    prompt: "A cinematic photo of a neon cybernetic tiger walking in Seoul street at night",
    model: "anime",
    steps: 6,
    cfgScale: 1.5,
    sampler: "lcm",
    device: "vulkan",
    diffusionFa: true,
    vaeOnCpu: true,
    outputPath: "/sdcard/Pictures/TermuxDiffusion/cyber_tiger_lcm.png"
  });
  console.log("DreamShaper 8 LCM Output:", lcmResult.outputPath);
}

runSynthesis().catch(console.error);
```

---

## 🎛️ Node.js API Parameter Reference

| Option Property | Type | Default | Engineering Purpose |
| :--- | :---: | :---: | :--- |
| `prompt` | `string` | *Required* | Text conditioning prompt |
| `width`, `height` | `number` | `512` | Image dimensions (multiples of 64) |
| `steps` | `number` | `8` (DiT) / `6` (LCM) | Numerical solver sampling iterations |
| `cfgScale` | `number` | `1.0` (DiT) / `1.5` (LCM) | Classifier-Free Guidance scale weight |
| `sampler` | `string` | `"euler"` | Denoising ODE solver algorithm |
| `device` | `string` | `"vulkan"` | Accelerator device (`"vulkan"`, `"cpu"`) |
| `preset` | `string` | `"z-image-turbo"` | Verified configuration bundle |
| `streamLayers` | `boolean` | `true` (DiT) | Enables dynamic layer streaming over AXI bus |
| `maxVram` | `string` | `"vulkan0=1"` | GPU memory ceiling (1.0 GB) to avert OS LMK aborts |
| `diffusionFa` | `boolean` | `true` | Flash Attention $O(N)$ memory reduction |
| `clipOnCpu` | `boolean` | `true` | Keeps LLM text encoder on CPU cores |
| `vaeOnCpu` | `boolean` | `true` | Offloads VAE decode from GPU to host CPU |
| `taesd` | `string` | `"auto"` | Tiny AutoEncoder for ~1.2s latent decoding |
| `outputPath` | `string` | `undefined` | Path to save output PNG artifact |

---

## 🌐 Official Documentation & Ecosystem Links
- [Official Architecture & API Reference](https://uno-km.vercel.app/lib/diffusion/)
- [Advanced Parameters Handbook](https://uno-km.vercel.app/lib/diffusion/advanced-parameters.html)
- [GitHub Repository](https://github.com/uno-km/termux-diffusion)
- [AMEVA Open-Source Foundation Portal](https://uno-km.vercel.app/foundation/index.html)

---

## 📄 License
Licensed under the Apache-2.0 License. Copyright (c) 2026 Eunho Kim ([@uno-km](https://github.com/uno-km)).
