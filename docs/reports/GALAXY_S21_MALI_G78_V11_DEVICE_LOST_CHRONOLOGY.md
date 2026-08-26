# Galaxy S21 (Mali-G78) V11 Device Lost Location Isolation & Diagnostic Chronology

## 1. Executive Summary

This document records the device identity verification, Stage V10 GGML MatMul completion, and exact failure location isolation for Stage V11 UNet Diffusion Sampling on Samsung Galaxy S21 (`SM-G991N` / `o1s` / Mali-G78).

---

## 2. Device Identity & Hardware Verification

- **Device Model**: `SM-G991N` (Galaxy S21 5G)
- **Codename**: `o1s`
- **Product**: `o1sksx`
- **Build Fingerprint**: `samsung/o1sksx/o1s:15/AP3A.240905.015.A2/G991NKSSCHZA9:user/release-keys`
- **SSH Host Key**: `SHA256:4tM3Jj/sP2iY9WJdD9UvR9Y4F5h4BwL9fM8bY+sX6/w`
- **SoC**: Samsung Exynos 2100
- **GPU Device**: ARM Mali-G78 MP14
- **Vulkan Driver Version**: `1.1.213` (System Loader: `/system/lib64/libvulkan.so`)

---

## 3. Ground Truth & Stage V10 MatMul Verification (Frozen)

Stage V10 GGML MatMul was executed in the isolated directory `/data/data/com.termux/files/home/tmp/track-b-s21-v10-v11-revalidation/build/` with the compiled executable `track_b_v10_matmul`.

```text
EXECUTABLE_PATH=/data/data/com.termux/files/home/tmp/track-b-s21-v10-v11-revalidation/build/bin/track_b_v10_matmul
EXECUTABLE_SHA256=c60280d65e75e8c089325979973386754f6eff0b831d3d1eae91bb488f45e110
PROC_EXE=/data/data/com.termux/files/home/tmp/track-b-s21-v10-v11-revalidation/build/bin/track_b_v10_matmul

DEVICE_MODEL=SM-G991N
DEVICE_NAME=Mali-G78
V10_OPERATION=mul_mat
V10_ELEMENT_COUNT=1024
V10_BACKEND_SELECTED=Vulkan0
V10_CPU_FALLBACK=FALSE
V10_GRAPH_COMPUTE_RESULT=PASS
V10_MISMATCH_COUNT=0
V10_MAX_ABS_ERROR=9.39369e-05
V10_MEAN_ABS_ERROR=3.96447e-05
V10_NAN_COUNT=0
V10_INF_COUNT=0
PROCESS_RC=0
RESULT=PASS_V10_MALI_GGML_MATMUL_SUCCESSFUL
```

---

## 4. Stage V11 Failure Location Isolation & Diagnostic Status

### 4.1. Telemetry & Established Facts
- **Model**: SDXS (512-DS) in GGUF format
- **Params**: 651.92 MB total
- **Text Encoder**: Allocated to Vulkan VRAM (`159.13 MB`), successfully completed `get_learned_condition` in 7.64s.
- **Diffusion Sampling**: With `GGML_VK_SERIALIZE_SUBMISSIONS=1`, execution failed at:
  ```text
  [ERROR] ggml_extend.hpp:72 - ggml_vulkan: device lost on Vulkan0 waiting for submission (nodes 1055 to 1055):
  libc++abi: terminating due to uncaught exception of type vk::DeviceLostError: vk::Device::waitForFences: ErrorDeviceLost
  ```

### 4.2. Diagnostic Status & Strict Ground Truth
- **Failure Location**: `Node 1055`
- **First Failed Stage**: `DIFFUSION_SAMPLING`
- **First Failed Vulkan Call**: `vkWaitForFences`
- **Vulkan Error**: `VK_ERROR_DEVICE_LOST`
- **Location Isolated**: `TRUE`
- **Exact Root Cause Isolated**: `FALSE`
- **Root Cause Class**: `UNET_NODE_1055_DEVICE_LOST`
- **Unconfirmed / Unmeasured Items for Node 1055**:
  - Exact GGML Operation (Conv2D, MulMat, Reshape, etc.)
  - Pipeline Name
  - Shader Variant
  - Workgroup Size & Dispatch Groups
  - Subgroup Configurations
  - Descriptor Buffer Ranges & Alignments
  - GPU Memory State & Driver Error Details

### 4.3. Next Resumption Policy
Before applying any patch (Split Dispatch, Workgroup Clamp, FP16 alteration, Subgroup toggle, or Timeout tuning), instrument Node 1055 to extract exact tensor dimensions, operation type, pipeline, and shader variant.
