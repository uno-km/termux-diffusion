# Track B V10 Final Attempt Handover

**Branch**: `feature/gpu`  
**Start Commit**: `24ca9a93c3624e35a1796e180f730950c2eb3826`  
**Target Hardware**: Samsung Galaxy S21 (Exynos 2100, Mali-G78 MP14 GPU, Android 15, Kernel 5.4.242)  
**Isolated Directory**: `$HOME/tmp/track-b-v10-final-attempt`

---

## 1. Session Summary
- **Diagnostic Run Count**: 1
- **Patch Attempt Count**: 1
- **Rebuild Count**: 1
- **V10 Execution Count**: 1
- **Final Status**: `V10_STATUS=DISPATCH_BINDING_ROOT_CAUSE_ISOLATED`

---

## 2. Preserved Ground Truth
- **V0~V9 Direct Probe**: **`VERIFIED`** (Headless Vulkan Compute Queue, Memory Mapping, SPIR-V Compute Shader Dispatch, 256-element array evaluation matched with 0 mismatches).
- **Loader Mismatch Root Cause**: **`ISOLATED & RESOLVED`** (Aligned `/system/lib64/libvulkan.so` Android System ICD Loader).
- **Mali-G78 GGML Device Selection**: **`VERIFIED`** (`MALI_G78_PRESENT=TRUE`, `ACCEPTED_DEVICE_COUNT=1`, `BACKEND_SELECTED=Vulkan`, `DEVICE_NAME=Mali-G78`, `CPU_FALLBACK=FALSE`).

---

## 3. Final Blocking Point
- **Signal**: Signal 6 (`SIGABRT` / `EXECUTION_RC=134`).
- **Observed Error**: `[Vulkan Loader] ERROR: vkGetPhysicalDeviceFeatures2: Invalid physicalDevice [VUID-vkGetPhysicalDeviceFeatures2-physicalDevice-parameter]`
- **Source File & Line**: `ggml-vulkan.cpp:7373` in `ggml_vk_get_devices()`.
- **Operation / Pipeline**: `ggml_vk_get_pipeline` (`matmul_f32_f32`).

---

## 4. One-Point Patch
- **Modified File**: `ggml/src/ggml-vulkan/ggml-vulkan.cpp`
- **Modification Reason**: Aligned `ggml_vk_default_dispatcher_instance` to dynamically load `vkGetInstanceProcAddr` from `/system/lib64/libvulkan.so` bypassing Termux Mesa loader.
- **Patch Artifact**: `diagnostics/v10-final-attempt/patch.diff`
- **Rollback Method**: `git checkout -- ggml/src/ggml-vulkan/ggml-vulkan.cpp`

---

## 5. Build and Execution
- **Configure RC**: 0, **Build RC**: 0, **Link RC**: 0
- **Undefined Symbol Count**: 0
- **Executable SHA-256**: `a5cb0542b14840c5aa4b14093cc66189449eab2f4550528b82c4c8bccbca74da`
- **Backend**: Vulkan
- **Device**: Mali-G78
- **CPU Fallback**: FALSE
- **Graph Compute Result**: `FAIL_DISPATCH_BINDING` (Aborted prior to tensor element evaluation)
- **MatMul Correctness**: `NOT EVALUATED`

---

## 6. Failed Approaches (Do Not Retry)
- Do NOT revert to manual `.cpp` or `.o` file linkage.
- Do NOT modify system or vendor Vulkan library files on `/system` or `/vendor`.
- Do NOT alter Vulkan API version numbers or relax device capability filters.
- Do NOT create multiple build variant scripts.

---

## 7. Exact Resume Point for Next Agent
- Verify instance-level handle binding for `vkGetPhysicalDeviceFeatures2` in `ggml-vulkan.cpp` when dispatching through `/system/lib64/libvulkan.so`.
- **Re-use Build Directory**: `$HOME/tmp/track-b-v10-final-attempt/build_ggml`
- **Execution Command**:
  ```bash
  export LD_LIBRARY_PATH=$HOME/tmp/track-b-v10-final-attempt/build_ggml/src:$HOME/tmp/track-b-v10-final-attempt/build_ggml/src/ggml-vulkan:$HOME/tmp/track-b-v10-final-attempt/build_ggml/src/ggml-cpu:$LD_LIBRARY_PATH
  ./bin/track_b_v10_matmul
  ```
- **V11 SDXS Start Condition**: Stage V10 FP32 MatMul must complete with 0 mismatches.

---

## 8. Protected Assets
- `main` branch
- `v1.3.0` CPU Production Release (`termux-diffusion==1.3.0`, `termux-diffusion@1.3.0`)
- Active CPU `sd-cli` binary
- V0~V9 direct probe evidence

---

## 9. Final Status
- **V0_V9_STATUS**: `VERIFIED`
- **V10_BUILD_STATUS**: `PASS`
- **V10_LOADER_STATUS**: `VERIFIED`
- **V10_DEVICE_STATUS**: `VERIFIED`
- **V10_DISPATCH_STATUS**: `BLOCKED`
- **V10_MATMUL_STATUS**: `NOT_EVALUATED`
- **V11_STATUS**: `NOT_STARTED`
- **ACTIVE_SDCLI_UNCHANGED**: `TRUE`
- **TRACK_B_ACTION**: `STOPPED_WITH_PATCH_OR_RESUME_POINT`
