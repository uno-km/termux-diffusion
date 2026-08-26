# Galaxy S21 (Mali-G78) V11 Engineering Handover Document

## 1. Final Verified Status

```text
DEVICE_MODEL=SM-G991N
DEVICE_CODENAME=o1s
ANDROID_BUILD_FINGERPRINT=samsung/o1sksx/o1s:15/AP3A.240905.015.A2/G991NKSSCHZA9:user/release-keys
SSH_HOST_KEY_FINGERPRINT=SHA256:4tM3Jj/sP2iY9WJdD9UvR9Y4F5h4BwL9fM8bY+sX6/w
GPU_DEVICE_NAME=Mali-G78

S21_V0_V9_RAW_VULKAN=VERIFIED
S21_V10_GGML_MATMUL=VERIFIED
S21_V11_SDXS_VULKAN=VERIFIED
S21_V11_STRICT_ALL_TENSOR=PENDING_BACKEND_AUDIT

ROOT_CAUSE_CLASS=UNET_MUL_MAT_ALIGNED_PIPELINE_OUT_OF_BOUNDS_BUFFER_ACCESS
ROOT_CAUSE_ISOLATED=TRUE
FIRST_FAILED_NODE=1055
FIRST_FAILED_OPERATION=MUL_MAT
FIRST_FAILED_PIPELINE=matmul_f16_f16acc_aligned_l

PATCH_PATH=patches/v10-v11-mali-g78-vulkan.patch
PATCH_SHA256=8cddc5b4f753eadb4180ad21f724876113deb8c00c82abe19d7efafdff82f21b

PACKAGE_STATUS=CANDIDATE_STAGED
PACKAGE_FILENAME=termux-diffusion-vulkan-prebuilt-v1.3.1-android-arm64-mali-compat-v2.tar.gz
PACKAGE_SHA256=65e4e305241b22385313e386afbcd12722061041280d00a44dfdc3ff23aa17b8
ACTIVE_CPU_UNCHANGED=TRUE
AUTOMATIC_ROLLBACK_VERIFIED=TRUE
```

---

## 2. Incontrovertible Evidence & Ground Truth

1. **Stage V10 GGML MatMul (`track_b_v10_matmul`)**:
   - SHA256: `c60280d65e75e8c089325979973386754f6eff0b831d3d1eae91bb488f45e110`
   - Output: `PASS_V10_MALI_GGML_MATMUL_SUCCESSFUL` (0 Mismatches, Max Error `9.39e-05`, Exit Code 0)

2. **Stage V11 SDXS 256x256 1-step Inference**:
   - Executable SHA256: `1f10b3c91b34764cbeb79bc2a8360c8e2f1580cbd41d7160b028a0b512ced6db`
   - Output Image: `s21_v11_sdxs_fixed.png` (82,829 bytes, SHA256: `27c3929325e876d8aab5219d3b286368916c80df45668f303c5695eebc4b1fde`)
   - Latency: Text Encoder `7.79s`, UNet Sampling `9.85s`, VAE Decode `1.04s`, Total `18.69s`. Exit Code 0.

3. **Staging Environment Verification**:
   - Tarball: `termux-diffusion-vulkan-prebuilt-v1.3.1-android-arm64-mali-compat-v2.tar.gz` (`65e4e305...`)
   - V10 Self-Test: PASS
   - V11 Smoke-Test: PASS
   - Active CPU binary: `5a98fec4...` (UNCHANGED)

---

## 3. Resumption Instructions for Next Agent

1. **Pull and inspect**:
   ```bash
   git clone https://github.com/uno-km/termux-diffusion.git
   cd termux-diffusion
   git switch feature/gpu
   git pull --ff-only origin feature/gpu
   cat docs/handover/GALAXY_S21_MALI_G78_V11_HANDOVER.md
   ```
2. **Next Milestone**:
   - Package signing with release keys.
   - Formal deployment into production update channel.
