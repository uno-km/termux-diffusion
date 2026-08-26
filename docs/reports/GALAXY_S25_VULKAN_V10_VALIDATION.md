# Galaxy S25 GGML-Vulkan Stage V10 MatMul Validation Report

**Mission**: `GALAXY_S25_GGML_VULKAN_V10_VALIDATION`  
**Target Device**: Samsung Galaxy S25 (`SM-S931N`)  
**SoC Family**: Qualcomm Snapdragon 8 Elite (`sun`)  
**GPU Family**: Adreno  
**GPU Target / Device**: Adreno (TM) 830  
**Driver**: Qualcomm Technologies Inc. Adreno Vulkan Driver  
**Timestamp (UTC)**: `2026-08-26T01:35:35Z`  
**Result Verdict**: **`PASS_V10_ADRENO_GGML_MATMUL_SUCCESSFUL`**  

---

## 1. Executive Summary

Stage V10 evaluates the **upstream-compatible GGML-Vulkan** tensor execution on the **Samsung Galaxy S25 (Qualcomm Adreno 830)**. While testing on the Galaxy S21 environment previously required loader alignment and dispatch adjustments, the Galaxy S25 Adreno 830 successfully executes the GGML-Vulkan FP32 matrix multiplication probe via the standard Termux Vulkan loader path without S21 Mali-specific runtime patches.

### Core Metrics Table

| Metric | Target / Specification | Measured Device Value | Status |
| :--- | :--- | :--- | :--- |
| **Target Device** | Samsung Galaxy S25 | `SM-S931N (sun)` | **CONFIRMED** |
| **GPU Hardware** | Qualcomm Adreno 830 | `Adreno (TM) 830` | **CONFIRMED** |
| **Vulkan Backend Enumeration** | $\ge 1$ physical device | `1 device detected` | **PASS** |
| **Backend Selection** | Pure Vulkan Backend | `backend = vulkan` | **PASS** |
| **CPU Fallback Activated** | Strictly `FALSE` | `V10_CPU_FALLBACK=FALSE` | **PASS** |
| **Tensor Operation** | `ggml_mul_mat` | `mul_mat (32x32 FP32)` | **PASS** |
| **Graph Allocation & Execution** | `ggml_backend_graph_compute` | `PASS` (`GGML_STATUS_SUCCESS`) | **PASS** |
| **Element Count** | 1,024 float32 | `1024` | **PASS** |
| **Numerical Mismatch Count** | 0 ($|\Delta| \le 10^{-3}$) | **`0`** | **PASS** |
| **Max Absolute Error ($L_\infty$)** | $< 1.0 \times 10^{-3}$ | **`3.757477e-04`** | **PASS** |
| **Mean Absolute Error ($L_1$)** | $< 5.0 \times 10^{-4}$ | **`1.585786e-04`** | **PASS** |
| **NaN / Inf Output Count** | 0 | `0 / 0` | **PASS** |
| **FP32 MatMul Correctness** | Numerical equivalence | **`VERIFIED`** | **PASS** |
| **FP16 Capability** | Driver capability | **`REPORTED (fp16: 1)`** | **INFO** |
| **FP16 MatMul Correctness** | Separate precision test | **`NOT TESTED`** | **N/A** |
| **Vulkan Driver Cleanup** | Clean deallocation | `PASS` | **PASS** |
| **Device Exit Code** | `0` | `0` | **PASS** |

---

## 2. Upstream Compatibility & Architecture Analysis

### 2.1 Upstream Compatibility Path
- On the tested Galaxy S21 environment, the Termux Vulkan path initially exposed llvmpipe rather than Mali-G78. Subsequent integration required Android system-loader alignment and device-dispatch compatibility work.
- On **Galaxy S25 (Snapdragon 8 Elite / Adreno 830)**:
  1. Standard Termux `libvulkan.so` loader directly enumerates `Adreno (TM) 830` without Mesa llvmpipe fallback.
  2. The upstream-compatible GGML-Vulkan pipeline executes cleanly without Mali-specific queue index workarounds or `/system/lib64` loader redirection.

### 2.2 Provenance & Source Hashes
- **Submodule Commit (`stable-diffusion.cpp`)**: `97d2990807fe6d558e395f8764198d7c7e7b411c`
- **GGML Commit**: `97d2990`
- **`ggml-vulkan.cpp` SHA256**: `c8ef996695578bef67cf1fe4457eda526a0d6d44143292d3a0ae4439daa79bae`
- **`ggml-vulkan-shaders.hpp` SHA256**: `063c5df028c696cdbb5720129e8e74f529a8240199de486f3d218ce940ae7f85`
- **`track_b_v10_matmul.cpp` SHA256**: `9cc69fc55bd1872ea0c539ff372393569416909b7063b1e3d93554a85cb3f8b5`

### 2.3 Adreno 830 Hardware Properties Exposed by GGML-Vulkan
```text
ggml_vulkan: Found 1 Vulkan devices:
ggml_vulkan: 0 = Adreno (TM) 830 (Qualcomm Technologies Inc. Adreno Vulkan Driver) |
             uma: 1 | fp16: 1 | bf16: 0 | fp4: 0 | warp size: 64 |
             shared memory: 32768 | int dot: 0 | matrix cores: none
```
- **Unified Memory Architecture (UMA)**: GGML reported UMA support (`uma: 1`). Actual copy behavior and performance require model-level profiling.
- **Subgroup / Warp Execution**: `warp size = 64` (Adreno Wave64 execution model).
- **Workgroup Shared Memory**: `32 KB` available per compute workgroup.
- **Precision Status**:
  - `FP16 capability`: **REPORTED** (`fp16: 1`)
  - `FP16 GGML MatMul correctness`: **NOT TESTED** (Reserved for precision-specific probes)
  - `FP32 GGML MatMul correctness`: **VERIFIED**

---

## 3. Verification Log & Numerical Sampling

```text
=== TRACK B V10 GGML-VULKAN TENSOR OPERATION PROBE (MATMUL 32x32 FP32) ===
V10_AVAILABLE_VK_DEVICES=1
[V10] VK Device #0: Adreno (TM) 830
V10_BACKEND_REQUESTED=vulkan
V10_BACKEND_SELECTED=vulkan
V10_DEVICE_NAME=Adreno (TM) 830
V10_CPU_FALLBACK=FALSE
V10_OPERATION=mul_mat
V10_MATRIX_SHAPE=32x32
V10_DATA_TYPE=FP32
V10_GRAPH_COMPUTE_RESULT=PASS
[V10] Sample [0] CPU=6.92 GPU=6.91962 delta=0.000375748
[V10] Sample [1] CPU=7.64 GPU=7.63996 delta=4.33922e-05
[V10] Sample [2] CPU=7.38 GPU=7.37972 delta=0.000282764
[V10] Sample [3] CPU=7.4 GPU=7.39993 delta=7.39098e-05
[V10] Sample [4] CPU=7.7 GPU=7.69973 delta=0.000268459
[V10] Sample [5] CPU=7.16 GPU=7.15985 delta=0.000151157
[V10] Sample [6] CPU=7.88 GPU=7.87986 delta=0.000136375
[V10] Sample [7] CPU=6.92 GPU=6.91962 delta=0.000375748
V10_ELEMENT_COUNT=1024
V10_MISMATCH_COUNT=0
V10_MAX_ABS_ERROR=3.757477e-04
V10_MEAN_ABS_ERROR=1.585786e-04
V10_NAN_COUNT=0
V10_INF_COUNT=0
V10_TOLERANCE=1.000000e-03
V10_CLEANUP_RESULT=PASS
PROCESS_RC=0
RESULT=PASS_V10_ADRENO_GGML_MATMUL_SUCCESSFUL
```

---

## 4. Evidence Artifacts

1. Evidence JSON: `validation/galaxy-s25/v10_evidence.json`
2. MatMul Source Code: `gpu-probe-suite/v10-cmake/track_b_v10_matmul.cpp`
3. Vulkan Backend Code: `gpu-probe-suite/v10-cmake/ggml-vulkan.cpp`
4. Generated Shader Header: `gpu-probe-suite/v10-cmake/ggml-vulkan-shaders.hpp`

---

## 5. Conclusion & Stage V11 Readiness

GGML-Vulkan FP32 tensor execution was verified on the Galaxy S25 Adreno 830 without CPU fallback.
- **Stage V0~V9 (Raw Vulkan Probes)**: `VERIFIED`
- **Stage V10 (GGML-Vulkan FP32 MatMul)**: `VERIFIED`
- **Stage V11 (SDXS Vulkan 256x256 1-Step Model Inference)**: **UNBLOCKED / READY TO PROCEED**
