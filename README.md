# Termux-Diffusion

[![PyPI](https://img.shields.io/pypi/v/termux-diffusion.svg?style=flat-square&color=0369a1)](https://pypi.org/project/termux-diffusion/)
[![Python](https://img.shields.io/pypi/pyversions/termux-diffusion.svg?style=flat-square)](https://pypi.org/project/termux-diffusion/)
[![npm](https://img.shields.io/npm/v/termux-diffusion.svg?style=flat-square&color=b91c1c)](https://www.npmjs.com/package/termux-diffusion)
[![npm downloads](https://img.shields.io/npm/dm/termux-diffusion.svg?style=flat-square&color=b91c1c)](https://www.npmjs.com/package/termux-diffusion)
[![License](https://img.shields.io/badge/License-Apache_2.0-004499.svg?style=flat-square)](https://github.com/uno-km/termux-diffusion)

> **디바이스 리소스를 활용한 Android Termux 네이티브 온디바이스 Stable Diffusion 런타임**  
> *Native On-Device Stable Diffusion Runtime Utilizing Device Resources for Android Termux*

---

## 📌 Architecture & Overview

안드로이드 순정 Bionic libc 상에서 디바이스 리소스를 활용하여 ARMv8.2-A DotProd/FP16 SIMD 벡터 연산(Cortex-A78 x4: 61초)을 통해 이미지를 생성하고 삼성 갤러리에 자동 반영합니다.

Executes quantized Stable Diffusion models utilizing device resources with ARMv8.2-A DotProd/FP16 SIMD vector execution (Cortex-A78 x4 61s) and direct Samsung Gallery indexing.

---

## 🚀 Installation & Quickstart

### Python (PyPI)
```bash
pip install termux-diffusion
```
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

### Node.js / TypeScript (npm)
```bash
npm install termux-diffusion
```
```typescript
import { generate } from "termux-diffusion";

const result = await generate({
  prompt: "Cyberpunk Seoul city at night, neon lights, 8k",
  model: "sd-turbo",
  steps: 4
});
console.log("Image created:", result.outputPath);

```

---

## 📖 Official Documentation & Benchmarks
- [Official Architecture & API Reference](https://uno-km.vercel.app/lib/diffusion/)
- [Ecosystem Metrics & Registry Stats](https://uno-km.vercel.app/foundation/metrics)
- [AMEVA Open-Source Foundation Portal](https://uno-km.vercel.app/foundation/index.html)

---

## 📄 License
Licensed under the Apache-2.0 License. Copyright (c) 2026 Eunho Kim ([@uno-km](https://github.com/uno-km)).
