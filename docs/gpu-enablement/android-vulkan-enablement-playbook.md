# 📘 Android Vendor GPU Enablement Playbook

## 📌 Architectural Principles

1. **Zero Firmware-Specific Hardcoding**:
   Never hardcode vendor driver library paths (e.g. `/vendor/lib64/hw/vulkan.exynos2100.so`) or SoC string matching (`device_name == "Mali-G78"`).
2. **Capability-Based Probing**:
   Select backend features based on runtime Vulkan API capabilities (`vkEnumeratePhysicalDevices`, `Vulkan API >= 1.1`, `shaderFloat16`, `subgroup` arithmetic).
3. **Environment Fingerprinting & OTA Resilience**:
   Save runtime fingerprint (`android_build_fingerprint`, `vulkan_driver_sha256`) in `state.json`. Re-validate via Native Self-Test automatically when OS or driver updates occur.
4. **Safety Fallback Hierarchy**:
   - **Primary Baseline**: High-Performance CPU Backend (100% universal stability across all Android devices).
   - **Accelerated Option**: Standard Vulkan GPU Backend (Activated ONLY when capability probe & self-test pass).
   - **Auto-Fallback**: Seamless fallback to CPU if Vulkan probe or dispatch fails.

---

## 🔬 Granular 12-Stage Validation Hierarchy (V0 – V11)

| Stage ID | Target Operation | Success Criteria |
| :--- | :--- | :--- |
| **V0** | `Vulkan Loader Open` | `dlopen("libvulkan.so")` succeeds |
| **V1** | `Instance Creation` | `vkCreateInstance()` returns `VK_SUCCESS` |
| **V2** | `Physical Device Enumeration` | `vkEnumeratePhysicalDevices()` returns >0 devices |
| **V3** | `Hardware GPU Device Selection` | Select device where `deviceType != eCpu` |
| **V4** | `Queue Family Probe` | Compute queue family identified |
| **V5** | `Logical Device Creation` | `vkCreateDevice()` succeeds with required extensions |
| **V6** | `Buffer Allocation` | Host/device visible memory allocated |
| **V7** | `Compute Pipeline Compilation` | SPIR-V compute shader pipeline created |
| **V8** | `Shader Dispatch Execution` | `vkCmdDispatch()` submitted and executed |
| **V9** | `Result Checksum Validation` | Output buffer matches expected calculation |
| **V10** | `ggml-vulkan Tensor Operations` | Matrix multiplication via `ggml-vulkan` backend |
| **V11** | `End-to-End Model Inference` | SDXS 256x256 image generated without fallback |

---
*Playbook Version: 1.0.0 | Maintainer: AMEVA Foundation*
