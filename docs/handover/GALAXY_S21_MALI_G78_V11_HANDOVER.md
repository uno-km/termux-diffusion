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
S21_V11_TEXT_ENCODER=VERIFIED (159.13MB VRAM, 7.64s compute)
S21_V11_DIFFUSION_SAMPLING=BLOCKED
S21_V11_FIRST_FAILED_NODE=1055
S21_V11_VK_RESULT=VK_ERROR_DEVICE_LOST

FAILURE_LOCATION_ISOLATED=TRUE
ROOT_CAUSE_ISOLATED=FALSE
ROOT_CAUSE_CLASS=UNET_NODE_1055_DEVICE_LOST
EXACT_ROOT_CAUSE=NOT_YET_ISOLATED
FIRST_FAILED_OPERATION=UNET_OPERATION_NOT_YET_DISAMBIGUATED
FIRST_FAILED_PIPELINE=NOT_YET_IDENTIFIED
FIRST_FAILED_SHADER=NOT_YET_IDENTIFIED
NEXT_ACTION=INSTRUMENT_NODE_1055_BEFORE_SELECTING_FIX

VULKAN_PACKAGE=INVALID_REJECTED
ACTIVE_CPU_UNCHANGED=TRUE
PUBLISH_READY=FALSE
```

---

## 2. Incontrovertible Evidence & Ground Truth

1. **Stage V10 GGML MatMul (`track_b_v10_matmul`)**:
   - Executable SHA256: `c60280d65e75e8c089325979973386754f6eff0b831d3d1eae91bb488f45e110`
   - Output: `RESULT=PASS_V10_MALI_GGML_MATMUL_SUCCESSFUL` (0 Mismatches, Max error `9.39e-05`)
   - Verified on `SM-G991N` Mali-G78 and fully frozen.

2. **Stage V11 Failure Location**:
   - Executable SHA256: `3291df600b540d52996cd98b89c8ccbf0c6f883b12651400ec7a1f137e4988e5`
   - Established Location: `Node 1055` in UNet Diffusion Sampling triggers `VK_ERROR_DEVICE_LOST` at `vkWaitForFences`.
   - Exact kernel operation, pipeline, shader, and dispatch geometry remain to be measured before applying any fix.

---

## 3. Resumption Instructions for Next Agent

1. **Clone & Switch**:
   ```bash
   git clone https://github.com/uno-km/termux-diffusion.git
   cd termux-diffusion
   git fetch --all --prune
   git switch feature/gpu
   git pull --ff-only origin feature/gpu
   ```
2. **Device Identity Gate**:
   - Verify `ro.product.model == SM-G991N` and `ro.product.device == o1s`.
3. **Instrumentation First**:
   - Instrument Node 1055 in `src_sd/ggml/src/ggml-vulkan/ggml-vulkan.cpp` to measure `OP`, `SHAPE`, `PIPELINE`, `SHADER`, and `WORKGROUP_SIZE`.
   - Select and apply the minimal single fix based on measured evidence.
   - Run V11 SDXS inference and verify PNG.
