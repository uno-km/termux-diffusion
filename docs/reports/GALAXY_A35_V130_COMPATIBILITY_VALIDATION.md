# Galaxy A35 termux-diffusion v1.3.0 Compatibility Validation

## 1. Executive Summary

| Validation Item | Status / Result | Target / Standard | Notes |
| :--- | :--- | :--- | :--- |
| **Target Device** | **Samsung Galaxy A35 5G** (`SM-A356N`) | Exynos 1380 / Mali-G68 MP5 | Korea Domestic Model |
| **Target Package** | `termux-diffusion v1.3.0` | PyPI & npm Public Channels | Dual-Engine Python & Node.js |
| **Baseline CPU Prebuilt** | **VALIDATED** | `sd-cli-arm64-v8a-cpu-baseline` | RC=0, Latency: 8.07s |
| **Optimized CPU Prebuilt** | **VALIDATED** | `sd-cli-arm64-v8.2a-dotprod-fp16` | RC=0, Latency: 4.08s (**1.98x Speedup**) |
| **Installer Auto-Selection** | **VALIDATED** | DotProd + FP16 Detection | Auto-selected Optimized artifact |
| **One-Touch Install** | **VALIDATED** | Prebuilt-Only (0 Compilations) | Instant provisioning |
| **Node.js / npm E2E SDK** | **VALIDATED** | `require('termux-diffusion')` | RC=0, Latency: 6.08s, Gallery Synced |
| **Mali-G68 GPU Vulkan** | **VERIFIED** | Track B V0 ~ V9 Probes | 10/10 Stages PASS (0 Mismatches) |
| **GGML / SDXS Vulkan** | **NOT TESTED** | Upstream GGML / SD Vulkan | Experimental track preserved |
| **Non-Destructive Integrity** | **PRESERVED** | Isolated `$HOME/tmp` staging | Existing installations unchanged |

---

## 2. Device Environment (Empirical Measurement)

All hardware, OS, and toolchain attributes were measured directly on the live Galaxy A35 device without simulation or extrapolation.

```json
{
  "DEVICE_MANUFACTURER": "samsung",
  "DEVICE_MODEL": "SM-A356N",
  "DEVICE_PRODUCT": "a35xks",
  "DEVICE_CODENAME": "a35x",
  "SOC_MODEL": "s5e8835",
  "BOARD_PLATFORM": "erd8835",
  "ANDROID_VERSION": "16",
  "ANDROID_API_LEVEL": "36",
  "ANDROID_BUILD_FINGERPRINT": "samsung/a35xks/a35x:16/BP4A.251205.006/A356NKSS9DZG1:user/release-keys",
  "KERNEL_VERSION": "5.15.189-android13-3-33470412",
  "UNAME_FULL": "Linux localhost 5.15.189-android13-3-33470412 #1 SMP PREEMPT Thu Jul 2 11:03:01 KST 2026 aarch64 Android",
  "ABI_LIST": "arm64-v8a,armeabi-v7a,armeabi",
  "PRIMARY_ABI": "arm64-v8a",
  "CPU_CORE_COUNT": 8,
  "CPU_CLUSTERS": "4x Cortex-A78 (2.4 GHz) + 4x Cortex-A55 (2.0 GHz)",
  "ONLINE_CPUS": "0-7",
  "RAM_TOTAL_MIB": 5425.82,
  "RAM_FREE_MIB": 527.86,
  "RAM_AVAILABLE_MIB": 2212.12,
  "STORAGE_FREE_MIB": 22528,
  "PREFIX": "/data/data/com.termux/files/usr",
  "TERMUX_USER": "u0_a30",
  "PYTHON_VERSION": "Python 3.13.13",
  "NODE_VERSION": "v25.8.2",
  "NPM_VERSION": "11.13.0"
}
```

---

## 3. Public Package Sources & Verification

Public channel availability and checksum audit for `termux-diffusion v1.3.0`:

* **Official Website**: [https://uno-km.vercel.app/lib/diffusion/](https://uno-km.vercel.app/lib/diffusion/) (Displays v1.3.0)
* **PyPI Release**: [https://pypi.org/project/termux-diffusion/](https://pypi.org/project/termux-diffusion/)
  * Latest Version: `1.3.0`
  * Wheel: `termux_diffusion-1.3.0-py3-none-any.whl` (53,495 bytes)
  * SHA-256: `9859553e6ee01c6c8a6251a71697e4c7c80fbed843d04d83b6da18b34d8eb5ee`
* **npm Release**: [https://www.npmjs.com/package/termux-diffusion](https://www.npmjs.com/package/termux-diffusion)
  * Latest Version: `1.3.0`
  * Tarball: `termux-diffusion-1.3.0.tgz` (25,379 bytes)
  * SHA-256: `85712c80ecbf6f51faf160d02391db65b1d78bd4b19094cd636b326f9d89bf31`
* **GitHub Repository**: [https://github.com/uno-km/termux-diffusion](https://github.com/uno-km/termux-diffusion)
  * Latest Git Tag: `v1.3.0`

### Package Security Audit
* `WHEEL_PRIVATE_KEY_PRESENT`: **FALSE** (Clean)
* `WHEEL_NATIVE_BINARY_PRESENT`: **FALSE** (Pure bootstrap packaging)
* `WHEEL_MODEL_PRESENT`: **FALSE** (External on-demand streaming)
* `NPM_PRIVATE_KEY_PRESENT`: **FALSE** (Clean)
* `NPM_NATIVE_BINARY_PRESENT`: **FALSE** (Pure bootstrap packaging)

---

## 4. Artifact Integrity & Ed25519 Signature

The release manifest `manifest-v1.3.0-dual.json` was cryptographically verified against its detached signature `manifest-v1.3.0-dual.json.sig` using the public key embedded within the PyPI wheel (`release-key-2026-01`).

* **Signing Key ID**: `release-key-2026-01`
* **Public Key Hex**: `ea58ee6d830ca51164a3968c38e4abbad7fe39ebb761164821cba00524c15721`
* **Algorithm**: Ed25519 (RFC 8032)
* **Signature File Bytes**: 64 bytes
* **Signature Validity**: **VALID** (`cryptography.hazmat.primitives.asymmetric.ed25519`)
* **Minimum OS API Compatibility**: Required $\ge 26$, Galaxy A35 API Level is `36` (**COMPATIBLE**)

### Staged Artifact Checksums

| Artifact | File Size | SHA-256 Checksum |
| :--- | :--- | :--- |
| `manifest-v1.3.0-dual.json` | 1,752 B | `d609dc4db9f282d34da43c2258b56714062473a42e2d41ea25faf85eda190239` |
| `manifest-v1.3.0-dual.json.sig` | 64 B | `2b28647ad27218b8ee35f9f815c8b7fbb9b488aa81f45994c4512ea5448f9c2b` |
| `termux-diffusion-prebuilt-v1.3.0-arm64-v8a-cpu-baseline.tar.gz` | 44,242,538 B | `f224d1988e2970aad6e557e9463eaa9d65ffce4db06cab5725f72dacf4b260be` |
| `termux-diffusion-prebuilt-v1.3.0-arm64-v8.2a-dotprod-fp16.tar.gz` | 44,290,906 B | `8299b02f1247f24e450201a8f3ce24499a23adc19fae607b1716b5c78046abad` |

---

## 5. CPU Capability & ISA Verification

CPU instruction set features probed via `/proc/cpuinfo` and native Android kernel `getauxval(AT_HWCAP / AT_HWCAP2)`:

```json
{
  "AARCH64": true,
  "ARMV8_2_A": true,
  "NEON": true,
  "FP16_SCALAR": true,
  "FP16_VECTOR": true,
  "ASIMDHP": true,
  "DOTPROD": true,
  "ASIMDDP": true,
  "I8MM": false,
  "SVE": false,
  "SVE2": false,
  "HWCAP_HEX": "0x119fff",
  "HWCAP2_HEX": "0x0",
  "EXPECTED_ARTIFACT": "sd-cli-arm64-v8.2a-dotprod-fp16"
}
```

* **ISA Decision**: Because `AARCH64=TRUE`, `ARMV8_2_A=TRUE`, `DOTPROD=TRUE`, and `FP16_VECTOR=TRUE` are all satisfied by the Exynos 1380 Cortex-A78 cores, the optimal artifact is `sd-cli-arm64-v8.2a-dotprod-fp16`.

---

## 6. Baseline CPU Prebuilt Validation

Executed in isolated directory `$HOME/tmp/termux-diffusion-a35-v130-validation/baseline`:

* **CLI `--help` Self-Test**: `RC=0` (Passed, 0 dynamic link errors)
* **Shared Libraries**: `libc++_shared.so`, `libomp.so` bundled and loaded from `$INSTALL_DIR/lib`
* **SDXS Smoke Inference**:
  * Model: `sdxs-512-tinySDdistilled_Q8_0.gguf` (651.92 MB, GGUF)
  * Resolution: `256x256`, Steps: `1`, Seed: `42`, Sampler: `Euler A`, CFG: `1.0`
  * Return Code: `0`
  * Conditioning Latency: `0.42 s`
  * Sampling Latency: `4.98 s`
  * VAE Latency: `2.67 s`
  * **Total Latency: 8.07 s**
  * Output Image: `a35-baseline-sdxs.png` (256×256 PNG, 134,274 bytes, SHA-256 `89778237b79e7dec101d542e90fa590413f341f6e7bbca7f74a464242639e407`)

---

## 7. Optimized CPU Prebuilt Validation

Executed in isolated directory `$HOME/tmp/termux-diffusion-a35-v130-validation/optimized`:

* **CLI `--help` Self-Test**: `RC=0` (Passed, SIGILL=FALSE, SIGSEGV=FALSE)
* **SDXS Smoke Inference**:
  * Model: `sdxs-512-tinySDdistilled_Q8_0.gguf` (Identical weights)
  * Resolution: `256x256`, Steps: `1`, Seed: `42`, Sampler: `Euler A`, CFG: `1.0`
  * Return Code: `0`
  * Conditioning Latency: `0.60 s`
  * Sampling Latency: `2.33 s`
  * VAE Latency: `1.15 s`
  * **Total Latency: 4.08 s**
  * Output Image: `a35-optimized-sdxs.png` (256×256 PNG, 133,697 bytes, SHA-256 `a747ab877132e064f21b2fb07225c5d3036702309ea7789a5c59f972514a8c3a`)

---

## 8. Performance Comparison: Baseline vs. Optimized

| Execution Phase | Baseline (`arm64-v8a`) | Optimized (`armv8.2a+dotprod+fp16`) | Speedup Factor |
| :--- | :---: | :---: | :---: |
| **Conditioning (Text Encoder)** | 0.42 s | 0.60 s | 0.70x |
| **UNet Sampling (1 step)** | 4.98 s | 2.33 s | **2.14x** |
| **VAE Decode (TAE)** | 2.67 s | 1.15 s | **2.32x** |
| **Total End-to-End Latency** | **8.07 s** | **4.08 s** | **1.98x (~2.0x)** |

> [!TIP]
> Hardware DotProd and FP16 vector instructions cut UNet sampling time by **53.2%** (from 4.98s down to 2.33s) and VAE decode time by **56.9%** (from 2.67s down to 1.15s) on the Exynos 1380 architecture.

---

## 9. One-Touch Installer & Process Compilation Audit

### Python Installer Auto-Selection
Tested inside an isolated Python virtualenv (`$ISODIR/staging/venv`):
* Installer capability detection identified `dotprod=True` and `fp16=True`.
* Selected Artifact: `sd-cli-arm64-v8.2a-dotprod-fp16`
* Selection Match: **TRUE** (100% matched expected artifact)

### Node.js / npm End-to-End SDK Validation
Tested inside an isolated npm project (`$ISODIR/staging/node_test`):
* Installed `termux-diffusion-1.3.0.tgz` via npm in 753ms.
* Executed programmatic Node.js generation via `const { generate } = require('termux-diffusion')`.
* Return Code: `0`
* Rendering Time: `6.087 s` (Total elapsed: `7.30 s`)
* Output image: `a35-node-sdxs.png` (256×256 PNG, 133,697 bytes, SHA-256 `a747ab877132e064f21b2fb07225c5d3036702309ea7789a5c59f972514a8c3a`)
* Auto-sync to Samsung Gallery: `/storage/pictures/TermuxDiffusion/a35-node-sdxs.png` (**PASSED**)

### Compilation Process Audit
* **termux-diffusion Installation & Image Generation**: **0 on-device compilations** (`make=0`, `cmake=0`, `ninja=0`, `clang=0`, `gcc=0`). Pure prebuilt instant provisioning.
* **Vulkan V0 ~ V9 GPU Probes**: Reused prebuilt NDK ELF64 binaries cross-compiled for Android ARM64 Bionic + SPIR-V bytecode generated via `glslangValidator`.

---

## 10. Mali-G68 GPU Vulkan Compute Probe (Track B V0 ~ V9)

Validation of the Mali-G68 MP5 integrated GPU using direct Vulkan API invocation via Android system loader `/system/lib64/libvulkan.so`:

| Probe Stage | Target Operation | Status | Output Details |
| :--- | :--- | :---: | :--- |
| **V0** | Android System Vulkan Loader `dlopen` | **PASS** | `libvulkan.so` loaded successfully at valid pointer |
| **V1** | Vulkan Instance Creation (`vkCreateInstance`) | **PASS** | API version: 1.1.0 requested, Instance created |
| **V2** | Physical Device Enumeration | **PASS** | Device count: 1 physical device discovered |
| **V3** | Mali Hardware GPU Selection | **PASS** | Detected: `Mali-G68` (Vendor: `0x13B5`, DevID: `0x92041010`, API: `1.3.219`, Driver: `0x09801000`) |
| **V4** | Compute Queue Family Discovery | **PASS** | Compute-capable queue family identified at Queue Index 0 |
| **V5** | Logical Device & Queue Creation | **PASS** | `vkCreateDevice` succeeded with compute queue |
| **V6** | 64 KiB Storage Buffer Allocation & Host Map | **PASS** | Memory allocated and host-visible mapped |
| **V7** | SPIR-V Compute Pipeline Creation | **PASS** | Shader module & compute pipeline built |
| **V8** | GPU Dispatch Execution | **PASS** | Command buffer recorded and dispatched (4 workgroups × 64 = 256 invocations) |
| **V9** | Verification & Checksum | **PASS** | Element count: 256, Expected checksum: `65536`, Actual checksum: `65536`, Mismatch count: **0** |

```
RESULT=PASS_V7_V8_V9_MALI_COMPUTE_DISPATCH_SUCCESSFUL
A35_MALI_G68_VULKAN_COMPUTE=VERIFIED
```

---

## 11. Shared vs. Device-Specific Assets

* **Shared Universal Assets (Reusable across Galaxy S21, Galaxy A35, and broad ARM64 devices)**:
  * Signed Optimized Tarball: `sd-cli-arm64-v8.2a-dotprod-fp16.tar.gz`
    * *Product Description*: **Android ARM64 ARMv8.2-A DotProd FP16 Optimized (Validated on Galaxy S21 and Galaxy A35)**
  * Signed Baseline Tarball: `sd-cli-arm64-v8a-cpu-baseline.tar.gz`
    * *Product Description*: **Android ARM64 CPU Baseline (Broad-Compatibility Candidate)**
  * Manifest & Ed25519 signature: `manifest-v1.3.0-dual.json` / `.sig`
  * PyPI wheel & npm package: `termux-diffusion 1.3.0`
* **Device-Specific Ground Truth Measurements**:
  * A35 Latency: Baseline 8.07s / Optimized 4.08s
  * A35 GPU Hardware ID: `0x92041010` (Mali-G68 MP5, Vulkan 1.3.219)
  * S21 GPU Hardware ID: *See S21 V3 raw device-enumeration evidence: `0x92020010` (Mali-G78 MP14)*

---

## 12. Final Compatibility Decision Matrix

```ini
A35_BASELINE_PREBUILT=VALIDATED
A35_OPTIMIZED_PREBUILT=VALIDATED
A35_ONE_TOUCH_INSTALLER=VALIDATED
A35_NODE_SDK_GENERATION=VALIDATED
A35_CPU_PRODUCT_SUPPORT=VALIDATED
A35_MALI_G68_VULKAN_COMPUTE=VERIFIED
A35_GGML_VULKAN_MATMUL=NOT_TESTED
A35_VULKAN_SDXS=NOT_TESTED
A35_VULKAN_GPU_SUPPORT=EXPERIMENTAL_READY
DEFAULT_ARTIFACT=sd-cli-arm64-v8.2a-dotprod-fp16
```

---

## 13. End-User Installation & Execution Guide

Galaxy A35 users can install and run `termux-diffusion` in 2 clean steps without any compilation tools:

### Python Runtime
```bash
# 1. Install package from PyPI
pip install termux-diffusion

# 2. Generate image (Prebuilt engine automatically provisions and generates in ~4s)
termux-diffusion generate "a small red robot on a wooden workbench, photorealistic" -m sdxs
```

### Node.js / TypeScript Runtime
```bash
# 1. Install CLI from npm
npm install -g termux-diffusion

# 2. Run instant generation
npx termux-diffusion generate "a small red robot on a wooden workbench, photorealistic" -m sdxs
```

Generated images are automatically indexed and saved to **Samsung Gallery / Google Photos**.

---

## 14. Known Limitations & Future Work

1. **Vulkan End-to-End Inference (Track B V10 / V11)**: While V0~V9 compute pipeline execution on Mali-G68 is verified (0 mismatches), full GGML MatMul and SDXS Vulkan pipelines are preserved as experimental tracks pending future upstream optimization.
2. **Memory Footprint**: Total memory consumption during 256x256 SDXS generation is ~652 MB, fitting comfortably within the 6 GB RAM budget of Galaxy A35 with zero Out-Of-Memory (OOM) events.
3. **Security Posture**: Galaxy A35 host verification is strictly enforced via `known_hosts` and `paramiko.RejectPolicy()`, with Ed25519 key-based SSH authentication.
