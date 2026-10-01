# Release Notes - termux-diffusion v1.8.0

**Release Tag**: `v1.8.0`  
**Distribution Channels**: PyPI (`termux-diffusion`), NPM (`termux-diffusion`), GitHub Releases  
**Target Platform**: Android Termux (ARM64 / aarch64 Bionic libc & Khronos Vulkan 1.1+)  
**License**: Apache-2.0  

---

## 🚀 Major Highlights & Breakthroughs

### 1. Official 6.0B DiT (Z-Image Turbo) Sovereign Mobile Execution
`termux-diffusion v1.8.0` introduces native, on-device support for **Z-Image Turbo**, making it possible to execute modern **6.0 Billion Parameter Diffusion Transformers (DiT)** natively on commercial Android hardware (verified on Samsung Galaxy S21 5G / ARM Mali-G78 MP14 GPU) without cloud dependencies.

* **Tri-Engine Asymmetric Pipeline**:
  * **Text Encoder (CPU 4-Core)**: 4.0B LLM (`Qwen3-4B-Instruct-2507-Q2_K.gguf`) performs dense context vectorization on CPU Big/Prime cores (`clip=cpu`).
  * **DiT Denoising Backbone (Vulkan GPU)**: 6.0B Diffusion Transformer (`z_image_turbo-Q2_K.gguf`) accelerated via Khronos Vulkan compute shaders (`diffusion=vulkan0`).
  * **Ultra-Fast VAE Decoder (CPU)**: 10MB Tiny AutoEncoder for FLUX.1 (`taef1.safetensors`) completes latent decoding rapidly without memory spikes (`vae=cpu`).
* **Dynamic Layer Streaming (`--stream-layers`)**: Breaks through mobile memory limits by streaming layers into Vulkan VRAM sequentially, maintaining a strict **1.0 GB VRAM footprint** (`--max-vram vulkan0=1`) and completely eliminating Android Low Memory Killer (LMK) aborts.
* **Tiled Flash Attention (`--diffusion-fa`)**: Eliminates $O(N^2)$ memory explosion during self-attention, enabling high-resolution DiT synthesis on mobile LPDDR5 RAM.
* **Prompt Embedding Caching (`Prompt Cache`)**: Automatically caches pre-computed text embeddings to eliminate redundant LLM tokenization on recurring prompt themes.
* **Structured Progress Monitoring (`--progress`, `--json-progress`)**: Real-time progress tracking with speed, step metrics, and IPC-friendly NDJSON streaming.

---

## 📸 Sovereign Physical Verification: Galaxy S21 DiT 8-Step Output

* **Verification Image**: [Galaxy S21 Z-Image Turbo 8-Step PNG Artifact](https://raw.githubusercontent.com/uno-km/termux-diffusion/main/docs/research/s21_z_image_turbo_8step.png)
* **Verification Prompt (Ground Truth)**:
  ```text
  "A cinematic photo of a neon cybernetic tiger walking in Seoul street at night"
  ```
* **Verified Input Parameters**:
  * `--steps 8` (Full numerical convergence ODE solver)
  * `--cfg-scale 1.0` (Optimal guidance for distilled DiT architecture)
  * `--sampling-method euler` (1st-order Ordinary Differential Equation solver)
  * `--backend clip=cpu,diffusion=vulkan0,vae=cpu` (Tri-Engine asymmetric offloading)
  * `--diffusion-fa` (Tiled Flash Attention enabled)
  * `--stream-layers` (Layer residency streaming over AXI bus)
  * `--max-vram vulkan0=1` (Strict 1.0 GB VRAM ceiling, Zero-LMK protection)
  * `--taesd taef1.safetensors` (Ultra-fast 10MB FLUX.1 latent decoder)
  * `--vae-tiling` (Prevents memory spikes during latent decoding)
* **Optical Realism**: Specular light scattering from neon signboards on wet Seoul asphalt road surfaces, razor-sharp cybernetic armor plates, and micro-texture whiskers cleanly isolated from background noise.
* **Runtime Stability**: 100% completion achieved with zero Out-of-Memory (LMK) aborts and zero thermal throttling termination.

### 🔬 Academic Research & Lab Report Reference
* **Full Technical Research Report**: [Galaxy S21 Z-Image Turbo Vulkan Research Report](https://github.com/uno-km/termux-diffusion/blob/main/docs/research/s21_z_image_turbo_vulkan_research_report.md)
* **Academic Research Paper**: [AMEVA Labs | Sovereign On-Device AI Research, Newsletter & Discussion](https://uno-km.vercel.app/labs/index.html?menu=research-papers&post=33)

---

## 💻 3-Channel Practical User Manual

### 1. Terminal CLI
```bash
termux-diffusion generate "A cinematic photo of a neon cybernetic tiger walking in Seoul street at night" \
  --preset z-image-turbo \
  --device vulkan \
  --steps 8 \
  --cfg 1.0 \
  --sampler euler \
  --diffusion-fa \
  --stream-layers \
  --max-vram vulkan0=1 \
  --clip-on-cpu \
  --vae-on-cpu \
  --taesd auto \
  -o /sdcard/Pictures/TermuxDiffusion/cyber_tiger_dit.png
```

### 2. Python SDK (PyPI)
```python
import termux_diffusion as td

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
```

### 3. Node.js / TypeScript SDK (NPM)
```typescript
import { generate } from "termux-diffusion";

async function main(): Promise<void> {
  const result = await generate({
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
  console.log("6.0B DiT Output saved to Samsung Gallery:", result.outputPath);
}

main().catch(console.error);
```

---

## 📦 Native Release Assets & Cryptographic Manifest

| Release Asset | Size (Bytes) | SHA-256 Checksum |
| :--- | :--- | :--- |
| `sd-cli-cpu-android-arm64.tar.gz` | `23,274,929` | `40efc24a5be9a8fba1e6e94e23845483726d7386aca7ed98d787ae1534fbeea3` |
| `libomp-android-arm64.so` | `1,205,616` | `c0f7797b5f137eb1ee442436d318e8a6fc576a8d6263ae7dbf4d8a0ebc85775f` |
| `termux_diffusion-1.8.0-py3-none-any.whl` | `75,361` | *Validated* |
| `termux_diffusion-1.8.0.tar.gz` | `83,389` | *Validated* |
| `s21_z_image_turbo_8step.png` | `627,838` | *Research Asset* |
| `s21_anime_tiger_6step.png` | `494,959` | *Research Asset* |
| `s21_sdxs_tiger_2step.png` | `592,606` | *Research Asset* |
