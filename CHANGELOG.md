# Changelog

All notable changes to termux-diffusion will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.7.0] - 2026-09-23

### Added & Resolved
- **Qualcomm Snapdragon 8 Elite (Adreno 830) Vulkan Numerical Distortion Ground-Truth Fix**:
  - **Shader Direct Byte Indexing**: Fixed Qualcomm Adreno 830 SPIR-V JIT compiler byte-lane swap defect in Q8_0 dequantization. Implemented `unpack8_to_vec4` helper in `types.glsl` and replaced `data_a_packed16` with direct 8-bit integer indexing (`data_a[ib].qs[4*iqs + ...]`) across `dequant_funcs.glsl` and `mul_mm_funcs.glsl`.
  - **Register Spill Elimination**: Purged `[[unroll]]` pragma from `soft_max.comp` preventing on-chip register file exhaustion on Adreno 830 architecture.
  - **FP32 Accumulator (`f32acc`) Enforcement**: Enforced FP32 accumulator for Qualcomm GPUs in `ggml-vulkan.cpp` (`ggml_vk_get_mul_mat_mat_pipeline`), completely eradicating FP16 accumulator overflow/underflow while maintaining maximum compute throughput (13.6s for 2-step 512x512 SDXS generation).
  - **Pure Vulkan Verification**: 100% verified on physical Galaxy S25 device without CPU fallback (`clip=vulkan0,diffusion=vulkan0,vae=vulkan0`), producing crystal-clear photographic fidelity.
- **Unified Engine Architecture & Zero-Silent-Fallback Hardening**:
  - **`engine.py` Extraction**: Modularized `DiffusionEngine`, `DiffusionRuntime`, `load()`, and `get_binary_path()` with strict backend-to-binary mapping (`gpu`/`vulkan` -> `sd-cli-vulkan`, `cpu` -> `sd-cli-cpu`/`sd-cli`).
  - **`doctor.py` Extraction**: Decoupled pre-flight environment diagnostics into dedicated diagnostic doctor.
  - **Android Bionic Linker Isolation**: Filtered Termux `$PREFIX/lib` from `LD_LIBRARY_PATH` during Vulkan dispatch, eradicating libc++ ABI symbol collisions with Android system drivers (`/system/lib64/libvulkan.so`, `libunwindstack.so`).
- **Universal Mobile Vulkan Support & BDA Null Pointer Crash Elimination (Mali-G78 & Adreno 650)**:
  - **Buffer Device Address (BDA) Null Guard**: Identified and eliminated root cause of `SIGSEGV (Return Code -11, SEGV_MAPERR, pc 0x0)` crash at offset `0x063d8764` during UNet dispatch on ARM Mali-G78 (Galaxy S21) and Adreno 650 (Galaxy S20). Enforced `device->buffer_device_address = false` on mobile Android Bionic runtimes, eradicating unhandled null function pointer calls to `device.getBufferAddress()` and smoothly routing to robust, leak-free `VkDescriptorSet` UMA bindings.
  - **Galaxy S21 Physical Verification**: Verified pure 100% Vulkan GPU inference (`sdxs.gguf`) on physical Galaxy S21 (Mali-G78), generating verified image artifact in 22.00s without CPU fallback.
  - **Unblocked Adreno 650**: Purged legacy artificial hardware block in `hardware.py`, restoring native Vulkan GPU execution capability for Snapdragon 865 devices.
- **Official Assetization**:
  - Packaged and pinned canonical ARM64 Bionic release binary `releases/sd-cli-vulkan-v2.7.2-android-arm64.tar.gz` with cryptographic SHA-256 verification (`4e96bdc40d0272b392e4eace8938f71cb30319e01bd19d406759b2595c622fb9`).
  - Archived complete source patch at `patches/0001-qualcomm-adreno830-fp32acc-dequant-unroll-fix.patch`.

## [1.6.9] - 2026-09-18

### Changed & Hardened
- **Zero-Hardcoding Dynamic Latest-First Provisioning Architecture**:
  - Completely purged hardcoded fallback version strings (`v1.6.8`) from `index.js`.
  - Implemented dynamic `package.json` version introspection (`pkgVer`) with prioritized `releases/latest/download/` canonical endpoints for both CPU binary (`sd-cli-cpu-android-arm64.tar.gz`) and companion library (`libomp-android-arm64.so`).
  - Prioritized Tier 2 latest download endpoint in Python `installer.py` candidate generator.
  - Synchronized versions across `package.json`, `pyproject.toml`, `setup.py`, and `_version.py` to `1.6.9`.

## [1.6.3] - 2026-09-07

### Added
- **Fast-Track Prebuilt Stream Extractor**: Node.js `provisionEngine()` in `index.js` now automatically streams and extracts precompiled ARM64 Bionic binaries (`sd-cli-vulkan`) and system shims (`libegl_shim.so`, `libomp.so`) in ~3 seconds from GitHub Releases, bypassing 20-minute on-device C++ compilation and preventing compilation OOMs.
- **Dynamic SSOT Release Endpoints**: Eliminated legacy hardcoded `v1.3.1-vulkan-experimental` URLs from `installer.py`. Implemented dynamic candidate resolution via `TERMUX_DIFFUSION_RELEASE_TAG`, `v{__version__}`, and `/releases/latest/download`.
- **Dynamic CLI Version SSOT**: CLI help output and banner now dynamically query `package.json` version.
- **Companion Shims Deployment**: Companion libraries (`libegl_shim.so`, `libomp.so`) are automatically deployed into `~/.cache/termux-diffusion/lib` and `~/.local/lib` upon engine installation.

---

## [1.5.3] - 2026-09-07

### Added
- **Adreno GPU Compute Check Bypass**: Embedded `GGML_VULKAN_SKIP_CHECKS="999999999"` default in execution environment, eliminating host-side debug CPU overhead on Qualcomm Adreno devices.
- **Multi-Engine Vulkan Targeting**: Enforced `--backend clip=vulkan0,diffusion=vulkan0,vae=vulkan0` for Vulkan/GPU modes ensuring rock-solid execution and preventing pipeline crashes.
- **Distilled Guidance Parameter (`-g` / `--guidance`)**: Added CLI and programmatic support for distilled CFG guidance (e.g. 3.5 for SDXS/Turbo).
- **Optimized Mobile Presets**: Updated `sdxs` and `turbo` presets with default 2 steps and 3.5 guidance.

---

## [1.5.2] - 2026-09-07

### Added
- **13-Section Production Documentation Overhaul**: Completely overhauled `README.md` and `README.pypi.md` with exhaustive English technical specifications, GPU activation commands, parameter matrix, real-world sample galleries, and physical device benchmarks.
- **Physical Device Telemetry & Benchmarks**: Added verified execution benchmarks across Galaxy S25 (Snapdragon 8 Elite), S21 (Exynos 2100), S20 5G (Snapdragon 865), and A35 (Exynos 1380).
- **24/7 Unattended Background Guide**: Documented complete 3-tier hardening procedure (Termux WakeLock -> Android OS Unrestricted Battery -> ADB Phantom Process Killer & LMK -1000 priority lock).
- **Comprehensive Discoverability Index**: Expanded SEO and technical taxonomy keywords across `pyproject.toml`, `package.json`, and official documentation manifests.

## [1.5.1] - 2026-09-07

### Changed
- Streamlined repository architecture: purged legacy scratch folders, internal handovers, and device test logs to official AMEVA Foundation archives.
- Standardized CI/CD release workflow with idempotent PyPI and NPM dual distribution.

---

## [1.5.0] - 2026-09-07

### Added
- Integrated unified `DiffusionAdapter` directly from `ameva_runtime.adapters` SSOT.
- Enforced strict E001/E003 Fail-Fast on explicit Vulkan requests without silent CPU fallback.
- Standardized English diagnostic messages and error logging.

---

## [1.4.5] - 2026-09-05

### Changed
- Aligned hardware doctor probes, selftest routines, and installation scripts with ameva-runtime.
- Standardized Vulkan HAL adapter integration with zero silent fallback.

---

## [1.4.4] - 2026-09-05

### Changed
- Migrated hardware acceleration dependency to unified `ameva-runtime>=2.0.0` and `@ameva/runtime>=2.0.0`.
- Standardized Vulkan HAL adapter integration with zero silent fallback in explicit GPU execution modes.

---

## [1.4.3] - 2026-09-04

### Added
- **Truthfulness Documentation Overhaul**: Replaced speculative GPU marketing claims with ground-truth device telemetry, highlighting native ARM64 ARMv8.2-A DotProd/FP16 SIMD vector execution (Cortex-A78 x4: 61s benchmark) and adaptive device resource routing.
- **AMEVA Component Protocol v1 Integration**: Added `DiffusionControl` and `DiffusionOrchestratorAdapter` (`BaseOrchestratorAdapter` compliant) for orchestrator pluggability, and wired `HeartbeatWriter` for real-time instance state tracking.
- **AMEVA CLI Subcommands**: Integrated `component`, `model`, and `instance` management commands directly into the unified CLI.

### Fixed
- **sd-cli Execution Crash Prevention**: Removed unsupported `--backend vulkan0` flag injection that caused immediate process exit (Exit Code 1) on C++ engine invocation.
- **Bionic Linker Isolation**: Removed `/system/lib64` and `/vendor/lib64` pollution from `LD_LIBRARY_PATH`, isolating to Termux native paths (`$PREFIX/lib`) to prevent Android 15 `SIGABRT` and EGL symbol collisions.
- **Process Locking & Hardware Introspection Truthfulness**: Resolved critical bug in `_is_pid_alive` where dead PIDs held file locks indefinitely, and hardened KGSL/NPU hardware discovery against deceptive fallbacks.
- **Pipe Resource Cleanup Safety**: Guarded `process.stdout.close()` with `hasattr` inspection to prevent attribute errors on mock and closed pipe objects.

### Verification
- **Unit Tests**: 62 / 62 Python unit tests passed and 12 / 12 Node.js unit tests passed.

---

## [1.3.2] - 2026-09-02

### Added
- **Android Bionic ICD Priority**: Prioritized Bionic Vulkan driver ICD path over Termux Mesa to eliminate SIGABRT crashes on Exynos/Snapdragon (Galaxy A35/S25/S21).
- **Official Installation Script**: Automated one-click environment setup via scripts/install.sh.

### Verification
- **Unit Tests**: 62 / 62 passed with 100% assertion coverage.