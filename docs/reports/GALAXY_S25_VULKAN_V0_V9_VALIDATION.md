# 📊 Galaxy S25 (Snapdragon 8 Elite / Adreno 830) Vulkan Compute V0~V9 Hardware Validation Report

**Document ID**: `GALAXY-S25-VULKAN-V0-V9-VAL`  
**Mission**: `GALAXY_S25_VULKAN_COMPUTE_V0_V9`  
**Target Device**: Samsung Galaxy S25 (`SM-S931N`, Codename: `pa1q`)  
**SoC Architecture**: Qualcomm Snapdragon 8 Elite (`SM8750`, `sun`)  
**GPU Family**: Qualcomm Adreno (`Adreno (TM) 830`, Vendor ID: `0x5143`, Device ID: `0x44050001`)  
**Validation Date**: 2026-08-26  
**Status**: **PASS (Stages V0 through V9 Verified)**  
**Classification**: `S25_RAW_VULKAN_COMPUTE=VERIFIED` | `S25_GGML_VULKAN_MATMUL=NOT_TESTED` | `S25_VULKAN_SDXS=NOT_TESTED`  

---

## 1. Executive Summary

This report documents the live on-device Vulkan compute validation (Stages V0 through V9) executed on the **Samsung Galaxy S25** (`SM-S931N`) running Android 16 (API Level 36) powered by the Qualcomm Snapdragon 8 Elite (`SM8750`) SoC with the **Adreno 830** GPU.

All operations adhered strictly to non-destructive verification policies:
1. Pre-existing system and vendor partition files were left 100% untouched.
2. Active CPU releases, sd-cli prebuilts, and configurations remained unchanged.
3. Tests executed in complete isolation under `$HOME/tmp/track-b-s25-v0-v9`.
4. All probes used dynamic, capability-based device and queue selection (zero hardware/vendor hardcoding).
5. Stages V0 through V9 all achieved **PASS** with zero numerical mismatches (Expected Checksum: 65536, Actual Checksum: 65536, Mismatch Count: 0).
6. Track B execution was stopped after Stage V9 awaiting explicit approval before any V10/V11 attempts.

---

## 2. Device and Android Environment

| Metric / Parameter | Value (Measured Ground Truth) |
| :--- | :--- |
| **Manufacturer** | `samsung` |
| **Model** | `SM-S931N` (Galaxy S25 Korea) |
| **Product** | `pa1qksx` |
| **Device Codename** | `pa1q` |
| **Android Version** | `16` |
| **Android API Level (SDK)** | `36` |
| **Build Fingerprint** | `samsung/pa1qksx/pa1q:16/BP4A.251205.006/S931NKSSBCZG3_OKRBCZG3:user/release-keys` |
| **Kernel Version** | `6.6.98-android15-8-pd6ff1cd-abogkiS931NKSSBCZG3-4k` |
| **ABI List** | `arm64-v8a` |
| **CPU Architecture** | `aarch64` |
| **CPU Core Count** | `8` (Qualcomm Oryon: 2 Prime @ 4.32GHz + 6 Performance @ 3.53GHz) |
| **RAM Total** | `11,113.50 MiB` (~12 GB LPDDR5X) |
| **Termux User** | `u0_a466` |
| **Termux Prefix** | `/data/data/com.termux/files/usr` |

---

## 3. SoC and GPU Ground Truth

| Property | Value |
| :--- | :--- |
| **SoC Model** | `SM8750` (Qualcomm Snapdragon 8 Elite) |
| **SoC Manufacturer** | `QTI` (Qualcomm Technologies, Inc.) |
| **Board Platform** | `sun` |
| **GPU Device Name** | `Adreno (TM) 830` |
| **GPU Type** | `VK_PHYSICAL_DEVICE_TYPE_INTEGRATED_GPU` (`1`) |
| **Vendor ID** | `0x5143` (Qualcomm) |
| **Device ID** | `0x44050001` |
| **Vulkan API Version** | `1.3.284` |
| **Vulkan Driver Version** | `0x80320040` |
| **Loader API Version** | `1.4.0` |

---

## 4. Termux Loader vs Android System Loader

Both loader pathways were evaluated independently to guarantee accurate hardware driver resolution.

| Property | Termux Default Loader | Android System Loader |
| :--- | :--- | :--- |
| **Loader Target** | `libvulkan.so` | `/system/lib64/libvulkan.so` |
| **Resolved Path** | `libvulkan.so` | `/system/lib64/libvulkan.so` |
| **Loader SHA-256** | N/A (Dynamic System Provider) | `ed2e11880f320081267a9cdb5bb0892e73a3b1d726061ab73540f4b2bbe13706` |
| **Raw Device Count** | `1` | `1` |
| **Device 0 Name** | `Adreno (TM) 830` | `Adreno (TM) 830` |
| **Device 0 Type** | `INTEGRATED_GPU` | `INTEGRATED_GPU` |
| **Device 0 Vendor ID** | `0x5143` | `0x5143` |
| **Device 0 Device ID** | `0x44050001` | `0x44050001` |
| **Device 0 API Version** | `1.3.284` | `1.3.284` |
| **Device 0 Driver Ver** | `0x80320040` | `0x80320040` |
| **Result** | **PASS** | **PASS** |

Both loader routes successfully resolved the real Qualcomm Adreno 830 hardware driver with identical device properties and zero software rasterizer fallbacks.

---

## 5. V0: Android System Vulkan Loader Test

- **Target Path**: `/system/lib64/libvulkan.so`
- **Loader File Size**: `256,784 bytes`
- **Loader SHA-256**: `ed2e11880f320081267a9cdb5bb0892e73a3b1d726061ab73540f4b2bbe13706`
- **dlopen Result**: `SUCCESS` (Handle: `0x490d7fcd2a12f437`)
- **vkGetInstanceProcAddr Provider**: `/system/lib64/libvulkan.so`
- **dlerror**: None
- **Stage Result**: `S25_V0_RESULT=PASS`

---

## 6. V1: Vulkan Instance Test

- **Loader Supported API Version**: `1.4.0`
- **Requested API Version**: `1.1.0`
- **Application Info**: `Galaxy S25 Vulkan Capability Probe`
- **Extensions / Layers Requested**: None (Headless compute mode)
- **vkCreateInstance Result**: `VK_SUCCESS` (`0`)
- **Instance Handle**: Valid non-null handle
- **Stage Result**: `S25_V1_RESULT=PASS`

---

## 7. V2: Physical-Device Enumeration

- **Total Physical Devices Found**: `1`
- **Device #0 Properties**:
  - `deviceName`: `Adreno (TM) 830`
  - `deviceType`: `VK_PHYSICAL_DEVICE_TYPE_INTEGRATED_GPU` (`1`)
  - `vendorID`: `0x5143` (Qualcomm)
  - `deviceID`: `0x44050001`
  - `apiVersion`: `1.3.284`
  - `driverVersion`: `0x80320040`
- **Software Rasterizer / llvmpipe Filter**: Not present; 100% hardware GPU.
- **Stage Result**: `S25_V2_RESULT=PASS`

---

## 8. V3: Hardware GPU Selection

- **Selection Logic**: Pure capability-based filtering (`deviceType == INTEGRATED_GPU || DISCRETE_GPU`). Zero hardcoded device name strings.
- **Selected Device Name**: `Adreno (TM) 830`
- **Selected Device Type**: `VK_PHYSICAL_DEVICE_TYPE_INTEGRATED_GPU`
- **Vendor ID**: `0x5143`
- **Device ID**: `0x44050001`
- **API Version**: `1.3.284`
- **Driver Version**: `0x80320040`
- **Stage Result**: `S25_V3_RESULT=PASS`

---

## 9. V4: Compute Queue Family Probe

- **Queue Family Count**: `3`
- **Queue Families Enumerated**:
  - **Family #0**: `count=3`, `flags=0x0000019f` (Compute: YES, Graphics: YES, Transfer: YES)
  - **Family #1**: `count=1`, `flags=0x00000002` (Compute: YES, Graphics: NO, Transfer: NO) -> **Dedicated Compute Queue!**
  - **Family #2**: `count=1`, `flags=0x00000004` (Compute: NO, Graphics: NO, Transfer: YES)
- **Selected Queue Family**: Index `1`
- **Selected Queue Count**: `1`
- **Selected Queue Flags**: `0x00000002` (`VK_QUEUE_COMPUTE_BIT`)
- **Dedicated Compute Queue**: `TRUE`
- **Stage Result**: `S25_V4_RESULT=PASS`

---

## 10. V5: Logical Device & Queue Retrieval

- **Queue Family Used**: Index `1` (Dedicated Compute)
- **Device Extensions Requested**: None
- **Device Features Requested**: None
- **vkCreateDevice Result**: `VK_SUCCESS` (`0`)
- **vkGetDeviceQueue Result**: Valid compute queue handle retrieved.
- **Queue Handle Valid**: `TRUE`
- **Stage Result**: `S25_V5_RESULT=PASS`

---

## 11. V6: Storage Buffer and GPU Memory

- **Memory Heaps**: `2`
- **Memory Types Available**: `9`
  - Type #0..#2: `0x00000001` (DeviceLocal: YES, HostVisible: NO)
  - Type #3: `0x0000000b` (DeviceLocal: YES, HostVisible: YES, HostCoherent: NO)
  - Type #4..#5: `0x00000007` (DeviceLocal: YES, HostVisible: YES, HostCoherent: YES)
  - **Type #6**: `0x0000000f` (DeviceLocal: YES, HostVisible: YES, HostCoherent: YES, HostCached: YES)
  - Type #7: `0x00000021` (DeviceLocal: YES, HostVisible: NO)
  - Type #8: `0x00000011` (DeviceLocal: YES, HostVisible: NO)
- **Test Buffer Size**: `65,536 bytes` (64 KiB, `VK_BUFFER_USAGE_STORAGE_BUFFER_BIT`)
- **Memory Requirements**: Size=`65536`, Alignment=`64`, MemoryTypeBits=`0x00000041`
- **Selected Memory Type**: Index `6` (`flags=0x0000000f`)
- **Host Visible**: `TRUE`
- **Host Coherent**: `TRUE`
- **Device Local**: `TRUE`
- **vkAllocateMemory Result**: `VK_SUCCESS` (`0`)
- **vkBindBufferMemory Result**: `VK_SUCCESS` (`0`)
- **vkMapMemory Result**: `VK_SUCCESS` (`0`)
- **Deterministic Pattern Written**: `i * 0x01010101`
- **Pattern Verification Readback**: `PASS` (0 mismatches across 16,384 uint32 words)
- **Stage Result**: `S25_V6_RESULT=PASS`

---

## 12. V7: SPIR-V Compute Pipeline Creation

- **Compute Shader Operation**: `output[i] = input[i] * 2 + 1`
- **SPIR-V Binary Size**: `1,228 bytes`
- **SPIR-V SHA-256**: `3bc597bd51e896a9f541de60ea360b08b826d87320e7d8896134a5f0d6525a2d`
- **Input Buffer**: 256 `uint32` elements (`1,024 bytes`), `input[i] = i`
- **Output Buffer**: 256 `uint32` elements (`1,024 bytes`), zero-initialized
- **Descriptor Set Bindings**:
  - Binding `0`: Input Storage Buffer (`VK_DESCRIPTOR_TYPE_STORAGE_BUFFER`, `COMPUTE_BIT`)
  - Binding `1`: Output Storage Buffer (`VK_DESCRIPTOR_TYPE_STORAGE_BUFFER`, `COMPUTE_BIT`)
- **vkCreateShaderModule**: `VK_SUCCESS` (`0`)
- **vkCreateDescriptorSetLayout**: `VK_SUCCESS` (`0`)
- **vkCreatePipelineLayout**: `VK_SUCCESS` (`0`)
- **vkCreateComputePipelines**: `VK_SUCCESS` (`0`)
- **Stage Result**: `S25_V7_RESULT=PASS`

---

## 13. V8: GPU Hardware Dispatch Execution

- **Elements Dispatched**: `256`
- **Workgroup Local Size**: `64` (`local_size_x = 64`)
- **Dispatch Workgroups**: `(groupCountX=4, groupCountY=1, groupCountZ=1)` (`4 * 64 = 256`)
- **vkCreateCommandPool**: `VK_SUCCESS` (`0`)
- **vkAllocateCommandBuffers**: `VK_SUCCESS` (`0`)
- **vkCmdDispatch**: Recorded & submitted to Dedicated Compute Queue.
- **vkQueueSubmit**: `VK_SUCCESS` (`0`)
- **vkWaitForFences**: `VK_SUCCESS` (`0`) (Completed in <5 ms, well within 5-second timeout)
- **Stage Result**: `S25_V8_RESULT=PASS`

---

## 14. V9: Numerical Validation

- **Element Count**: `256`
- **Calculation Formula**: `output[i] = input[i] * 2 + 1` (`2i + 1`)
- **Expected Checksum Calculation**:

  $$\sum_{i=0}^{255} (2i + 1) = 2 \times \frac{255 \times 256}{2} + 256 = 65280 + 256 = 65536$$

- **Expected Checksum**: `65536`
- **Actual Measured Checksum**: `65536`
- **Mismatch Count**: `0`
- **First Mismatch Index**: `-1` (None)
- **Stage Result**: `S25_V9_RESULT=PASS`

---

## 15. Cross-Device Comparison: S21 vs A35 vs S25

| Dimension | Galaxy S21 5G | Galaxy A35 5G | Galaxy S25 |
| :--- | :--- | :--- | :--- |
| **Model** | `SM-G991N` | `SM-A356N` | `SM-S931N` |
| **SoC** | Samsung Exynos 2100 | Samsung Exynos 1380 | Qualcomm Snapdragon 8 Elite (`SM8750`) |
| **CPU Cores** | 8 (1x X1 + 3x A78 + 4x A55) | 8 (4x A78 + 4x A55) | 8 (2x Oryon Prime + 6x Oryon Perf) |
| **RAM** | 8 GB LPDDR5 | 6 GB LPDDR4X | 12 GB LPDDR5X (`11,113.5 MiB`) |
| **GPU Vendor** | ARM (`0x13b5`) | ARM (`0x13b5`) | Qualcomm (`0x5143`) |
| **GPU Name** | Mali-G78 | Mali-G68 | **Adreno (TM) 830** |
| **Device ID** | `0x92020010` | `0x92041010` | `0x44050001` |
| **Vulkan API** | `1.1.213` | `1.3.219` | **`1.3.284`** (Loader 1.4.0) |
| **Driver Ver** | `0x07401000` | `0x09801000` | **`0x80320040`** |
| **Queue Families**| 1 (Queue 0 Shared) | 1 (Queue 0 Shared) | **3 (Queue 1 Dedicated Compute)** |
| **Memory Types** | 4 | 4 | **9** |
| **V0~V9 Probes** | PASS | PASS | **PASS** |
| **V10 GGML MatMul**| BLOCKED (Mali crash) | NOT_TESTED | **NOT_TESTED** |
| **V11 SDXS Inference**| BLOCKED (Mali crash) | NOT_TESTED | **NOT_TESTED** |

---

## 16. Shared Probe Assets

All probes were cross-compiled on the host PC using standard Android NDK r26b without on-device compilation:
- **Compiler**: Android NDK r26b Clang 17.0.2 (`aarch64-linux-android26`)
- **Shader Compiler**: Android NDK r26b `glslc.exe`
- **Probe Binaries**:
  - `track_b_vulkan_loader_compare` (SHA-256: `38d0349586c3df0c2f929959546acb6587d8a9285a5d06d16abcfa1ba6376796`)
  - `track_b_vulkan_probe_s25` (SHA-256: `dfc80f50e1f133c232f9448ef184576a38ffdca4a9162ba11a5aaa506c87c585`)
  - `compute_shader.spv` (SHA-256: `3bc597bd51e896a9f541de60ea360b08b826d87320e7d8896134a5f0d6525a2d`)

---

## 17. Device-Specific Results

Unlike the Samsung Exynos / ARM Mali architectures (S21 Mali-G78, A35 Mali-G68) which feature a single combined graphics/compute queue and 4 unified memory types, the **Qualcomm Adreno 830** on the Galaxy S25 provides:
1. **Dedicated Compute Queue**: Dedicated asynchronous compute queue family (Queue Index 1, flags `0x00000002`), bypassing the graphics pipeline completely.
2. **Advanced Memory Hierarchy**: 9 distinct memory types with full support for host-visible, host-coherent, device-local, and host-cached unified memory (Type 6, `0x0000000f`).
3. **Vulkan 1.3.284 / Loader 1.4.0**: Vulkan 1.3.284 was reported by the device. The tested storage-buffer, compute-pipeline, queue-submission, and synchronization paths passed. Additional extensions and subgroup capabilities require separate feature-level validation.

---

## 18. Known Limitations

1. **V0~V9 Scope Only**: V0~V9 validates raw Vulkan compute pipeline creation, shader execution, memory mapping, and numerical accuracy. It does not validate ggml matrix multiplication or full diffusion models.
2. **No NPU/QNN Validation**: This test specifically targets Vulkan GPU compute. Snapdragon NPU / QNN pathways were not evaluated.
3. **Headless Mode**: Validation was performed in pure headless compute mode without Android surface/display interaction.

---

## 19. V10 Readiness Assessment

| Requirement | Status | Details |
| :--- | :--- | :--- |
| **Vulkan 1.1+ Capability** | **READY** | Adreno 830 supports Vulkan `1.3.284` |
| **Dedicated Compute Queue**| **READY** | Queue Family 1 (`0x00000002`) available |
| **Host-Visible Device Memory**| **READY** | Type 6 provides coherent, cached, device-local memory |
| **SPIR-V Compute Pipeline**| **READY** | Shader modules and compute pipelines create and execute cleanly |
| **Numerical Determinism** | **READY** | 256/256 elements verified with 0 checksum mismatch |

**V10 Entry Recommendation**: The Galaxy S25 Adreno 830 is fully capable and ready for Stage V10 (`ggml-vulkan` matrix multiplication probe) once explicit user authorization is granted.

---

## 20. Final Decision Matrix

```

S25_RAW_VULKAN_COMPUTE=VERIFIED

S25_GGML_VULKAN_MATMUL=NOT_TESTED

S25_VULKAN_SDXS=NOT_TESTED

V10_STARTED=FALSE

V11_STARTED=FALSE

ACTIVE_SDCLI_UNCHANGED=TRUE

SYSTEM_VENDOR_FILES_UNCHANGED=TRUE

```

### Final Verdict:

**`RESULT=PASS_GALAXY_S25_VULKAN_COMPUTE_V0_V9`**  

**`S25_RAW_VULKAN_COMPUTE=VERIFIED`**  

**`TRACK_B_ACTION=STOPPED_AWAITING_V10_APPROVAL`**  
