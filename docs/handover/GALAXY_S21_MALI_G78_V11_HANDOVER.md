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
S21_V11_DIFFUSION_SAMPLING=BLOCKED_AT_NODE_1055
VULKAN_PACKAGE=INVALID_REJECTED
ACTIVE_CPU_UNCHANGED=TRUE
PUBLISH_READY=FALSE
```

---

## 2. Incontrovertible Evidence & Binary Identity

1. **Stage V10 GGML MatMul (`track_b_v10_matmul`)**:
   - SHA256: `c60280d65e75e8c089325979973386754f6eff0b831d3d1eae91bb488f45e110`
   - Output: `RESULT=PASS_V10_MALI_GGML_MATMUL_SUCCESSFUL` (0 Mismatches, Max error `9.39e-05`)
   - Fully frozen and verified.

2. **Stage V11 Failure Isolation**:
   - Executable SHA256: `3291df600b540d52996cd98b89c8ccbf0c6f883b12651400ec7a1f137e4988e5`
   - Exact Blocker: `Node 1055` in UNet Diffusion Sampling triggers `VK_ERROR_DEVICE_LOST` under Vulkan 1.1 single-loader without kernel splitting.

---

## 3. Next Resumption Steps for Release Management Agent

When resuming on S21:
1. Validate Device Gate (`SM-G991N`, `o1s`).
2. Implement split-dispatch or workgroup size clamp for Node 1055 in `src_sd/ggml/src/ggml-vulkan/ggml-vulkan.cpp`.
3. Re-run `sd-cli` and verify complete PNG output.
4. Package `termux-diffusion-vulkan-prebuilt-v1.3.1-android-arm64-mali-compat-v2.tar.gz`.
