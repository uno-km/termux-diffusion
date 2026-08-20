# Comprehensive Guide to Advanced Parameters in Termux-Diffusion

`termux-diffusion` exposes the full suite of high-precision diffusion controls powered by the native `sd-cli` (`stable-diffusion.cpp`) engine. This handbook details every advanced parameter, supported values, boundary clamping rules, and production code examples for **Python SDK**, **Node.js SDK**, and **Terminal CLI**.

---

## 📑 Quick Parameter Matrix

| Parameter (Python / JS) | CLI Flag | Type | Valid Choices / Range | Default | Purpose |
| :--- | :--- | :---: | :--- | :---: | :--- |
| `sampling_method` / `samplingMethod` | `--sampler` | String | `euler`, `euler_a`, `heun`, `dpm2`, `dpm++2s_a`, `dpm++2m`, `dpm++2mv2`, `ipndm`, `lcm` | `euler_a` | Denoising sampler algorithm |
| `schedule` | `--schedule` | String | `default`, `discrete`, `karras`, `exponential`, `ays`, `gits` | `default` | Noise sigma schedule |
| `vae_tiling` / `vaeTiling` | `--vae-tiling` | Boolean | `True` / `False` | `False` | Reduces peak VRAM/RAM by ~70% during VAE decode |
| `init_img` / `initImg` | `-i`, `--init-img` | Path | Valid image filepath (`.png`, `.jpg`) | `None` | Source image for Image-to-Image (Img2Img) |
| `strength` | `--strength` | Float | `0.0` to `1.0` | `0.75` | Img2Img denoising strength |
| `lora_dir` / `loraDir` | `--lora-dir` | Path | Valid directory containing `.gguf`/`.safetensors` | `None` | Directory containing LoRA adapters |
| `clip_skip` / `clipSkip` | `--clip-skip` | Integer | `1` or `2` | `None` | Skips final CLIP text encoder layers |
| `control_net` / `controlNet` | `--control-net` | Path | Valid `.gguf` ControlNet model file | `None` | Spatial conditioning model (pose, edges) |
| `control_image` / `controlImage` | `--control-image` | Path | Valid image filepath | `None` | Guide image for ControlNet |
| `control_strength` / `controlStrength` | `--control-strength` | Float | `0.0` to `2.0` | `0.9` | Influence weight of ControlNet conditioning |
| `taesd` | `--taesd` | Path | Valid TAESD `.gguf` file | `None` | Ultra-lightweight Tiny AutoEncoder (0.1s decode) |

---

## 1. 🎛️ Samplers (`sampling_method`) & Schedulers (`schedule`)

### Supported Samplers (`sampling_method`):
* **`"euler_a"` (Default):** Euler Ancestral. Fast, creative, highly versatile across general prompts.
* **`"euler"`:** Standard deterministic Euler. Produces smooth, stable compositions.
* **`"dpm++2m"` (Recommended for Photorealism):** 2nd-order multi-step DPM solver. Excellent facial details and micro-textures at 10-15 steps.
* **`"dpm++2s_a"`:** 2nd-order single-step ancestral solver. Higher artistic variance.
* **`"heun"`:** High-accuracy 2nd-order ODE solver. Slower per step but high mathematical fidelity.
* **`"lcm"` (Latent Consistency Model):** Extreme acceleration sampler for LCM models (produces final images in 4 to 6 steps).
* **`"dpm2"` / `"dpm++2mv2"` / `"ipndm"`:** Specialized solvers for experimental workflows.

### Supported Schedulers (`schedule`):
* **`"default"` (Default):** Native linear sigma schedule.
* **`"karras"` (Recommended):** Non-linear variance schedule matching human perceptual clarity. Drastically improves contrast when paired with `dpm++2m`.
* **`"exponential"`:** Exponential decay schedule for smoother background gradients.
* **`"ays"` (Align Your Steps):** 10-step optimized schedule designed by NVIDIA researchers for rapid convergence.
* **`"discrete"` / `"gits"`:** Alternative discrete quantization schedules.

### Code Examples:
```python
# Python SDK
from termux_diffusion import generate

result = generate(
    "hyperrealistic portrait of a cyborg samurai, neon lighting, 8k",
    model="realistic",
    sampling_method="dpm++2m",
    schedule="karras",
    steps=12,
    cfg_scale=4.0
)
```

```javascript
// Node.js SDK
const { generate } = require('termux-diffusion');

const result = await generate({
  prompt: 'hyperrealistic portrait of a cyborg samurai, neon lighting, 8k',
  model: 'realistic',
  samplingMethod: 'dpm++2m',
  schedule: 'karras',
  steps: 12,
  cfgScale: 4.0
});
```

```bash
# Terminal CLI
termux-diffusion generate "hyperrealistic portrait of a cyborg samurai" -m realistic --sampler dpm++2m --schedule karras -s 12
```

---

## 2. 🧩 VAE Tiling (`vae_tiling`) - Mobile OOM Prevention

During the final phase of image generation, the Latent tensor (64x64) is decoded into a 512x512 RGB pixel image. On smartphones with limited memory or when generating high resolutions (768x768 or 1024x1024), standard monolithic VAE decoding causes a temporary **1.2GB memory spike**.

Setting `vae_tiling=True` splits the image into smaller 64x64 spatial tiles and stitches them together, **reducing peak memory consumption by 70%** without visual degradation.

```python
# Python SDK
generate("futuristic megacity landscape", width=768, height=768, vae_tiling=True)
```

```bash
# CLI
termux-diffusion generate "futuristic megacity landscape" -W 768 -H 768 --vae-tiling
```

---

## 3. 🖼️ Image-to-Image (`init_img` & `strength`)

Transform existing photos, sketches, or previous AI renders into new artwork.

* **`init_img`:** Filepath to input source image.
* **`strength` (`0.0` to `1.0`):**
  * `0.2 - 0.4`: Subtle touch-up / style enhancement (preserves original composition).
  * `0.5 - 0.75` (Default: `0.75`): Balanced reimagination.
  * `0.85 - 1.0`: Dramatic transformation.

```python
# Python SDK
generate(
    "convert sketch into an oil painting of a castle on a hill",
    init_img="/sdcard/Pictures/my_sketch.png",
    strength=0.70,
    steps=15
)
```

```bash
# CLI
termux-diffusion generate "convert sketch into oil painting" -i /sdcard/Pictures/my_sketch.png --strength 0.70
```

---

## 4. 🎨 LoRA Adapters (`lora_dir`)

Inject Low-Rank Adaptation (LoRA) weights to specialize character appearances, costumes, or artistic styles without altering base model files.

* Place `.gguf` or `.safetensors` LoRA files into a dedicated directory (e.g. `~/loras/`).
* Pass `lora_dir="~/loras"`. You can reference specific LoRAs in your prompt using standard syntax `<lora:filename:0.8>`.

```python
# Python SDK
generate(
    "cyberpunk detective in trenchcoat <lora:cyber_armor:0.8>",
    model="realistic",
    lora_dir="/data/data/com.termux/files/home/loras"
)
```

```bash
# CLI
termux-diffusion generate "cyberpunk detective <lora:cyber_armor:0.8>" --lora-dir ~/loras
```

---

## 5. ✂️ CLIP Skip (`clip_skip`)

Anime, stylized illustration, and NovelAI-derived models are trained to interpret prompt semantics from the penultimate (second to last) text encoder layer.

* **`clip_skip=1`:** Standard SD 1.5 photorealism (default).
* **`clip_skip=2`:** Standard anime/manga aesthetic (smoother skin tones, vibrant anime rendering).

```python
# Python SDK
generate(
    "1girl, magical girl, starry sky, anime masterpiece",
    model="anime",
    clip_skip=2,
    steps=8
)
```

```bash
# CLI
termux-diffusion generate "1girl, anime masterpiece" -m anime --clip-skip 2
```

---

## 6. 🎭 ControlNet (`control_net`, `control_image`, `control_strength`)

Lock in exact character poses (OpenPose) or structural line art (Canny Edge) during image synthesis.

```python
# Python SDK
generate(
    "warrior posing heroically on battlefield",
    control_net="/sdcard/AI_Models/controlnet_openpose.gguf",
    control_image="/sdcard/Pictures/pose_guide.png",
    control_strength=0.9
)
```

```bash
# CLI
termux-diffusion generate "warrior posing" --control-net ~/models/cnet.gguf --control-image ~/pose.png --control-strength 0.9
```

---

## 7. ⚡ Tiny AutoEncoder (`taesd`)

Replace the standard 330MB VAE with a 5MB distilled TAESD AutoEncoder. This reduces the final decoding stage from 4.5 seconds down to **0.12 seconds** on mobile ARM64 CPUs.

```python
# Python SDK
generate("speedy sports car", taesd="~/models/taesd.gguf")
```

---

## 🛡️ Error Handling, Boundary Clamping & Safety Rules

`termux-diffusion` guarantees zero silent failures while actively preventing invalid configurations from crashing the underlying Bionic C++ engine:

| Error / Edge Case | Behavior & Safety Action |
| :--- | :--- |
| **Missing `init_img` / `control_net` File** | 🔴 **Critical Halt (`FileNotFoundError`):** Aborts immediately to prevent unintended Txt2Img generation with missing inputs. |
| **Out-of-Bounds `strength` (`< 0.0` or `> 1.0`)** | 🟡 **Auto-Clamping & Warning:** Automatically clamped to `0.0` or `1.0` with a descriptive warning log, allowing synthesis to proceed. |
| **Invalid `clip_skip` (`< 1` or `> 2`)** | 🟡 **Auto-Clamping & Warning:** Automatically clamped to valid bounds (`1` or `2`). |
| **Typo in `sampling_method` or `schedule`** | 🟡 **Graceful Default Fallback:** Warns the user and falls back to engine default (`euler_a` / `default`) without failing the batch. |
| **Unset / `None` / Empty Arguments** | 🟢 **Zero Overhead:** Parameter flags are completely omitted from the C++ command line, preserving 100% native baseline performance. |
