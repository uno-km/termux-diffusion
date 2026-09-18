# termux-diffusion (Node.js & TypeScript)

[![npm](https://img.shields.io/npm/v/termux-diffusion.svg?style=flat-square&color=b91c1c)](https://www.npmjs.com/package/termux-diffusion)
[![npm downloads](https://img.shields.io/npm/dm/termux-diffusion.svg?style=flat-square&color=b91c1c)](https://www.npmjs.com/package/termux-diffusion)
[![License](https://img.shields.io/badge/License-Apache_2.0-004499.svg?style=flat-square)](https://github.com/uno-km/termux-diffusion)

> **Pure CPU Native On-Device Stable Diffusion Runtime for Android Termux & Samsung Galaxy.**  
> *Zero PRoot. Zero Virtualization. 100% Native ARM64 Bionic libc & NEON SIMD Vector Acceleration.*

---

## Installation & One-Touch Native Provisioning

```bash
# 1. Install Node.js package from npm
npm install termux-diffusion

# 2. Provision prebuilt Pure CPU native engine & OpenMP runtime
npx termux-diffusion install
```

---

## Quickstart (Node.js / TypeScript)

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

  console.log("Image synthesized successfully:", result.outputPath);
}

main().catch(console.error);
```

## CLI Usage

```bash
# Generate image using pure CPU with LCM anime preset
npx termux-diffusion generate "cute polar bear in snow" -m anime --cpu -o polar_bear.png
```

---

## Key Capabilities

* **Zero-PRoot Native ARM64 Bionic**: Executes directly on host Android Termux with zero virtual machine indirection.
* **Fast-Track Native Extractor**: Automatically deploys the prebuilt Bionic ARM64 binary (`sd-cli-cpu`) and companion OpenMP runtime (`libomp.so`) in seconds.
* **Built-in VAE Tiling**: Reduces peak RAM consumption by ~70% during latent decoding, preventing mobile Out-Of-Memory (OOM) aborts.
* **Android MediaStore Auto-Indexing**: Automatically synchronizes output images to `Pictures/TermuxDiffusion` for real-time visibility in the Samsung Gallery app.
* **Fail-Fast Thermal Protection**: On-device C++ compilation is blocked by default without explicit opt-in (`TERMUX_DIFFUSION_ALLOW_SOURCE_BUILD=1`), protecting mobile hardware against battery drain and thermal throttling.

---

## Hardware Benchmarks (Physical Android Devices)

| Device | AP / Architecture | Total Wall Time | Sampling Time | Peak RAM |
| :--- | :--- | :--- | :--- | :--- |
| **Galaxy S25** | Snapdragon 8 Elite | **15m 52s (951s)** | 11m 37s (697s) | ~2.5 GB |
| **Galaxy S21** | Exynos 2100 | **53m 45s (3221s)** | 7m 47s (467s) | ~2.4 GB |

---

## Documentation & Repository
- [Official Architecture & API Reference](https://uno-km.vercel.app/lib/diffusion/)
- [GitHub Repository](https://github.com/uno-km/termux-diffusion)

## License
Apache-2.0 License. Copyright (c) 2026 Eunho Kim (@uno-km).
