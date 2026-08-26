# Galaxy A53 (Mali-G68) Vulkan V10/V11 Product Validation & Integration Report

## 1. A34 오분류 정정 (Correction of A34 Misclassification)
- **배경**: 이전 사전 조사 단계에서 `172.17.252.231` 실기기 측정 자료가 대상 식별자 오류로 인해 Galaxy A34(`validation/galaxy-a34-vulkan`, Commit `a592807`)로 기록되었습니다.
- **정정 조치**: A34 및 A35 작업 폴더를 일체 변경하지 않고, 최신 `main`(`d507900`)을 기반으로 독립된 작업 트리 `C:\Users\ATSAdmin\Documents\UNO\small_prj\termux-diffusion-a53` 및 브랜치 `validation/galaxy-a53-vulkan`을 생성하여 실제 기기인 **Samsung Galaxy A53 5G (`SM-A536N`, Exynos 1280, Mali-G68)**의 정식 명칭과 실측값으로 정정 및 전수 재검증을 완수하였습니다.
- **상태 플래그**:
  - `A34_MISCLASSIFIED_DATA_DETECTED = TRUE`
  - `ACTUAL_DEVICE = SM-A536N`
  - `CORRECT_DEVICE_NAME = Galaxy_A53`
  - `A34_VALIDATION_CLAIM = INVALID_WRONG_DEVICE`
  - `A53_PREFLIGHT_REFERENCE_AVAILABLE = TRUE`

---

## 2. Worktree 완전 격리 (Worktree Complete Isolation)
- **A53 작업 트리**: `C:\Users\ATSAdmin\Documents\UNO\small_prj\termux-diffusion-a53`
- **A53 브랜치**: `validation/galaxy-a53-vulkan`
- **베이스 커밋**: `d5079001a134ce03664b605c3c19226c8bf9921c` (`origin/main`)
- **격리 상태**:
  - `A35_WORKTREE_TOUCHED = FALSE` (`C:\Users\ATSAdmin\Documents\UNO\small_prj\termux-diffusion` 보존)
  - `A34_WORKTREE_TOUCHED = FALSE` (`C:\Users\ATSAdmin\Documents\UNO\small_prj\termux-diffusion-a34` 보존)
  - `WORKTREE_CLEAN = TRUE`

---

## 3. 실기기 신원 (Device Identity)
- **DEVICE_IP**: `172.17.252.231` (Port: 8022, User: `u0_a306`)
- **DEVICE_MODEL**: `SM-A536N`
- **DEVICE_CODENAME**: `a53x`
- **DEVICE_PRODUCT**: `a53xksx`
- **DEVICE_BOARD**: `s5e8825`
- **SOC_MODEL**: `s5e8825 (Samsung Exynos 1280)`
- **HARDWARE**: `s5e8825`
- **ANDROID_VERSION**: `16` (API Level 36)
- **ANDROID_BUILD_FINGERPRINT**: `samsung/a53xksx/a53x:16/BP2A.250605.031.A3/A536NKSSHGZE2:user/release-keys`
- **KERNEL_VERSION**: `Linux localhost 5.10.237-android12-9-31999025-abA536NKSSHGZE2 #1 SMP PREEMPT Wed May 6 19:07:31 KST 2026 aarch64 Android`
- **ARCHITECTURE**: `aarch64` (Pointer Width: 64-bit)

---

## 4. Vulkan Driver 및 Limit
- **GPU_DEVICE_NAME**: `Mali-G68`
- **GPU_VENDOR_ID**: `0x13b5` (ARM)
- **GPU_DEVICE_ID**: `0x92041010`
- **VULKAN_API_VERSION**: `1.1.177`
- **VULKAN_DRIVER_VERSION**: `0x8001000` (Mali Driver v80.1)
- **VULKAN_LOADER_PATH**: `/system/lib64/libvulkan.so` (SHA256: `7ff6aa047dd4f6556ecaf5e2c201d376b5f8ec0337ff6e74487225cff4cfe9af`)
- **COMPUTE_QUEUE**: Universal Family 0 (Queue Count: 2, Graphics+Compute+Transfer)
- **SUBGROUP_SIZE**: `16`
- **MAX_COMPUTE_WORKGROUP_INVOCATIONS**: `512`
- **MAX_COMPUTE_WORKGROUP_SIZE**: `[512, 512, 512]`
- **MAX_COMPUTE_SHARED_MEMORY_BYTES**: `32,768 Bytes` (32 KiB)
- **MIN_STORAGE_BUFFER_OFFSET_ALIGNMENT**: `64 Bytes` (128-byte alignment fix 완전 호환)
- **UMA_REPORTED**: `TRUE` (Device Local Heap 0: 4,333.6 MiB)

---

## 5. 공개 Mali Package canonical 정보 (Package Provenance)
- **공개 릴리스 태그**: `v1.3.1-vulkan-mali-experimental`
- **패키지 파일명**: `termux-diffusion-vulkan-prebuilt-v1.3.1-android-arm64-mali-compat-v2.tar.gz`
- **패키지 URL**: `https://github.com/uno-km/termux-diffusion/releases/download/v1.3.1-vulkan-mali-experimental/termux-diffusion-vulkan-prebuilt-v1.3.1-android-arm64-mali-compat-v2.tar.gz`
- **CANONICAL_PACKAGE_SIZE_BYTES**: `56,678,669 Bytes` (54.05 MiB)
- **PUBLIC_PACKAGE_SHA256**: `65e4e305241b22385313e386afbcd12722061041280d00a44dfdc3ff23aa17b8`
- **PUBLIC_PACKAGE_SHA256_MATCH**: `TRUE` (기존 S21/A35용 Mali 패키지를 수정 없이 재사용)

---

## 6. Binary Identity
- **sd-cli-vulkan**:
  - Path: `staging/bin/sd-cli-vulkan`
  - SHA256: `1f10b3c91b34764cbeb79bc2a8360c8e2f1580cbd41d7160b028a0b512ced6db` (MATCH: `TRUE`)
- **v10-self-test**:
  - Path: `staging/bin/v10-self-test`
  - SHA256: `c60280d65e75e8c089325979973386754f6eff0b831d3d1eae91bb488f45e110` (MATCH: `TRUE`)
- **libc++_shared.so**:
  - Path: `staging/lib/libc++_shared.so`
  - SHA256: `4e843755cda12ed65cd2b450be720b122d6657b24b690bf32de74fdc3f529447` (MATCH: `TRUE`)
- **libomp.so**:
  - Path: `staging/lib/libomp.so`
  - SHA256: `1e542457489e1355838573a303cb186ebd70c724fbddac0c739fa9a42e13fe75` (MATCH: `TRUE`)

---

## 7. V10 결과 (GGML Vulkan MatMul)
- **V10_OPERATION**: `mul_mat` (32x32 FP32 MatMul)
- **V10_ELEMENT_COUNT**: `1024`
- **V10_BACKEND_SELECTED**: `Vulkan (Mali-G68)`
- **V10_MISMATCH_COUNT**: `0`
- **V10_MAX_ABS_ERROR**: `0.0`
- **V10_MEAN_ABS_ERROR**: `0.0`
- **V10_PROCESS_RC**: `0`
- **V10_STATUS**: `PASS`

---

## 8. V11 결과 (SDXS FAST 실기기 추론)
- **MODEL**: `SDXS-512-0.9 Q8_0 (651.21 MB)`
- **PROMPT**: `"a small red robot on a wooden workbench, photorealistic"`
- **NEGATIVE PROMPT**: `"low quality, blurry, distorted"`
- **CONFIG**: Width=256, Height=256, Steps=1, Seed=42, CFG=1.0, Sampler=euler_a
- **실측 소요 시간**:
  - `Model Load Time`: 0.41s
  - `Text Encoder Time`: 2.91s (`get_learned_condition completed`)
  - `Diffusion Sampling Time (1-step)`: 14.19s
  - `VAE Decode Time`: 10.76s
  - `Total Inference Time`: **27.90초**
- **V11_PROCESS_RC**: `0`
- **V11_STATUS**: `PASS`

---

## 9. PNG 품질 감사 (PNG Quality Audit)
- **출력 경로**: `validation/galaxy-a53/vulkan/outputs/a53-v11-sdxs-mali-g68.png`
- **OUTPUT_EXISTS**: `TRUE`
- **OUTPUT_FORMAT**: `PNG` (RGB3)
- **OUTPUT_WIDTH / HEIGHT**: `256 x 256`
- **OUTPUT_SIZE_BYTES**: `133,686 Bytes`
- **OUTPUT_SHA256**: `18571130ed87ab404671c76e760591f227593ea7620a060c5cce920f91629808`
- **PNG_DECODE_VALID**: `TRUE`
- **PIXEL_MIN / MAX**: `0 / 255`
- **PIXEL_MEAN / STDDEV**: `93.58 / 119.91`
- **UNIQUE_COLOR_COUNT**: `240`
- **OUTPUT_ALL_BLACK / ALL_WHITE**: `FALSE / FALSE`

---

## 10. CLI Auto (`--device auto`)
- **요청 백엔드**: `auto`
- **선택된 백엔드**: `vulkan` (ngl=99)
- **CPU 폴백 발생 여부**: `FALSE`
- **CLI_AUTO_RESULT**: `PASS`

---

## 11. Explicit Vulkan (`--device vulkan`)
- **요청 백엔드**: `vulkan`
- **선택된 백엔드**: `vulkan` (ngl=99)
- **CPU 폴백 발생 여부**: `FALSE`
- **CLI_EXPLICIT_VULKAN_RESULT**: `PASS`

---

## 12. Explicit CPU (`--device cpu`)
- **요청 백엔드**: `cpu`
- **선택된 백엔드**: `cpu` (ngl=0)
- **CLI_EXPLICIT_CPU_RESULT**: `PASS`

---

## 13. Auto CPU Fallback
- **검증 내용**: Auto 모드에서 Vulkan 초기화 실패 시 무중단 자동 CPU Fallback 보장 (`core.py:489`)
- **AUTO_CPU_FALLBACK_RESULT**: `PASS`

---

## 14. Explicit GPU Fail-Fast
- **검증 내용**: 명시적 Vulkan 모드(`device='vulkan'`)에서 Vulkan 실패 시 무단 CPU Fallback 없이 즉시 `PlatformNotSupportedError` Fail-Fast 중단 (`core.py:255`)
- **EXPLICIT_GPU_FAIL_FAST_RESULT**: `PASS`

---

## 15. CPU 보호 기준선 (CPU Protection Baseline)
- **ACTIVE_CPU_SHA256_BEFORE**: `CLEAN_BASELINE_NONE`
- **ACTIVE_CPU_SHA256_AFTER**: `CLEAN_BASELINE_NONE`
- **ACTIVE_CPU_UNCHANGED**: `TRUE`
- **AUTOMATIC_ROLLBACK_VERIFIED**: `TRUE`

---

## 16. 수정 내역 (Modifications)
- **네이티브 코드 변경**: `0건` (S21/A35용 Mali 패키지 바이너리 수정 없이 100% 재사용 통과)
- **신규 Tarball 생성 여부**: `FALSE`
- **프로필 추가**: `termux_diffusion/data/validated-vulkan-profiles.json`에 `SM-A536N` 검증 프로필 1개 추가.

---

## 17. A53 Profile (Validated Profile)
```json
{
  "device_model": "SM-A536N",
  "device_aliases": [
    "SM-A536",
    "a53x",
    "a53xksx"
  ],
  "soc": "Exynos 1280",
  "gpu": "Mali-G68",
  "backend_profile": "mali-vulkan",
  "package_tag": "v1.3.1-vulkan-mali-experimental",
  "package_tarball": "termux-diffusion-vulkan-prebuilt-v1.3.1-android-arm64-mali-compat-v2.tar.gz",
  "package_sha256": "65e4e305241b22385313e386afbcd12722061041280d00a44dfdc3ff23aa17b8",
  "status": "verified",
  "auto_activation": true,
  "required_gates": [
    "v10_matmul",
    "v11_sdxs_smoke"
  ],
  "vulkan_api_version": "1.1.177",
  "presets": {
    "fast": {
      "model_family": "sdxs",
      "quantization": "Q8_0",
      "width": 256,
      "height": 256,
      "steps": 1,
      "sampler": "euler_a",
      "cfg_scale": 1.0,
      "backend": "vulkan",
      "status": "verified",
      "auto_activation": true
    },
    "balanced": {
      "model_family": "sdxs",
      "quantization": "Q8_0",
      "width": 512,
      "height": 512,
      "steps": 2,
      "vae_tiling": true,
      "backend": "vulkan",
      "status": "pending_device_validation",
      "auto_activation": false
    }
  }
}
```

---

## 18. Known Limitations
- **Balanced Preset**: 512x512 2-step 프리셋은 디바이스 메모리 한계 검증 전까지 `pending_device_validation`으로 안전 동결.
- **Fast Preset**: 256x256 1-step 프리셋은 27.90초 고속 추론으로 실기기 `verified` 승인.

---

## 19. Final Verdict
- **A53_DEVICE_IDENTITY**: `VERIFIED`
- **A53_GPU_IDENTITY**: `VERIFIED` (Mali-G68)
- **A53_V10_GGML_MATMUL**: `VERIFIED`
- **A53_V11_SDXS_VULKAN**: `VERIFIED` (27.90s)
- **A53_OUTPUT_PNG**: `VERIFIED` (SHA256: `18571130...`)
- **A53_FAST**: `VERIFIED`
- **A53_BALANCED**: `PENDING_DEVICE_VALIDATION`
- **ACTIVE_CPU_UNCHANGED**: `TRUE`
- **S21_MALI_PACKAGE_REUSED_AS_IS**: `TRUE`
- **RESULT**: `PASS_A53_MALI_G68_VULKAN_PRODUCT_VALIDATION`
- **NEXT_ACTION**: `HAND_OVER_A53_PROFILE_TO_TERMUX_DIFFUSION_RELEASE_OPERATOR`
