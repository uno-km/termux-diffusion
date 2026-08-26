# Galaxy S25 Adreno Vulkan Release Handover

## 1. Executive Summary

- **Development Objective**: Enable verified, deterministic, hardware-accelerated Vulkan inference for Stable Diffusion (SDXS) on Qualcomm Snapdragon 8 Elite (Adreno 830) within Android Termux environment.
- **Achieved Milestones**:
  - Raw Vulkan compute probe suite: Stages V0 through V9 **VERIFIED** (Device enumerated, queue allocated, memory bound, SPIR-V pipeline compiled, kernel dispatched, math verified).
  - True GGML Vulkan Tensor Operation Probe: Stage V10 **VERIFIED** (`mul_mat` FP32 32x32 matrix multiplication, 1024 elements, 0 mismatches, max absolute error 3.757e-4, CPU Fallback = FALSE).
  - End-to-End Model Inference: Stage V11 **VERIFIED** (SDXS 512 Tiny SD Distilled Q8_0, 256x256, 1-step Euler A, total generation 4.39s C++ / 7.20s Python CLI, deterministic PNG SHA-256 `5fc44f5e...`).
- **User-Facing Value**: Delivers sub-5-second local generative AI inference on flagship Qualcomm Android devices, bypassing CPU compute bottlenecks.
- **Current Candidate Status**: `PACKAGE_STATUS=VERIFIED_UNSIGNED_EXPERIMENTAL_CANDIDATE`.
- **Remaining Release Gate**: Offline root key signing (`release-key-2026-01`) of `manifest-v1.3.1-vulkan-experimental.json` and GitHub Pre-release upload.

---

## 2. Hardware Ground Truth

- **Device Model**: Samsung Galaxy S25 (`SM-S931N`)
- **SoC**: Qualcomm Snapdragon 8 Elite (`sun` / Oryon CPU cores)
- **GPU**: Qualcomm Adreno (TM) 830
- **Android Version / API**: Android 15 (Linux Kernel 6.6.56, API Level 35)
- **Vulkan API & Driver**: Vulkan 1.3.284 / Qualcomm Technologies Inc. Adreno Vulkan Driver (`vulkan.adreno.so` v0800.64.7)
- **Vulkan Driver Path**: `/system/lib64/libvulkan.so`
- **Vulkan Queue Family**: Index 0 (Graphics | Compute | Transfer, 1 queue)
- **Memory Properties**: Unified Memory Architecture (UMA = 1), Device Local + Host Visible (Heap 0: 11,468 MB)
- **Subgroup & Arithmetic Properties**:
  - Fixed Hardware Wave Size: 64 (`subgroupSize = 64`, `minSubgroupSize == maxSubgroupSize == 64`)
  - Subgroup Operations: Basic & Vote supported; 16-bit Float arithmetic (`f16vec2` reduction) unsupported by Adreno driver.
  - Max Compute Workgroup Invocations: 1024 (Total threads per workgroup capped at 1024).

---

## 3. Complete Engineering Chronology

1. **Stage V0 - Vulkan Loader & Linking (`VERIFIED`)**: Dynamically resolved Vulkan entrypoints via `/system/lib64/libvulkan.so` and `dlopen`/`dlsym`.
2. **Stage V1 - VkInstance Creation (`VERIFIED`)**: Initialized instance with API version 1.3.0.
3. **Stage V2 - Physical Device Enumeration (`VERIFIED`)**: Identified Qualcomm Adreno (TM) 830 (Device ID `0x43050a01`, Vendor ID `0x5143`).
4. **Stage V3 - GPU Selection (`VERIFIED`)**: Successfully selected discrete/integrated Adreno compute queue family.
5. **Stage V4 - Compute Queue Discovery (`VERIFIED`)**: Acquired compute command queue from family 0.
6. **Stage V5 - Logical Device Creation (`VERIFIED`)**: Created VkDevice with 16-bit storage, float16 arithmetic, and timeline semaphores enabled.
7. **Stage V6 - GPU Memory Allocation & Mapping (`VERIFIED`)**: Allocated and memory-mapped host-visible unified buffer.
8. **Stage V7 - Compute Pipeline Compilation (`VERIFIED`)**: Compiled SPIR-V compute shader into VkPipeline.
9. **Stage V8 - Kernel Dispatch & Execution (`VERIFIED`)**: Dispatched 1D compute workgroup with fence synchronization.
10. **Stage V9 - Numerical Correctness Validation (`VERIFIED`)**: Validated FP32 vector math with zero absolute error.
11. **Stage V10 - Upstream GGML Vulkan MatMul Failure Analysis & Fixes**:
    - *Failure 1 (Workgroup Size Overrun)*: Upstream GGML allocated workgroup dimensions exceeding 1024 on Wave64 architectures. **Fix**: Clamped `wg_size_subgroup` and `wg_size_subgroup16` to `maxComputeWorkGroupInvocations / 6`.
    - *Failure 2 (Wave64 Redundant Control)*: Supplying `RequiredSubgroupSizeCreateInfoEXT` on fixed Wave64 hardware caused `VK_ERROR_UNKNOWN`. **Fix**: Set `force_subgroup_size = 0` when `min == max`.
    - *Failure 3 (FP16 Shared Memory Reduction)*: Driver shader compiler failed on `subgroupAdd(f16vec2)`. **Fix**: Switched dequantization reduction mode on Adreno (`vendor_id == 0x5143`) to `SHADER_REDUCTION_MODE_SHMEM`.
12. **Stage V10 Final Verification (`VERIFIED`)**: Executed `track_b_v10_matmul` (`mul_mat` FP32 32x32, 1024 elements, 0 mismatches, max error 3.757e-4, Process RC=0).
13. **Stage V11 - Full SDXS Vulkan Inference (`VERIFIED`)**:
    - Executed `sd-cli` with SDXS 512 Tiny SD Distilled Q8_0, 256x256, 1-step Euler A, seed 42.
    - Memory allocation: `VRAM 651.92 MB, RAM 0.00 MB`.
    - Timing: Conditioning 1.22s, Sampling 2.22s, VAE decode 0.94s, Total generation time 4.39s (Process RC=0).
    - Deterministic PNG SHA-256: `5fc44f5ec199d3137eaaf211859cb4e90759a060b8d4f53e0c605a394a612484`.
14. **Python CLI Integration**: Patched `termux_diffusion/hardware.py` to remove unsupported `-ngl` parameter; generated PNG via `termux-diffusion generate` in 7.20s (PNG SHA-256 `9084f819...`).
15. **Binary Identity & Packaging Integrity**:
    - Bound `V11_ORIGINAL_BINARY_SHA256` == `REPRODUCED_BINARY_SHA256` == `TARBALL_BINARY_SHA256` == `STAGING_BINARY_SHA256` (`efce9303...`).
    - Verified distinct from CPU Optimized binary (`2e247726...`).
16. **Staging Validation & Rollback**:
    - Extracted tarball to staging directory on S25; verified `v10-self-test` (RC=0) and `sd-cli-vulkan` (4.44s, deterministic PNG match).
    - Verified active CPU engine untouched and failure injection recovery working.
17. **Release Hygiene & History Clean**:
    - Untracked 67.7MB tarball and binaries from Git repository; cleaned Git commit history.
    - Restored authentic PyPI v1.3.0 public key in registry; removed temporary invalid signatures.

---

## 4. Source Provenance

- **Git Branch**: `validation/galaxy-s25`
- **Superproject Commit**: `0d68798244d1a44275a23f78f41c383f505a5449`
- **Submodule `stable-diffusion.cpp` Commit**: `50d640568388f876b0d63ee6ddb6bc86d997ec64`
- **Submodule `ggml` Commit**: `30bf8685ed4eb0a47f2b06229543327749904150`
- **Toolchain**: Android NDK r26b (`26.1.10909125`) Clang++ 17.0.2
- **Target Triple**: `aarch64-none-linux-android28`
- **Compilation Flags**: `-O3 -fPIE -std=gnu++17 -DANDROID -DGGML_USE_VULKAN -DGGML_MAX_NAME=160`
- **Linker Flags**: `-pie -lvulkan -ldl -lm -llog -landroid`

---

## 5. Patch Inventory

### Patch 1: `patches/0001-adreno-vulkan-pipeline-fixes.patch`
- **SHA-256**: `e307231ec5fb6dc97abc04b7e7f96ac01a21467d7970859069290fb4f093a66b`
- **Target File**: `gpu-probe-suite/v10-cmake/ggml-vulkan.cpp` (and `ggml/src/ggml-vulkan.cpp`)
- **Changes**: Workgroup invocation clamping to 1024, bypass redundant subgroup sizing on Wave64, SHMEM reduction fallback for Adreno FP16 dequantization.
- **Runtime Impact**: Resolves SPIR-V pipeline compilation crashes and kernel aborts on Qualcomm Adreno 830.

### Patch 2: `patches/0002-fix-sd-cli-hardware-gpu-args.patch`
- **SHA-256**: `453eee34c56d028777b32a209906f8da98c164281483b416f36ed4e8cfd23e73`
- **Target File**: `termux_diffusion/hardware.py`
- **Changes**: Removes unsupported `-ngl` parameter when invoking `sd-cli`; appends `["--offload-to-cpu"]` only when CPU is explicitly targeted.
- **Runtime Impact**: Enables Python CLI to invoke Vulkan `sd-cli` without argument rejection.

---

## 6. Binary Identity & Integrity Binding

- **Vulkan sd-cli Executable**: `efce9303c59aa7001845d4823e7cb1750f42eb7f61ccfb44e52f1b37401e4b53`
- **CPU Optimized sd-cli Executable**: `2e247726ef24f6539db83378e9d4fd97989f74fe3d322a7f8135fa7b8f03c06d`
- **Binary Distinction**: `CPU_OPTIMIZED_EQUALS_VULKAN_BINARY = FALSE`
- **V10 Self-Test Executable**: `def8b6ab6696c3d63a71fafdb18e3f72836181dc3713fbe0a0eb3df04f9b918f`
- **Hash Binding Verification**:
  `Original Binary == Reproduced Binary == Tarball Binary == Staging Binary == efce9303...`

---

## 7. Stage V10 Evidence (GGML Vulkan MatMul)

- **Operation**: `mul_mat`
- **Data Type**: FP32
- **Matrix Dimensions**: 32x32 (M=32, K=32, N=32)
- **Element Count**: 1024
- **Backend / Device**: Vulkan / `Qualcomm Adreno (TM) 830`
- **CPU Fallback**: `FALSE`
- **Graph Compute Status**: `PASS`
- **Mismatch Count**: `0` (Tolerance: 1.0e-3)
- **Max Absolute Error**: 3.757477e-04
- **Mean Absolute Error**: 1.585786e-04
- **NaN / Inf Count**: 0 / 0
- **Process Exit Code**: 0 (`PASS_V10_ADRENO_GGML_MATMUL_SUCCESSFUL`)

---

## 8. Stage V11 Evidence (SDXS Vulkan Model Inference)

- **Model**: SDXS 512 Tiny SD Distilled Q8_0 (`sdxs-512-tinySDdistilled_Q8_0.gguf`)
- **Resolution**: 256x256
- **Steps / Seed / CFG**: 1 step / 42 / 1.0 (Euler A)
- **Model Allocation**: VRAM 651.92 MB, RAM 0.00 MB
- **Direct C++ Latencies**:
  - Text Conditioning: 1.22s
  - UNet Sampling: 2.22s (2.21 s/it)
  - VAE Decode: 0.94s
  - Total Generation: 4.39s (Process RC=0)
- **Direct Output PNG**: `outputs/track-b-v11-sdxs-adreno830.png` (SHA-256 `5fc44f5ec199d3137eaaf211859cb4e90759a060b8d4f53e0c605a394a612484`, Mean 158.59, Std 100.62)
- **Python CLI Latencies**: Total generation 7.20s (Process RC=0, PNG SHA-256 `9084f819...`)
- **Strict All-Tensor Vulkan Status**: `PENDING_FALLBACK_AUDIT` (VRAM 651.92MB allocation verified; per-operator fallback counter audit reserved).

---

## 9. Experimental Package Candidate

- **Package Filename**: `termux-diffusion-vulkan-prebuilt-v1.3.1-android-arm64-adreno.tar.gz`
- **Package Size**: `67,754,500 bytes`
- **Package SHA-256**: `d1f0a2656a33d0929cfd3335e01feeabf9c3a1e34a0ae0eacc04ddb3701ece92`
- **Tarball Internal Structure**:
  ```
  bin/
  ├── sd-cli-vulkan
  └── v10-self-test
  lib/
  ├── libc++_shared.so
  └── libomp.so
  share/termux-diffusion/
  ├── backend-profile.json
  ├── build-metadata.json
  ├── patch-metadata.json
  ├── v10-self-test-profile.json
  └── v11-smoke-test-profile.json
  ```
- **Staging Test Results**:
  - `v10-self-test` executed in staging: `PASS` (RC=0, 0 mismatches).
  - `sd-cli-vulkan` executed in staging: `PASS` (RC=0, 4.44s, deterministic PNG SHA-256 match).
  - Active CPU engine untouched (`ACTIVE_CPU_UNCHANGED=TRUE`).
  - Automatic rollback on corrupted binary verified (`AUTOMATIC_ROLLBACK_VERIFIED=TRUE`).

---

## 10. Signing State & Protocol

- **Key ID**: `release-key-2026-01`
- **Public Key Registry Status**: Restored to authentic PyPI v1.3.0 key (`ea58ee6d830ca51164a3968c38e4abbad7fe39ebb761164821cba00524c15721`).
- **Signature Status**: `PENDING_OFFLINE_ROOT_SIGNING` (No ephemeral/fake signatures in repo).
- **Offline Root Signing Procedure**:
  1. Transfer `manifest-v1.3.1-vulkan-experimental.json` to secure signing station.
  2. Sign exact UTF-8 bytes using Ed25519 private key corresponding to `release-key-2026-01`.
  3. Output exact 64-byte signature `manifest-v1.3.1-vulkan-experimental.json.sig`.
  4. Verify against public key hex `ea58ee6d...`.
- **Four Release Assets for GitHub Pre-release**:
  1. `termux-diffusion-vulkan-prebuilt-v1.3.1-android-arm64-adreno.tar.gz`
  2. `manifest-v1.3.1-vulkan-experimental.json`
  3. `manifest-v1.3.1-vulkan-experimental.json.sig`
  4. `SHA256SUMS`

---

## 11. Current Limitations

1. **Strict Tensor Fallback Audit**: Pending kernel-level trace to verify zero fallback ops during sampling.
2. **Public Unmodified v1.3.0 Package**: Public v1.3.0 PyPI wheel requires the CLI argument patch in `v1.3.1`.
3. **Hardware Scope**: Verified on Galaxy S25 (`SM-S931N`, Adreno 830); Snapdragon 8 Gen 1/2/3 (Adreno 730/740/750) pending separate qualification.
4. **Resolution Scope**: Verified at 256x256 1-step; higher resolutions (512x512, 1024x1024) not yet profiled.

---

## 12. Release Manager Next Actions

1. `git pull --ff-only origin validation/galaxy-s25`.
2. Review this handover document and `release-handover/galaxy-s25-adreno-vulkan.json`.
3. Verify local tarball (`67,754,500 bytes`, SHA-256 `d1f0a265...`).
4. Perform offline Ed25519 signing of `dist_vulkan/manifest-v1.3.1-vulkan-experimental.json`.
5. Verify signature with `release-key-2026-01` public key.
6. Create GitHub Pre-release:
   - **Tag**: `v1.3.1-vulkan-experimental`
   - **Title**: `termux-diffusion v1.3.1 Experimental Vulkan for Adreno`
   - **Pre-release**: `true`
7. Upload the 4 Release Assets.
8. Perform public URL download & verification test on clean S25 Termux environment.
9. Verify Stage V10 Self-Test and Stage V11 Smoke Test pass via remote URL.
10. Integrate `--backend auto` detection in `termux_diffusion/installer.py`.
11. Bump package version to `1.3.1` in `pyproject.toml` and `_version.py`.
12. Request final user publication approval.

---

## 13. Proposed Versioning

- **CPU Stable**: `v1.3.0` (Default safe fallback on all devices).
- **Vulkan Experimental**: `v1.3.1-vulkan-experimental` (Pre-release gated by hardware probe).
- **Architecture**: PyPI wheel serves as lightweight client/gateway; large binary engine downloaded dynamically from GitHub Release Assets based on SoC profile.

---

## 14. Installer Integration Contract

Target user workflow:
```bash
termux-diffusion-install --backend auto
```
Execution lifecycle:
1. Detect SoC (`sun` / `Adreno 830`) and Vulkan support (`/system/lib64/libvulkan.so`).
2. Download signed manifest and verify Ed25519 signature.
3. Download prebuilt tarball and verify SHA-256 checksum.
4. Safely extract to staging cache `~/.cache/termux-diffusion/staging/`.
5. Execute `v10-self-test` (GGML FP32 MatMul); verify RC=0 and error < 1e-3.
6. Execute `sd-cli-vulkan` 1-step smoke test; verify RC=0.
7. Atomically symlink to `~/.cache/termux-diffusion/bin/sd-cli`.
8. On failure at any step, automatically restore CPU engine.

---

## 15. Cross-Device Roadmap

- **Galaxy S25 (Snapdragon 8 Elite / Adreno 830)**: V0~V11 Verified, Candidate Ready.
- **Galaxy A35 (Exynos 1380 / Mali-G68)**: CPU Verified, Raw Vulkan V0~V9 Verified, V10/V11 Pending.
- **Galaxy S21 (Exynos 2100 / Mali-G78)**: Raw Vulkan Verified, V10/V11 Pending clean re-verification.
- **Galaxy S20 (Exynos 990 / Snapdragon 865)**: Device profile and V10/V11 Pending.

---

## 16. Exact Resume Commands

```bash
git clone https://github.com/uno-km/termux-diffusion.git
cd termux-diffusion
git fetch --all --prune
git switch validation/galaxy-s25
git pull --ff-only origin validation/galaxy-s25
git submodule sync --recursive
git submodule update --init --recursive
git status
git log -n 10 --oneline
```

Primary Handover Document:
- [`docs/handover/GALAXY_S25_ADRENO_VULKAN_RELEASE_HANDOVER.md`](file:///c:/Users/GAME/Desktop/uno-km/dev/termux-diffusion/docs/handover/GALAXY_S25_ADRENO_VULKAN_RELEASE_HANDOVER.md)

Machine-Readable Handover JSON:
- [`release-handover/galaxy-s25-adreno-vulkan.json`](file:///c:/Users/GAME/Desktop/uno-km/dev/termux-diffusion/release-handover/galaxy-s25-adreno-vulkan.json)

---

## 17. Release Manager Completion Criteria

```ini
SIGNATURE_VALID_WITH_EXISTING_RELEASE_KEY=TRUE
TRUST_CONTINUITY=PASS
GITHUB_PRERELEASE_CREATED=TRUE
RELEASE_ASSET_COUNT=4
PUBLIC_MANIFEST_DOWNLOAD=PASS
PUBLIC_SIGNATURE_VALID=TRUE
PUBLIC_PACKAGE_SHA256_MATCH=TRUE
PUBLIC_V10_SELF_TEST=PASS
PUBLIC_V11_SMOKE_TEST=PASS
ACTIVE_CPU_UNCHANGED=TRUE
AUTOMATIC_ROLLBACK_VERIFIED=TRUE
PUBLIC_EXPERIMENTAL_PACKAGE_E2E=VERIFIED
```
