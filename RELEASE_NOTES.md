# Release Notes - termux-diffusion v1.8.1

**Release Tag**: `v1.8.1`  
**Distribution Channels**: PyPI (`termux-diffusion`), NPM (`termux-diffusion`), GitHub Releases  
**Target Platform**: Android Termux (ARM64 / aarch64 Bionic)  
**License**: Apache-2.0  

---

## Highlights & Key Architectural Changes

### 1. Unified 5-Backend Standardization
- **Ecosystem Parameter Whitelist**: Aligned CLI options to standard 5-set `["auto", "gpu", "vulkan", "opencl", "cpu"]`.
- **Fail-Fast Policy**: Eliminates ambiguous or misleading parameter formats. Passing unsupported arguments halts immediately with strict diagnostics.

### 2. Zero-Regression Test Suite
- **Comprehensive Unit Testing**: Validated 86 test cases across diffusion pipeline, scheduler presets, prompt caching, and hardware detection (100% Green).
