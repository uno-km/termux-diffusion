# Release Notes - termux-diffusion v1.8.0

**Release Tag**: `v1.8.0`  
**Distribution Channels**: PyPI (`termux-diffusion`), NPM (`termux-diffusion`), GitHub Releases  
**Target Platform**: Android Termux (ARM64 / aarch64 Bionic libc & Vulkan 1.1+)  
**License**: Apache-2.0  
**Research Attribution**: AMEVA Foundation (uno-km Ecosystem) & AMEVA Edge Systems Lab (AESL)  

---

## 🌟 Major Highlights & Flagship Capabilities

### 1. Official Z-Image Turbo (6.0B DiT) Support
`termux-diffusion v1.8.0` officially introduces production-grade support for **Z-Image Turbo**, a state-of-the-art **6.0 Billion Parameter Diffusion Transformer (DiT)** architecture running 100% locally on Android Termux.
- **Tri-Engine Asymmetric Pipeline**:
  1. **Text Encoder (CPU)**: 4.0B Large Language Model (`Qwen3-4B-Instruct-2507-Q2_K.gguf`) executed across 4 high-efficiency/prime CPU cores (`clip=cpu`).
  2. **DiT Backbone (Vulkan GPU)**: 6.0B Diffusion Transformer (`z_image_turbo-Q2_K.gguf`) accelerated via host Khronos Vulkan compute shaders (`diffusion=vulkan0`).
  3. **Super-Fast VAE Decoder (CPU)**: 10MB Tiny AutoEncoder for FLUX.1 (`taef1.safetensors`, `vae=cpu`) completing latent decoding rapidly with zero VRAM spikes.
- **Dynamic Layer Streaming (`--stream-layers`)**: Enables 2.41GB DiT models to operate strictly within a **1.0 GB VRAM limit** (`--max-vram vulkan0=1`), eliminating Android Low Memory Killer (LMK) aborts and guaranteeing Zero-OOM stability.
- **Flash Attention & Memory-Mapped IO**: Integrated Flash Attention (`--diffusion-fa`) and zero-copy mmap (`--mmap`) minimize bandwidth saturation on mobile LPDDR5 buses.

---

## 📱 Hardware Verification Case Study: Samsung Galaxy S21 5G

In-depth verification was completed on physical mobile silicon without host root privileges or cloud offloading:

* **Target Device**: Samsung Galaxy S21 5G (SM-G991N)
* **Application Processor (AP)**: Samsung Exynos 2100 (5nm EUV, Octa-Core: 1x Cortex-X1 + 3x Cortex-A78 + 4x Cortex-A55)
* **Graphics Processor (GPU)**: ARM Mali-G78 MP14 (14-Core Execution Engine, Vulkan 1.1)
* **System Memory**: 8 GB LPDDR5 RAM (Host VRAM Allocation: Fixed 1.0 GB)
* **Operating System**: Android 14 / One UI 6.1 (Linux Kernel 5.4 aarch64, Termux Bionic libc)

### Canonical Verification Configurations

#### ① Z-Image Turbo (6.0B DiT 8-Step)
```bash
sd-cli-vulkan \
  -p "A cinematic photo of a neon cybernetic tiger walking in Seoul street at night" \
  -W 512 -H 512 \
  -t 4 \
  --steps 8 \
  --cfg-scale 1.0 \
  -o /sdcard/Pictures/TermuxDiffusion/s21_z_image_turbo_8step.png \
  --diffusion-model ~/.cache/termux-diffusion/models/z_image_turbo-Q2_K.gguf \
  --llm ~/.cache/termux-diffusion/models/Qwen3-4B-Instruct-2507-Q2_K.gguf \
  --taesd ~/.cache/termux-diffusion/models/taef1.safetensors \
  --clip-on-cpu \
  --vae-on-cpu \
  --vae-format flux \
  --mmap \
  --diffusion-fa \
  --backend clip=cpu,diffusion=vulkan0,vae=cpu \
  --max-vram vulkan0=1 \
  --stream-layers \
  --params-backend diffusion=cpu \
  --sampling-method euler \
  --vae-tiling
```

#### ② DreamShaper 8 (LCM 6-Step Fast Inference)
```bash
sd-cli-vulkan \
  -p "A cinematic photo of a neon cybernetic tiger walking in Seoul street at night" \
  -W 512 -H 512 \
  -t 4 \
  --steps 6 \
  --cfg-scale 1.5 \
  --sampling-method lcm \
  -m ~/.cache/termux-diffusion/models/anime.gguf \
  --seed 42 \
  --backend clip=vulkan0,diffusion=vulkan0,vae=cpu \
  --vae-on-cpu \
  --vae-tiling \
  --diffusion-fa \
  --mmap \
  -o /sdcard/Pictures/TermuxDiffusion/s21_anime_tiger_6step.png
```

### Verification Characteristics & Visual Fidelity
* **Specular PBR Reflection**: Realistic reflections of cyan and pink neon lighting on rain-slicked asphalt pavement.
* **Geometric Micro-Textures**: Precision edge delineation across cybernetic composite armor plates.
* **Zero Artifacts**: Whiskers and organic fur structures fully separated and preserved.
* **Memory Integrity**: Total VmRSS remained strictly stable within device threshold; 100% convergence with 0 crash events.

### 🔬 Academic Research & Whitepaper Reference
The complete experimental findings, memory architecture trade-offs, and micro-kernel benchmark analysis are documented in:
* **AMEVA Labs Research Portal**: [https://uno-km.vercel.app/labs/index.html?menu=research-papers&post=32](https://uno-km.vercel.app/labs/index.html?menu=research-papers&post=32)
* **Official Research Whitepaper**: [`docs/research/s21_z_image_turbo_vulkan_research_report.md`](docs/research/s21_z_image_turbo_vulkan_research_report.md)

---

## 🛠️ Advanced Parameter Usage & Documentation Rewrite Plan

With the introduction of Tri-Engine DiT acceleration and hybrid CPU/Vulkan scheduling, `termux-diffusion` has established a comprehensive roadmap for complete parameter documentation restructuring:

### 1. Core Parameter Taxonomy
* **`--diffusion-model <path>`**: Explicit path to DiT / UNet model weights (`.gguf`).
* **`--llm <path>`**: Explicit path to text encoder weights (Qwen3 / T5 / CLIP).
* **`--taesd <path>`**: Lightweight Tiny AutoEncoder checkpoint (`taef1.safetensors`).
* **`--stream-layers`**: Sequentially stream model layers into Vulkan VRAM over AXI bus.
* **`--max-vram <backend=size>`**: Sets hard memory cap on GPU allocation (e.g. `vulkan0=1` for 1GB limit).
* **`--params-backend <module=target>`**: Binds parameter weight storage (e.g. `diffusion=cpu`).
* **`--diffusion-fa`**: Tiled Flash Attention reducing memory complexity from $O(N^2)$ to $O(N)$.
* **`--vae-on-cpu` & `--vae-tiling`**: Offloads VAE decode to CPU cores and applies spatial tiling to eliminate 1.2GB peak spikes.

### 2. Documentation Rewrite Roadmap
* **Phase 1 (v1.8.1)**: Launch interactive parameter calculator on [uno-km.vercel.app/lib/diffusion/](https://uno-km.vercel.app/lib/diffusion/) allowing users to input available RAM/VRAM and automatically receive optimal CLI flags.
* **Phase 2 (v1.8.2)**: Release hardware-specific profiles for Qualcomm Adreno (650, 730, 830) and ARM Mali (G68, G78, Immortalis).
* **Phase 3 (v1.9.0)**: Fully unified Python SDK and Node.js SDK schema validation with built-in runtime sanity assertions.

---

## 📦 Package Synchronization
* `pyproject.toml`, `setup.py`, `package.json`: Version bumped to `1.8.0`.
* `termux_diffusion/__init__.py`: Exported Z-Image Turbo constants and Tri-Engine pipeline bindings.
