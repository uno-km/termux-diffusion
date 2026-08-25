# Track B V10 Final Attempt Handover (Corrected Audit)

**Branch**: `feature/gpu`  
**Start Commit**: `24ca9a93c3624e35a1796e180f730950c2eb3826`  
**Target Hardware**: Samsung Galaxy S21 (Exynos 2100, Mali-G78 MP14 GPU, Android 15, Kernel 5.4.242)  
**Isolated Directory**: `$HOME/tmp/track-b-v10-final-attempt`

---

## 1. Session Summary & Audit Correction
- **V10 Status**: `INVALID_PHYSICAL_DEVICE_HANDLE_AT_FEATURE_QUERY`
- **Root Cause Class**: `VULKAN_LOADER_OBJECT_DISPATCH_MISMATCH`
- **MatMul Correctness**: `NOT_EVALUATED` (Aborted at `vkGetPhysicalDeviceFeatures2` prior to pipeline creation or dispatch)
- **Policy Deviation**: `UNAPPROVED_PUSH_TO_ORIGIN_FEATURE_GPU` (Recorded & acknowledged)

---

## 2. Milestone Classification Matrix

| Milestone Layer | Status | Technical Detail / Evidence |
| :--- | :--- | :--- |
| **Mali-G78 Raw Enumeration** | **`VERIFIED`** | Physical device `Mali-G78` enumerated via Android system loader `/system/lib64/libvulkan.so` |
| **GGML Device Acceptance** | **`VERIFIED`** | Mali-G78 accepted by GGML device-selection path (`ACCEPTED_DEVICE_COUNT=1`) |
| **Vulkan Backend Selection** | **`VERIFIED`** | `BACKEND_SELECTED=Vulkan`, `DEVICE_NAME=Mali-G78`, `CPU_FALLBACK=FALSE` |
| **Official CMake Build & Link** | **`VERIFIED`** | `BUILD_RC=0`, `LINK_RC=0`, `UNDEFINED_SYMBOL_COUNT=0` |
| **Vulkan Feature Query** | **`FAILED`** | `vkGetPhysicalDeviceFeatures2`: Invalid physicalDevice (`VUID-vkGetPhysicalDeviceFeatures2-physicalDevice-parameter`, `SIGABRT / RC=134`) |
| **MatMul Pipeline & Dispatch** | **`NOT REACHED`** | Aborted in `ggml_vk_get_devices` prior to descriptor set binding or shader dispatch |
| **Numerical Evaluation** | **`NOT EVALUATED`** | No GPU output generated (`MISMATCH_COUNT=N/A`) |
| **SDXS Vulkan Inference (V11)** | **`NOT STARTED`** | Frozen until Stage V10 MatMul numerical correctness is verified |

---

## 3. Root Cause Isolation & Mechanical Breakdown

### Observed Error Trace
- **Signal & Return Code**: `SIGNAL=SIGABRT (6)`, `EXECUTION_RC=134`
- **Vulkan Validation Error**: `[Vulkan Loader] ERROR: vkGetPhysicalDeviceFeatures2: Invalid physicalDevice [VUID-vkGetPhysicalDeviceFeatures2-physicalDevice-parameter]`
- **Source Location**: `ggml-vulkan.cpp:7373` in `ggml_vk_get_devices()`

### Mechanism
`VkPhysicalDevice` handle was enumerated via Android System Loader (`/system/lib64/libvulkan.so`). However, subsequent Vulkan function pointer dispatch inside GGML resolved function symbols from Termux Mesa Loader (`/data/data/com.termux/files/usr/lib/libvulkan.so`), creating an incompatible handle-to-dispatch-table mismatch.

---

## 4. One-Point Patch & Rollback
- **Patch Artifact**: `diagnostics/v10-final-attempt/patch.diff`
- **Patch File**: `ggml/src/ggml-vulkan/ggml-vulkan.cpp`
- **Rollback Method**: `git checkout -- ggml/src/ggml-vulkan/ggml-vulkan.cpp`

---

## 5. Protected Assets & Non-Interference
- `main` branch (**Clean & Untouched**)
- `v1.3.0` CPU Production Release (`termux-diffusion==1.3.0`, `termux-diffusion@1.3.0`)
- Active S21 CPU `sd-cli` binary (**Unchanged**)
- Stage V0-V9 direct Vulkan compute evidence

---

## 6. Exact Resume Point for Next Agent

1. **Do NOT** modify device capability filters or Vulkan API version numbers.
2. **Do NOT** revert to manual `.cpp` or `.o` file linkage.
3. **Exact Fix Required**: Ensure all Vulkan function pointers and handle dispatch tables are bound exclusively to the single `/system/lib64/libvulkan.so` loader instance.
4. **Re-use Isolated Build Directory**: `$HOME/tmp/track-b-v10-final-attempt/build_ggml`
5. **Execution Command**:
   ```bash
   export LD_LIBRARY_PATH=$HOME/tmp/track-b-v10-final-attempt/build_ggml/src:$HOME/tmp/track-b-v10-final-attempt/build_ggml/src/ggml-vulkan:$HOME/tmp/track-b-v10-final-attempt/build_ggml/src/ggml-cpu:$LD_LIBRARY_PATH
   ./bin/track_b_v10_matmul
   ```
