# Changelog

All notable changes to 	ermux-diffusion will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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