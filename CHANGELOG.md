# Changelog

All notable changes to termux-diffusion will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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