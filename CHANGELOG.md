# Changelog

All notable changes to 	ermux-diffusion will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.3.2] - 2026-09-02

### Added
- **Android Bionic ICD Priority**: Prioritized Bionic Vulkan driver ICD path over Termux Mesa to eliminate SIGABRT crashes on Exynos/Snapdragon (Galaxy A35/S25/S21).
- **Official Installation Script**: Automated one-click environment setup via scripts/install.sh.

### Verification
- **Unit Tests**: 62 / 62 passed with 100% assertion coverage.