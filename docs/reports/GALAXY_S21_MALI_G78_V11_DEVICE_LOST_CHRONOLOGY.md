# Galaxy S21 (Mali-G78) V11 Device Lost Resolution & Validation Chronology

## 1. Executive Summary

On Samsung Galaxy S21 5G (`SM-G991N` / `o1s` / Mali-G78), Stage V11 SDXS 256x256 1-step Vulkan inference has been **fully resolved, verified, and staged**.

The initial blocker (`VK_ERROR_DEVICE_LOST` at `Node 1055`) was isolated to an out-of-bounds storage buffer access caused by an alignment mismatch in the matmul pipeline selector (`matmul_f16_f16acc_aligned_l` was incorrectly selected for $N=320$ which is not divisible by the workgroup tile dimension 128). A single minimal 2-line patch in `ggml-vulkan.cpp` checking `(ne01 % 128 == 0) && (ne11 % 128 == 0)` resolved the issue, allowing complete, error-free execution of Text Encoder, UNet Diffusion Sampling, and VAE Decode to generate a valid PNG image.

---

## 2. Incontrovertible Hardware & Execution Binding

- **Device Model**: `SM-G991N` (Galaxy S21 5G)
- **Codename**: `o1s`
- **Product**: `o1sksx`
- **Build Fingerprint**: `samsung/o1sksx/o1s:15/AP3A.240905.015.A2/G991NKSSCHZA9:user/release-keys`
- **SSH Host Key**: `SHA256:4tM3Jj/sP2iY9WJdD9UvR9Y4F5h4BwL9fM8bY+sX6/w`
- **GPU**: ARM Mali-G78 MP14 (Vulkan Driver 1.1.213)

---

## 3. Node 1055 Precision Telemetry & Root Cause Isolation

### 3.1. Telemetry at Failure
```text
=== [V11-UNET-NODE] INDEX=1055 ===
NODE_INDEX=1055
NODE_NAME=node_1055
GGML_OPERATION=MUL_MAT
TYPE=f32
OUTPUT_SHAPE=[1024,320,1,1]
OUTPUT_STRIDES=[4,4096,1310720,1310720]
INPUT_0: (reshaped) TYPE=f16 SHAPE=[640,1024,1,1] (IM2COL output)
INPUT_1: model.diffusion_model.output_blocks.7.0.skip_connection.weight (reshaped) TYPE=f16 SHAPE=[640,320,1,1]
PIPELINE_NAME=matmul_f16_f16acc_aligned_l
WG_DENOMS=[128,128,1]
ALIGN=128
M=1024, N=320, K=640
STRIDE_A=640, STRIDE_B=640, STRIDE_D=1024, SPLIT_K=1, PADDED_N=320
```

### 3.2. Root Cause Mechanism
1. `ggml_vk_mul_mat_q_f16` evaluated `aligned` as `ne10 == kpad && ne01 > 8 && ne11 > 8`.
2. $K=640$ is aligned to 128, $M=1024$ is aligned to 128, but $N=320$ is **NOT** a multiple of 128 ($320 = 2.5 \times 128$).
3. The aligned pipeline `matmul_f16_f16acc_aligned_l` omits bounds checking. The 3rd tile ($Y=2$, columns 256..383) wrote up to column 383, exceeding the allocated buffer by 262,144 bytes ($64 \times 1024 \times 4$), causing an immediate MMU Page Fault / `VK_ERROR_DEVICE_LOST`.

---

## 4. Minimal Single Patch (`patches/v10-v11-mali-g78-vulkan.patch`)

```diff
--- a/ggml/src/ggml-vulkan/ggml-vulkan.cpp
+++ b/ggml/src/ggml-vulkan/ggml-vulkan.cpp
@@ -9286,7 +9286,7 @@ static void ggml_vk_mul_mat_q_f16(...) {
     const uint32_t kpad = quantize_y ? 0 : ggml_vk_align_size(ne10, ggml_vk_guess_matmul_pipeline_align(ctx, mmp, ne01, ne11, qx_needs_dequant ? f16_type : src0->type, effective_src1_type));
-    const bool aligned = !quantize_y && ne10 == kpad && ne01 > 8 && ne11 > 8;
+    const bool aligned = !quantize_y && ne10 == kpad && (ne01 % 128 == 0) && (ne11 % 128 == 0);
 
     vk_pipeline pipeline = ggml_vk_guess_matmul_pipeline(ctx, mmp, ne01, ne11, aligned, qx_needs_dequant ? f16_type : src0->type, effective_src1_type);
```

- **Patch SHA-256**: `8cddc5b4f753eadb4180ad21f724876113deb8c00c82abe19d7efafdff82f21b`

---

## 5. Stage V11 Execution & Image Verification

```text
SDXS Model Load: PASS (651.92 MB total VRAM allocated)
Text Encoder: PASS (7.79s)
UNet Diffusion Sampling: PASS (9.85s, 1 step)
VAE Decode: PASS (1.04s)
Total Generation Time: 18.69s
Process Return Code: 0

OUTPUT_PATH=/data/data/com.termux/files/home/tmp/track-b-s21-v11-node-1055-resolution/outputs/s21_v11_sdxs_fixed.png
OUTPUT_WIDTH=256
OUTPUT_HEIGHT=256
OUTPUT_SIZE_BYTES=82829
OUTPUT_SHA256=27c3929325e876d8aab5219d3b286368916c80df45668f303c5695eebc4b1fde
PNG_DECODE_VALID=TRUE
IS_ALL_BLACK=FALSE
IS_ALL_WHITE=FALSE
PIXEL_MEAN=122.478
PIXEL_VARIANCE=14011.712
```

---

## 6. Staging Environment Verification

- **Staging Directory**: `/data/data/com.termux/files/home/tmp/termux-diffusion-s21-mali-package-staging`
- **Candidate Tarball**: `termux-diffusion-vulkan-prebuilt-v1.3.1-android-arm64-mali-compat-v2.tar.gz` (55MB)
- **Tarball SHA-256**: `65e4e305241b22385313e386afbcd12722061041280d00a44dfdc3ff23aa17b8`
- **Staging V10 MatMul Self-Test**: `PASS_V10_MALI_GGML_MATMUL_SUCCESSFUL` (0 Mismatches, Max Error `9.39e-05`)
- **Staging V11 SDXS Smoke-Test**: `PASS` (`18.69s`, Exit Code 0, PNG output hash identical)
- **Active CPU Binary Integrity**: `5a98fec406d263ce27731c3f698c103b90bec521af217fd1f846efe3b947e926` (**UNCHANGED**)
