# Mali-G78 GPU Enablement & GGML Vulkan Handover Document

**Branch**: `feature/gpu`  
**Target Hardware**: Samsung Galaxy S21 (Exynos 2100, Mali-G78 MP14 GPU, Vulkan API 1.1.213)  
**Status**: V0-V9 `VERIFIED`, V10 Build `PASS` / Runtime `RUNTIME_DEVICE_DISCOVERY_BLOCKED`

---

## 1. Executive Summary & Verified Milestones

The Samsung Galaxy S21 Mali-G78 GPU Vulkan compute pipeline has been proven and hardware-validated from raw loader open down to SPIR-V compute shader dispatch and array checksum verification.

### Completed & Frozen Stages (Stages V0 - V9) — 100% VERIFIED
1. **V0 Vulkan Loader & V1 Instance**: `dlopen("libvulkan.so")` and `vkCreateInstance` succeeded on S21 Termux.
2. **V2 Physical Device & V3 Hardware Selection**: Physical device enumerated as `Mali-G78` (`Vendor: 0x13b5`, `Device: 0x92020010`, `API: 1.1.213`, `DeviceType: INTEGRATED_GPU`).
3. **V4 Compute Queue & V5 Logical Device**: Selected Queue Family #0 (`queueFlags: 0x00000017`, shared graphics+compute). Created `VkDevice` (`vkCreateDevice` RC=0) and fetched valid `VkQueue` handle.
4. **V6 Buffer & Host Memory Allocation**: Allocated 64 KiB storage buffer (`HostVisible: YES`, `HostCoherent: YES`, `DeviceLocal: YES`). Mapped host memory, wrote test patterns, and read back with 0 errors.
5. **V7 SPIR-V Compute Pipeline**: Compiled 1,252-byte compute shader (SHA256: `f47bac...`) creating `VkShaderModule` and `VkPipeline`.
6. **V8 GPU Shader Dispatch**: Dispatched `vkCmdDispatch(4, 1, 1)` on Mali-G78 compute queue. `vkWaitForFences` returned `0` (`PASS`).
7. **V9 GPU Output Result Validation**: Evaluated $output[i] = input[i] \times 2 + 1$ across 256 uint32 elements. Expected checksum `65536` matched actual checksum `65536` with **0 mismatches**.

---

## 2. Stage V10 Status & Current Block

### V10 GGML-Vulkan Integration Status
- **CMake Target Build**: **`PASS`** (`BUILD_METHOD=OFFICIAL_CMAKE_TARGET_GRAPH`, `LINK_RC=0`, `UNDEFINED_SYMBOL_COUNT=0`).
- **Runtime Execution**: **`RUNTIME_DEVICE_DISCOVERY_BLOCKED`** (`ggml_vulkan: No devices found.`).

### Root Cause Analysis & Diagnostic Hypothesis
Direct Vulkan calls (Stages V0-V9) successfully select and run on Mali-G78. However, `ggml-vulkan` reports `No devices found.`.

This narrows the issue down to two specific possibilities:
- **Possibility A (Loader Lookup Mismatch)**: `vkEnumeratePhysicalDevices` inside `ggml-vulkan` returns 0 physical devices because `vkGetInstanceProcAddr` or loader symbols differ from system `libvulkan.so`.
- **Possibility B (Capability Filter Rejection)**: `vkEnumeratePhysicalDevices` detects Mali-G78, but `ggml_vk_device_is_supported` or extension/feature checks reject Mali-G78 (e.g. 16-bit storage buffer or Vulkan 1.2 requirement check).

---

## 3. Execution Protocol & Action Plan for the Next Agent

> **STRICT DIRECTIVE**: Do NOT iterate in manual `.cpp` compilation loops or modify build scripts. Use the official CMake target graph.

### Diagnostic Procedure (Single-Pass Probe)
1. **Instrument `ggml-vulkan.cpp`**: Add explicit diagnostic `std::cerr` print logs in `ggml_vk_instance_init()` and `ggml_vk_get_devices()`:
   - Print raw physical device count returned by `vk_instance.instance.enumeratePhysicalDevices()`.
   - Print `deviceName`, `deviceType`, and `apiVersion` for each physical device.
   - Print the boolean return value of `ggml_vk_device_is_supported(dev)` and the result of individual feature checks (`storageBuffer16BitAccess`, etc.).
2. **Execute V10 Probe**: Run `track_b_v10_matmul` with `LD_LIBRARY_PATH` set on S21.
3. **Isolate & Apply Single Fix**:
   - If **Raw Count == 0** (Possibility A): Align Vulkan loader initialization or dynamic dispatcher loading with system `libvulkan.so`.
   - If **Mali-G78 Enumerated but Rejected** (Possibility B): Adjust the failing feature check in `ggml_vk_device_is_supported` to bypass false-negative capability rejections for Mali-G78.
4. **Verify MatMul Result**: Verify FP32 $32 \times 32$ matrix multiplication output ($C = A \times B$) against CPU reference calculation ($Max/Mean\ Absolute\ Error < 10^{-4}$).
5. **Proceed to Stage V11**: Execute strict Vulkan SDXS 256x256 1-step inference on Mali-G78.

---

## 4. Success Criteria for Stage V10 & V11

### Stage V10 MatMul Target Output
```text
V10_BACKEND_REQUESTED=vulkan
V10_BACKEND_SELECTED=vulkan
V10_DEVICE_NAME=Mali-G78
V10_CPU_FALLBACK=FALSE
V10_OPERATION=mul_mat
V10_MATRIX_SHAPE=32x32
V10_DATA_TYPE=FP32
V10_GRAPH_COMPUTE_RESULT=PASS
V10_ELEMENT_COUNT=1024
V10_MISMATCH_COUNT=0
V10_MAX_ABS_ERROR=0.000000e+00
V10_MEAN_ABS_ERROR=0.000000e+00
V10_NAN_COUNT=0
V10_INF_COUNT=0
V10_TOLERANCE=1.000000e-04
V10_CLEANUP_RESULT=PASS
PROCESS_RC=0
RESULT=PASS_V10_MALI_GGML_MATMUL_SUCCESSFUL
```

### Stage V11 SDXS Target Output
```text
V11_BACKEND_SELECTED=vulkan
V11_DEVICE_NAME=Mali-G78
V11_CPU_FALLBACK=FALSE
V11_MODEL=sdxs_256x256_1step
V11_INFERENCE_RESULT=PASS
V11_OUTPUT_IMAGE=sdxs_mali_g78_vulkan.png
PROCESS_RC=0
RESULT=PASS_V11_MALI_SDXS_VULKAN_SUCCESSFUL
```

---

## 5. File Structure & Key Artifacts

- **V10 Probe Source**: `gpu-probe-suite/v10/track_b_v10_matmul.cpp`
- **V0-V9 Probes**: `gpu-probe-suite/`
- **Handover Document**: `docs/handover/GPU_MALI_G78_HANDOVER.md`
- **Master Report**: `Termux_Diffusion_v1.2.1_Master_Technical_Report.md` in Antigravity Brain artifacts.
