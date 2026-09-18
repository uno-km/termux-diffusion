# Termux-Diffusion (Python)

[![PyPI](https://img.shields.io/pypi/v/termux-diffusion.svg?style=flat-square&color=0369a1)](https://pypi.org/project/termux-diffusion/)
[![Python](https://img.shields.io/pypi/pyversions/termux-diffusion.svg?style=flat-square)](https://pypi.org/project/termux-diffusion/)
[![License](https://img.shields.io/badge/License-Apache_2.0-004499.svg?style=flat-square)](https://github.com/uno-km/termux-diffusion)

> **Pure CPU Native On-Device Stable Diffusion Runtime for Android Termux & Samsung Galaxy.**  
> *Zero PRoot. Zero Virtualization. 100% Native ARM64 Bionic libc & NEON SIMD Vector Acceleration.*

---

## Installation & Native Engine Provisioning

```bash
# 1. Install Python package from PyPI
pip install termux-diffusion

# 2. Provision prebuilt Pure CPU native engine & OpenMP runtime
termux-diffusion install
```

---

## Quickstart (Python SDK)

```python
import termux_diffusion as td

# Generate image using pure CPU with LCM anime preset
image_path = td.generate(
    prompt="cute polar bear in snow, high quality illustration",
    model="anime",
    steps=6,
    device="cpu",
    output_path="polar_bear.png"
)
print(f"Generated and saved to Android Gallery: {image_path}")
```

## CLI Usage

```bash
termux-diffusion generate "cute dolphin, vibrant ocean" -m anime --cpu -o dolphin.png
```

---

## Key Capabilities

* **ARMv8.2-A DotProd & FP16 NEON SIMD**: Native matrix acceleration compiled directly against Android Bionic libc.
* **Built-in VAE Tiling**: Reduces peak RAM consumption by ~70% during latent-to-pixel decoding to prevent Out-Of-Memory (OOM) aborts.
* **Android MediaStore Auto-Indexing**: Automatically synchronizes generated images into `Pictures/TermuxDiffusion` and the native Samsung Gallery.
* **Fail-Fast Protection**: Blocks unintended on-device compilation cycles to protect mobile devices from severe thermal throttling.

---

## Hardware Benchmarks (Physical Android Devices)

| Device | AP / Architecture | Wall Time | Sampling Time | Peak RAM |
| :--- | :--- | :--- | :--- | :--- |
| **Galaxy S25** | Snapdragon 8 Elite | **15m 52s (951s)** | 11m 37s (697s) | ~2.5 GB |
| **Galaxy S21** | Exynos 2100 | **53m 45s (3221s)** | 7m 47s (467s) | ~2.4 GB |

---

## Documentation & Repository
- [Official Architecture & API Reference](https://uno-km.vercel.app/lib/diffusion/)
- [GitHub Repository](https://github.com/uno-km/termux-diffusion)

## License
Apache-2.0 License. Copyright (c) 2026 Eunho Kim (@uno-km).

