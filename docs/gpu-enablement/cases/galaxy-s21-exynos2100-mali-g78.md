# 📱 Case Study: Samsung Galaxy S21 5G (Exynos 2100 / Mali-G78)

## 📌 System Snapshot

- **Device**: Samsung Galaxy S21 5G (SM-G991N)
- **SoC**: Exynos 2100
- **GPU**: ARM Mali-G78 MP14
- **OS**: Android 14 / One UI 6.0
- **Environment**: Termux user container (`u0_a328`)

---

## 🔬 Empirical Diagnostic Findings

1. **Termux Vulkan Loader Behavior**:
   - `vulkaninfo` in Termux user container exposes `GPU0: llvmpipe (Mesa CPU software rasterizer, PHYSICAL_DEVICE_TYPE_CPU)`.
2. **`ggml-vulkan.cpp` Device Filtering**:
   - Line 7566: `if (devices[i].getProperties().deviceType != vk::PhysicalDeviceType::eCpu)`
   - `ggml-vulkan` explicitly filters out `eCpu` Vulkan devices.
   - Output: `ggml_vulkan: No devices found.`
3. **Execution Resolution**:
   - Standard mode: Seamless fallback to high-performance CPU NEON execution (3.83s for 256x256 1-step).
   - Strict mode (`--strict-vulkan`): Returns `RC!=0` and blocks CPU fallback as designed.

---
*Case Study Date: 2026-08-25 | Status: Track B Baseline Documented*
