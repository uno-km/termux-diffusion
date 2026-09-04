# Termux-Diffusion (Python)

[![PyPI](https://img.shields.io/pypi/v/termux-diffusion.svg?style=flat-square&color=0369a1)](https://pypi.org/project/termux-diffusion/)
[![Python](https://img.shields.io/pypi/pyversions/termux-diffusion.svg?style=flat-square)](https://pypi.org/project/termux-diffusion/)
[![License](https://img.shields.io/badge/License-Apache_2.0-004499.svg?style=flat-square)](https://github.com/uno-km/termux-diffusion)

> **디바이스 리소스를 활용한 Android Termux 네이티브 온디바이스 Stable Diffusion 런타임**  
> *Native On-Device Stable Diffusion Runtime Utilizing Device Resources for Android Termux*

## Installation

```bash
pip install termux-diffusion
```

## Quickstart

```python
import termux_diffusion as td

# 1. Generate image on Android hardware
image_path = td.generate(
    prompt="Cyberpunk Seoul city at night, neon lights, 8k",
    model="sd-turbo",
    steps=4
)
print(f"Generated and saved to Gallery: {image_path}")

```

## Description
Executes quantized Stable Diffusion models utilizing device resources with ARMv8.2-A DotProd/FP16 SIMD vector execution (Cortex-A78 x4 61s) and direct Samsung Gallery indexing.

## Documentation
- [Official Documentation & API Reference](https://uno-km.vercel.app/lib/diffusion/)
- [GitHub Repository](https://github.com/uno-km/termux-diffusion)

## License
Apache-2.0 License. Copyright (c) 2026 Eunho Kim (@uno-km).
