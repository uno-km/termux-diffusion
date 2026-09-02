# termux-diffusion

> **Hardware-Accelerated On-Device Image Generation & Stable Diffusion Runtime for Android Termux**  
> *Non-Root Native Vulkan GPU Execution · ARM64 DotProd SIMD · Android Bionic ICD Driver Priority · Resilient Memory Pipeline*

---

## ⚡ 5-Minute Quickstart

### Python Installation

`ash
# In Android Termux:
pkg update && pkg install -y python python-numpy git
pip install termux-diffusion
`

### Python SDK Usage

`python
from termux_diffusion import DiffusionPipeline

pipeline = DiffusionPipeline.from_pretrained("sd-turbo-arm64")
image = pipeline.generate("cyberpunk street cat, 4k", steps=4)
image.save("output.png")
`

---

## 📚 Official Documentation

- **Official Web Documentation**: [https://uno-km.vercel.app/lib/diffusion/](https://uno-km.vercel.app/lib/diffusion/)
- **GitHub Repository**: [https://github.com/uno-km/termux-diffusion](https://github.com/uno-km/termux-diffusion)
- **License**: Apache-2.0