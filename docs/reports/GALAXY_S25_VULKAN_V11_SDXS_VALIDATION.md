# Galaxy S25 Stage V11: SDXS Vulkan 256x256 1-Step Hardware Validation & Identity Audit Report

## 1. Executive Status & Official Verdict

- **Device Model**: Samsung Galaxy S25 (`SM-S931N`)
- **SoC**: Qualcomm Snapdragon 8 Elite (`sun` / SM8750-AB)
- **GPU**: Qualcomm Adreno (TM) 830 (`vulkan.adreno.so` v0800.64.7)
- **SSH Host-Key Fingerprint**: `SHA256:4+dqpOrh2jItfsoVUMTJ1yh0Kxm4KYb/FCTse7xgwfY`

### Official Verification Judgments
- `S25_V0_V9_RAW_VULKAN=VERIFIED`
- `S25_V10_GGML_VULKAN_MATMUL=VERIFIED`
- `S25_V11_SDXS_VULKAN_INFERENCE=VERIFIED`
- `S25_OUTPUT_PNG=VERIFIED`
- `S25_STRICT_ALL_TENSOR_VULKAN=PENDING_FALLBACK_AUDIT`
- `PUBLIC_V130_UNMODIFIED_VULKAN_E2E=NOT_PROVEN`
- `LOCAL_VULKAN_CLI_INTEGRATION=VERIFIED`
- `PACKAGE_STATUS=VERIFIED_UNSIGNED_EXPERIMENTAL_CANDIDATE`
- `OFFLINE_ROOT_SIGNATURE=PENDING`
- `PUBLISH_READY=FALSE`
- `RESULT=SUCCESS_WITH_SECURITY_AND_PACKAGING_ACTIONS`

---

## 2. Security Notice: Action Required

> [!CAUTION]
> **SECURITY_ACTION_REQUIRED**:
> Plaintext SSH credentials were previously present in interactive test workflows.
> 1. All local scratch test files containing hardcoded credentials have been securely scrubbed and deleted.
> 2. The repository secret scan has completed with 0 secret leaks found in git history.
> 3. **The user must immediately update the Termux user password (`passwd`) on the Galaxy S25 device and disable password authentication in `sshd_config` (`PasswordAuthentication no`, `PubkeyAuthentication yes`).**

---

## 3. Provenance, Base Commits & Binary Identity Binding

| Property | Value |
|---|---|
| **Base Repository Commit** | `8410b1a5522fb040e36ae93772e88e1aab842a59` |
| **stable-diffusion.cpp Base Commit** | `50d640568388f876b0d63ee6ddb6bc86d997ec64` |
| **ggml Base Commit** | `30bf8685ed4eb0a47f2b06229543327749904150` |
| **Adreno Vulkan Patch File** | `patches/0001-adreno-vulkan-pipeline-fixes.patch` |
| **Adreno Vulkan Patch SHA-256** | `e307231ec5fb6dc97abc04b7e7f96ac01a21467d7970859069290fb4f093a66b` |
| **CLI Hardware Patch File** | `patches/0002-fix-sd-cli-hardware-gpu-args.patch` |
| **CLI Hardware Patch SHA-256** | `453eee34c56d028777b32a209906f8da98c164281483b416f36ed4e8cfd23e73` |
| **V11 Executable Path** | `validation/galaxy-s25/v11/sd-cli` |
| **V11 Executable Size** | `91,310,288 bytes` |
| **V11 Executable SHA-256** | `efce9303c59aa7001845d4823e7cb1750f42eb7f61ccfb44e52f1b37401e4b53` |
| **CPU Optimized Baseline SHA-256** | `2e247726ef24f6539db83378e9d4fd97989f74fe3d322a7f8135fa7b8f03c06d` |
| **CPU Optimized Equals V11 Executable** | `FALSE` |

---

## 4. Execution & Artifact Metrics

### Model Allocation & Timings
- **Model**: SDXS 512 Tiny SD Distilled Q8_0 (`sdxs-512-tinySDdistilled_Q8_0.gguf`)
- **Resolution / Steps / Seed / CFG**: `256x256` / `1 step` / `42` / `1.0`
- **Model VRAM Allocation**: `651.92 MB`
- **Model RAM Allocation**: `0.00 MB`
- **CPU Tensor Fallback Count**: `PENDING_FALLBACK_AUDIT` (Allocation confirmed on Vulkan backend; full per-op audit reserved)
- **CLIP Conditioning**: `1.22s`
- **1-Step Sampling**: `2.22s` (`2.21s/it`)
- **TAE VAE Decode**: `0.94s`
- **Total Image Generation Time**: `4.39s` (Overall process `4.99s`, RC `0`)

### Output Differentiation
- **Direct C++ sd-cli Output**:
  - File: `validation/galaxy-s25/v11/track-b-v11-sdxs-adreno830.png`
  - Size: `163,884 bytes`
  - SHA-256: `5fc44f5ec199d3137eaaf211859cb4e90759a060b8d4f53e0c605a394a612484`
- **Python CLI termux-diffusion Output**:
  - File: `validation/galaxy-s25/v11/termux-diffusion-vulkan-adreno830.png`
  - Size: `163,834 bytes`
  - SHA-256: `9084f8195a9f6e429e257011d1b01a0571a05d43bee6d19958cb2fac5c33f427`

---

## 5. Python Test Suite Status

- **Branch**: `validation/galaxy-s25`
- **Superproject Commit**: `8955ab72bea8d5f169c9ab136c4c1f45f4c4e9fd`
- **Worktree Clean**: `TRUE`
- **Pytest Results**: `54 passed in 3.08s` (`PYTEST_TOTAL=54`, `PYTEST_PASSED=54`, `PYTEST_FAILED=0`, `PYTEST_RC=0`)
