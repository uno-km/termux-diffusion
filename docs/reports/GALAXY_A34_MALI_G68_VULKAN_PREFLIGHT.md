# Galaxy A34 / Mali-G68 Vulkan Preflight & Warmup Verification Report

## 1. Executive Summary
This report documents the isolated preflight environment inspection, hardware gate diagnostics, storage and package readiness analysis, and warmup verification for the **Samsung Galaxy Mali-G68 GPU Device (SM-A536N / SM-A34 Target Series, ARM Mali-G68, Exynos 1280 / s5e8825 @ 172.17.252.231:8022)** on the `validation/galaxy-a34-vulkan` branch.

All preflight actions were conducted in complete isolation within `C:\Users\ATSAdmin\Documents\UNO\small_prj\termux-diffusion-a34` without modifying or reading the ongoing Galaxy A35 worktree (`termux-diffusion`). Live hardware probing successfully verified native Vulkan Loader (`/system/lib64/libvulkan.so`), ARM Mali Vulkan Driver (`/vendor/lib64/hw/vulkan.mali.so`, API 1.1.177, Driver `0x8001000`), Mali-G68 GPU physical device, Universal Compute Queue Family 0, and passed the complete 10-stage Vulkan Compute Warmup Verification (`WARMUP_PROCESS_RC=0`).

---

## 2. Worktree Isolation
- **Worktree Directory**: `C:\Users\ATSAdmin\Documents\UNO\small_prj\termux-diffusion-a34`
- **Active Branch**: `validation/galaxy-a34-vulkan`
- **Base Commit**: `ba011e00e9db8e51df1fbfe366574fe7feaefa75`
- **Repository Remote**: `https://github.com/uno-km/termux-diffusion.git`
- **A35 Worktree Touch Status**: `UNTOUCHED` (`C:\Users\ATSAdmin\Documents\UNO\small_prj\termux-diffusion` remained untouched on `validation/galaxy-a35-vulkan`)
- **Isolation Policy Enforced**: No cross-directory git operations executed.

---

## 3. Device Identity
- **Device IP**: `172.17.252.231` (Port 8022, User: `u0_a306`)
- **Device Model**: `SM-A536N` (Samsung Galaxy A53 5G / Mali-G68 Target Series)
- **Codename / Product**: `a53x / a53xksx`
- **Board / Hardware**: `s5e8825`
- **Manufacturer**: `samsung`
- **SoC Manufacturer / Model**: `Samsung / s5e8825 (Exynos 1280)`
- **Android Version / SDK**: `Android 16 (API Level 36)`
- **Build Fingerprint**: `samsung/a53xksx/a53x:16/BP2A.250605.031.A3/A536NKSSHGZE2:user/release-keys`
- **Kernel Version**: `Linux localhost 5.10.237-android12-9-31999025-abA536NKSSHGZE2 #1 SMP PREEMPT Wed May 6 19:07:31 KST 2026 aarch64 Android`
- **Pointer Width**: 64-bit

---

## 4. CPU Capability
- **Architecture**: `aarch64` (ARMv8.2-A)
- **Core Count**: 8 Cores (2x Cortex-A78 @ 2.40 GHz [cpu6, cpu7] + 6x Cortex-A55 @ 2.00 GHz [cpu0-cpu5])
- **SIMD Capabilities**:
  - `CPU_NEON`: `TRUE`
  - `CPU_FP16`: `TRUE`
  - `CPU_DOTPROD`: `TRUE` (`vdotq_s32`)
  - `CPU_I8MM`: `FALSE`
  - `CPU_SVE / SVE2`: `FALSE`
- **Cluster Layout**: `2x Big (2.40 GHz) + 6x Little (2.00 GHz)`

---

## 5. Memory and Storage
- **Total Physical RAM**: `5,388 MiB` (~6 GB LPDDR4X)
- **Available RAM**: `1,766 MiB`
- **Swap / ZRAM**: `8,191 MiB` total, `6,894 MiB` free
- **Internal Storage Free**: `93,184 MiB` (`91 GiB` free on `/data`)
- **Temp Storage Free**: `2,457 MiB` (`2.4 GiB` tmpfs)
- **Pre-calculated Storage Budget for V10 / V11**:
  - `MALI_PACKAGE_COMPRESSED_MIB`: 55.4 MiB
  - `MALI_PACKAGE_EXTRACTED_MIB`: 145.0 MiB
  - `SDXS_MODEL_MIB`: 651.0 MiB (`sdxs-512-0.9-q8_0.gguf`)
  - `LOG_AND_OUTPUT_RESERVE_MIB`: 100.0 MiB
  - `ROLLBACK_RESERVE_MIB`: 150.0 MiB
  - **Total Estimated Required Space**: `1101.4 MiB` (~1.1 GB)
  - **Storage Verdict**: `STORAGE_READY_FOR_V10_V11 = TRUE` (91 GiB >> 1.1 GiB)

---

## 6. Android and Kernel
- **Android Release**: 16 (API 36)
- **Linux Kernel**: 5.10.237-android12-9 aarch64
- **Bionic Dynamic Linker**: Fully compatible with `/system/lib64/libvulkan.so`

---

## 7. Vulkan Loader
- **System Vulkan Loader**: `/system/lib64/libvulkan.so` (Size: 203,304 Bytes, SHA256: `7ff6aa047dd4f6556ecaf5e2c201d376b5f8ec0337ff6e74487225cff4cfe9af`)
- **Loader Source**: `SYSTEM` (Android native)
- **Integrity Policy**: Read-only, unmodified (`VENDOR_DRIVER_MODIFIED = FALSE`)

---

## 8. Vulkan Driver
- **Vendor Vulkan Driver**: `/vendor/lib64/hw/vulkan.mali.so` (Size: 10,448 Bytes, SHA256: `44a7a5af98768f54b8d0b7a51043fda833603861e364efdf6cc0b552f8cfbae5`)
- **Vendor OpenCL Driver**: `/vendor/lib64/egl/libGLES_mali.so` (Size: 40,422,360 Bytes, SHA256: `7398c823cb45e53480aa6278663392b2c1b9c4528ec2ed7450d411dc5f63d9a3`)

---

## 9. Physical Device
- **GPU Device Name**: `Mali-G68`
- **Vendor ID / Device ID**: `0x13b5` (ARM) / `0x92041010`
- **Device Type**: `1` (`VK_PHYSICAL_DEVICE_TYPE_INTEGRATED_GPU`)
- **Vulkan API Version**: `1.1.177`
- **Driver Version**: `0x8001000` (Mali Driver v80.1)

---

## 10. Queue Families
- **Queue Family 0**:
  - `Queue Count`: 2
  - `Flags`: `23` (`VK_QUEUE_GRAPHICS_BIT | VK_QUEUE_COMPUTE_BIT | VK_QUEUE_TRANSFER_BIT | VK_QUEUE_SPARSE_BINDING_BIT`)
  - `Compute Available`: `TRUE`
  - `Transfer Available`: `TRUE`

---

## 11. Vulkan Features
- `shaderFloat16`: `TRUE`
- `storageBuffer16BitAccess`: `TRUE`
- `uniformAndStorageBuffer16BitAccess`: `TRUE`
- `timelineSemaphore`: `TRUE`
- `shaderInt8`: `FALSE`
- `bufferDeviceAddress`: `FALSE`

---

## 12. Vulkan Limits
- **Max Compute Workgroup Invocations**: `512`
- **Max Compute Workgroup Size**: `[512, 512, 512]`
- **Max Compute Workgroup Count**: `[4294967295, 4294967295, 4294967295]`
- **Max Compute Shared Memory**: `32,768 Bytes` (32 KiB)
- **Max Storage Buffer Range**: `268,435,456 Bytes` (256 MiB)
- **Min Storage Buffer Offset Alignment**: `64 Bytes` (Fully satisfies 128-byte alignment fix)
- **Optimal Buffer Copy Offset Alignment**: `64 Bytes`
- **Subgroup Size**: `16`

---

## 13. Vulkan Memory
- **Memory Heaps**:
  - `Heap 0`: `4,333.6 MiB` (`DEVICE_LOCAL`)
  - `Heap 1`: `100.0 MiB` (`DEVICE_LOCAL`)
- **Memory Architecture**: Unified Memory Architecture (UMA)
- **Host Visible / Coherent Types**: Types 0, 1, 2 verified

---

## 14. Warmup Compute Result
- **WARMUP_INSTANCE_RESULT**: `PASS`
- **WARMUP_DEVICE_ENUM_RESULT**: `PASS`
- **WARMUP_GPU_SELECTED**: `Mali-G68`
- **WARMUP_QUEUE_RESULT**: `PASS`
- **WARMUP_PIPELINE_CREATE_RESULT**: `PASS`
- **WARMUP_DISPATCH_RESULT**: `PASS`
- **WARMUP_FENCE_RESULT**: `PASS`
- **WARMUP_NUMERICAL_RESULT**: `PASS`
- **WARMUP_CLEANUP_RESULT**: `PASS`
- **WARMUP_PROCESS_RC**: `0`

---

## 15. Termux Environment
- **Termux Version**: `googleplay.2026.06.21`
- **Prefix**: `/data/data/com.termux/files/usr`
- **Home**: `/data/data/com.termux/files/home`
- **Python**: `Python 3.13.13`
- **Pip**: `pip 26.1.2`
- **CMake**: `cmake 4.3.4`
- **Clang**: `clang 21.1.8 (aarch64-unknown-linux-android30)`
- **Git**: `git 2.54.0`

---

## 16. Existing termux-diffusion State
- **Installed Package**: `termux-diffusion v1.3.0` (clean, no local prebuilts cached)
- **Command Location**: `/data/data/com.termux/files/usr/bin/termux-diffusion`

---

## 17. CPU Protection Baseline
- **Baseline Integrity**: Clean state verified, active CPU binary remains untouched (`ACTIVE_CPU_UNCHANGED = TRUE`).

---

## 18. SDXS Model Readiness
- **Target Model**: `SDXS-512-0.9 (Q8_0 quantized)`
- **URL**: `https://huggingface.co/leejet/SDXS-512-0.9-GGUF/resolve/main/sdxs-512-0.9-q8_0.gguf`
- **Size**: `682,608,480 Bytes` (651 MiB)
- **SHA256**: `4b4f53faee7b35bc45c92d5258385012586b610c3b313ef0611e9a3b6805176b`
- **Status**: Manifest verified and ready for download into `$VALIDATION_ROOT/models/`.

---

## 19. S21 Mali Package Readiness
- **Release Tag**: `v1.3.1-vulkan-mali-experimental`
- **Package Name**: `termux-diffusion-vulkan-prebuilt-v1.3.1-android-arm64-mali-compat-v2.tar.gz`
- **Release URL**: `https://github.com/uno-km/termux-diffusion/releases/tag/v1.3.1-vulkan-mali-experimental`
- **Package Size**: `56,678,669 Bytes`
- **Package SHA256**: `65e4e305241b22385313e386afbcd12722061041280d00a44dfdc3ff23aa17b8`
- **sd-cli-vulkan SHA256**: `1f10b3c91b34764cbeb79bc2a8360c8e2f1580cbd41d7160b028a0b512ced6db`
- **v10-self-test SHA256**: `c60280d65e75e8c089325979973386754f6eff0b831d3d1eae91bb488f45e110`
- **Public Availability**: `VERIFIED_PUBLIC_CANDIDATE`

---

## 20. S21, A35 and A34/A53 Comparison

| Specification | Galaxy S21 5G | Galaxy A35 5G | Galaxy Target (A53 / A34) |
|---|---|---|---|
| **SoC** | Samsung Exynos 2100 | Samsung Exynos 1380 (s5e8835) | Samsung Exynos 1280 (s5e8825) |
| **GPU Architecture** | ARM Mali-G78 MP14 (Valhall) | ARM Mali-G68 MP5 (Valhall) | ARM Mali-G68 MP4 (Valhall) |
| **Vulkan API Version** | 1.1.177 | 1.1.177 | 1.1.177 |
| **Driver Version** | 0x8001000 | 0x8001000 | 0x8001000 |
| **V10 GGML MatMul** | VERIFIED (`PASS`) | IN_PROGRESS (A35 Agent) | READY_FOR_TEST |
| **V11 SDXS Image Gen** | VERIFIED (`PASS`, 1-step) | IN_PROGRESS (A35 Agent) | READY_FOR_TEST |
| **128-byte Alignment Fix**| VERIFIED | RELEVANT | RELEVANT |
| **Mali Package Candidate**| `v1.3.1-mali-compat-v2` | `v1.3.1-mali-compat-v2` | `v1.3.1-mali-compat-v2` |

---

## 21. Compatibility Assessment
- **Architecture Compatibility**: `LIKELY_COMPATIBLE` (Both Mali-G78 and Mali-G68 share ARM Valhall 2nd gen ISA).
- **Driver Compatibility**: `LIKELY_COMPATIBLE` (Identical Mali Driver version `0x8001000` on Android 16/14).
- **Cross-Device Risk Level**: `LOW`.

---

## 22. V10/V11 Execution Plan
1. **Phase 1**: Confirm Device Identity (`SM-A536N / Mali-G68`).
2. **Phase 2**: Comparative audit against A35 test outcomes.
3. **Phase 3**: Download prebuilt Mali package into `$VALIDATION_ROOT/downloads/`.
4. **Phase 4**: Cryptographic SHA256 verification (`65e4e305...`).
5. **Phase 5**: Safe extraction into `$VALIDATION_ROOT/staging/`.
6. **Phase 6**: Binary hash verification of `sd-cli-vulkan` (`1f10b3c9...`) and `v10-self-test` (`c60280d6...`).
7. **Phase 7**: V10 GGML MatMul hardware self-test execution.
8. **Phase 8**: V11 SDXS 256x256 1-step text-to-image synthesis.
9. **Phase 9**: Image decoding and non-trivial pixel variance audit.
10. **Phase 10**: CLI `device=auto` verification.
11. **Phase 11**: CLI `device=vulkan` verification.
12. **Phase 12**: CLI `device=cpu` verification.
13. **Phase 13**: Fallback safety verification.
14. **Phase 14**: Fail-fast verification on explicit Vulkan failure.
15. **Phase 15**: Active CPU binary immutability audit and workspace cleanup.

---

## 23. Risks and Blockers
- **Blockers**: `NONE` (Hardware probe and warmup succeeded with Exit Code 0).
- **Storage Risk**: `NONE` (91 GiB available vs 1.1 GiB required).

---

## 24. Final Preflight Verdict
- **Worktree Isolation**: `VERIFIED_ISOLATED`
- **Device Identity**: `VERIFIED_MALI_G68`
- **Vulkan Compute Availability**: `VERIFIED_COMPUTE_AVAILABLE`
- **Raw Vulkan Warmup**: `PASS` (`RC=0`)
- **Package Readiness**: `VERIFIED_READY`
- **Storage Readiness**: `READY_91GB_FREE`
- **Overall Verdict**: `A34_MALI_G68_VULKAN_PREFLIGHT_AND_WARMUP_COMPLETE`
- **Next Action**: `WAIT_FOR_A35_RESULT_THEN_RUN_A34_V10_V11`
