# Track B Stage V10 Vulkan Loader Alignment & Diagnostic Handover

**Branch**: `feature/gpu`  
**Commit**: `34ae184661f0c0d597135278844d376b9afe915a`  
**Target Hardware**: Samsung Galaxy S21 (Exynos 2100, Mali-G78 MP14 GPU, Android 15)  
**Isolated Execution Directory**: `$HOME/tmp/track-b-v10-loader-alignment`

---

## 1. Executive Summary & Root Cause Isolation

The root cause of `ggml_vulkan: No devices found.` has been **empirically isolated**:

- **Direct Probe Loader (V0-V9)**: Resolved to Android System Vulkan Loader (`/system/lib64/libvulkan.so`). Successfully enumerated physical device `Mali-G78` (`VendorID: 0x13b5`, `DeviceID: 0x92020010`).
- **GGML Process Loader (V10)**: Resolved to Termux Mesa Vulkan Loader (`/data/data/com.termux/files/usr/lib/libvulkan.so.1.4.354`). Enumerated `llvmpipe (LLVM 21.1.8, 128 bits)` (CPU renderer, `deviceType = 4`), which GGML's capability filter rejected as a non-discrete/non-integrated GPU, resulting in `No devices found.`.

```text
ROOT_CAUSE_CLASS=LOADER_PATH_MISMATCH_CONFIRMED
ROOT_CAUSE_ISOLATED=TRUE
```

---

## 2. Loader Comparison Data

| Metric | Direct Probe (V0-V9) | GGML Process (V10) |
| :--- | :--- | :--- |
| **Resolved Library Path** | `/system/lib64/libvulkan.so` | `/data/data/com.termux/files/usr/lib/libvulkan.so.1.4.354` |
| **Provider** | System Vulkan ICD | Termux Mesa Loader |
| **Raw Device Count** | `1` | `1` |
| **Raw Device #0 Name** | `Mali-G78` | `llvmpipe (LLVM 21.1.8, 128 bits)` |
| **Raw Device #0 Type** | `Integrated GPU (1)` | `CPU Renderer (4)` |
| **Paths Identical?** | **`FALSE`** | **`FALSE`** |

---

## 3. One-Point Loader Alignment Patch & Execution Results

### Applied Patch (`diagnostics/v10-loader-alignment/patch.diff`)
Instrumented `ggml-vulkan.cpp` to explicitly load `/system/lib64/libvulkan.so` via `dlopen` for dynamic dispatch initialization, bypassing the Termux Mesa loader override.

### Outcome
- **CMake Build & Link**: `CONFIGURE_RC=0`, `BUILD_RC=0`, `LINK_RC=0`, `UNDEFINED_SYMBOL_COUNT=0`.
- **Device Discovery Result**: Bypassed Mesa `llvmpipe` and successfully restored `Mali-G78` enumeration in `ggml-vulkan`.
- **Device Feature Dispatch Signal**: Signal 6 (`SIGABRT`) triggered during `vkGetPhysicalDeviceFeatures2` call due to Vulkan-Hpp dynamic dispatcher handle binding mismatch on Vulkan 1.1 Android ICD (`1.1.213`).

---

## 4. Next Resume Point & Instructions for Next Agent

1. **Do NOT** revert to manual `.cpp` or `.o` file linkage.
2. **Do NOT** modify system or vendor Vulkan libraries.
3. **Exact Fix Needed**: Align `vkGetInstanceProcAddr` dynamic function pointers (`DispatchLoaderDynamic`) in `ggml-vulkan.cpp` so that `vkGetPhysicalDeviceFeatures2` is dispatched via the instance-level handle returned by `/system/lib64/libvulkan.so`.
4. **V11 Requirement**: Do not start V11 SDXS inference until V10 FP32 MatMul completes with 0 mismatches.
