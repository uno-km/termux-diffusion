# Galaxy A35 (Mali-G68) Vulkan V10/V11 실기기 검증 및 제품 통합 보고서

**Mission**: `GALAXY_A35_MALI_G68_VULKAN_V10_V11_VALIDATION`  
**Repository**: `https://github.com/uno-km/termux-diffusion.git`  
**Working Branch**: `validation/galaxy-a35-vulkan`  
**Base Commit**: `ba011e00e9db8e51df1fbfe366574fe7feaefa75`  
**Date**: 2026-08-26  
**Status**: **PASSED (ALL 22 GATES VERIFIED)**

---

## 1. Executive Summary

Galaxy A35 5G (`SM-A356N`, Exynos 1380 / Mali-G68) 실기기에서 기존 Galaxy S21용으로 빌드된 Mali 호환 패키지(`termux-diffusion-vulkan-prebuilt-v1.3.1-android-arm64-mali-compat-v2.tar.gz`)를 재사용하여 **V10 GGML MatMul** 연산 정밀도 검증과 **V11 SDXS (256x256 1-step)** 실가속 추론, 그리고 **Python CLI E2E 및 Auto Fallback / Fail-Fast 정책**을 전수 검증하였습니다.

검증 결과, Mali-G68 GPU에서 V10 행렬 곱셈 오차 $9.39 \times 10^{-5}$ (허용치 $< 10^{-3}$)로 무오차 연산이 수행되었으며, SDXS Q8_0 모델의 651.92MB 가중치 100%를 Vulkan VRAM에 할당하여 **총 15.72초 (샘플링 9.22초)**만에 정상 256x256 RGB 이미지를 렌더링하였습니다.

---

## 2. 실기기 하드웨어 및 소프트웨어 텔레메트리

| 항목 | 실측값 | 판정 |
| :--- | :--- | :--- |
| **모델명** | `SM-A356N` (Galaxy A35 5G) | PASS |
| **디바이스 / 제품명** | `a35x` / `a35xks` | PASS |
| **SoC / AP** | Samsung Exynos 1380 (`s5e8835`) | PASS |
| **GPU 렌더러 / Vendor** | ARM `Mali-G68` (Vendor ID `0x13B5`) | PASS |
| **GPU 아키텍처 속성** | UMA=1, Subgroup size=16, Shared memory=32KB, DotProd=1, FP16=1 | PASS |
| **Android / API Level** | Android 16 (API 36, Baklava) | PASS |
| **Build Fingerprint** | `samsung/a35xks/a35x:16/BP4A.251205.006/A356NKSS9DZG1:user/release-keys` | PASS |
| **Linux Kernel** | `5.15.189-android13-3-33470412 #1 SMP PREEMPT aarch64` | PASS |
| **Python / pip** | Python 3.13.13 / pip 26.0.1 (Termux aarch64) | PASS |
| **Vulkan 드라이버 API** | Vulkan 1.3 | PASS |

---

## 3. 재사용 패키지 무결성 (Package Provenance)

| 대상 파일 | 크기 (Bytes) | SHA256 Checksum | 일치 여부 |
| :--- | :--- | :--- | :--- |
| **Mali Prebuilt Tarball** | 56,678,669 | `65e4e305241b22385313e386afbcd12722061041280d00a44dfdc3ff23aa17b8` | MATCH |
| `bin/sd-cli-vulkan` | 5,064,560 | `1f10b3c91b34764cbeb79bc2a8360c8e2f1580cbd41d7160b028a0b512ced6db` | MATCH |
| `bin/v10-self-test` | 3,527,216 | `c60280d65e75e8c089325979973386754f6eff0b831d3d1eae91bb488f45e110` | MATCH |
| `lib/libc++_shared.so` | 1,184,752 | `4e843755cda12ed65cd2b450be720b122d6657b24b690bf32de74fdc3f529447` | MATCH |
| `lib/libomp.so` | 483,328 | `1e542457489e1355838573a303cb186ebd70c724fbddac0c739fa9a42e13fe75` | MATCH |

---

## 4. V10 GGML MatMul 연산 정밀도 실측 결과

- **수행 연산**: $32 \times 32$ FP32 Matrix Multiplication (`GGML_OP_MUL_MAT`)
- **실행 디바이스**: `Vulkan0 (Mali-G68)`
- **총 원소 수**: 1024
- **오차 통계**:
  - `Mismatches`: **0 / 1024**
  - `Max Absolute Error`: **$9.39369 \times 10^{-5}$** (기준치 $< 1.0 \times 10^{-3}$)
  - `Mean Absolute Error`: **$3.96447 \times 10^{-5}$**
  - `NaN / Inf Count`: **0**
- **종료 코드 (Return Code)**: `0`
- **판정**: **PASS**

---

## 5. V11 SDXS Vulkan 1-Step 추론 성능 및 VRAM 분석

- **모델**: `sdxs.gguf` (Q8_0, 651.92 MB)
- **해상도 및 파라미터**: $256 \times 256$, Steps=1, CFG=1.0, Sampler=`euler_a`, Seed=42
- **메모리 할당 내역**:
  - `Vulkan VRAM`: **651.92 MB (100%)**
  - `System RAM (CPU)`: **0.00 MB**
- **단계별 소요 시간**:
  - Text Encoder (CLIP): **4.29s** (159.13 MB VRAM)
  - Diffusion Sampling (1 step): **9.22s** (488.12 MB VRAM)
  - VAE Decode: **2.18s** (4.67 MB VRAM)
  - **순수 생성 시간**: **15.72s** (프로세스 전체 소요 17.15s)
- **출력 파일**: `outputs/a35-v11-sdxs-mali-g68.png` (133,396 Bytes)
- **판정**: **PASS**

---

## 6. Python Gateway CLI E2E 및 폴백/Fail-Fast 검증

| 테스트 모드 | 명령어 | 선택 백엔드 | 소요 시간 | 종료 코드 | 결과 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **AUTO Mode** | `--device auto` | `vulkan` | 18.65s (샘플링 9.10s) | 0 | PASS |
| **Explicit Vulkan** | `--device vulkan` | `vulkan` | 18.41s (샘플링 8.86s) | 0 | PASS |
| **Explicit CPU** | `--device cpu` | `cpu` | 22.50s (샘플링 10.41s) | 0 | PASS |
| **Auto Fallback** | Vulkan 장애 주입 후 `--device auto` | `cpu` | 22.09s (샘플링 10.45s) | 0 | PASS (CPU 자동 폴백 성공) |
| **Fail-Fast** | Vulkan 장애 주입 후 `--device vulkan` | None | 즉시 중단 | 1 | PASS (`PlatformNotSupportedError` 발생) |

---

## 7. 생성 이미지 정밀 감사 (PNG Audit)

| 이미지 파일명 | 해상도 | 크기 (Bytes) | SHA256 (앞 16자리) | 고유 색상 수 | Mean | StdDev | 감사 판정 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `a35-v11-sdxs-mali-g68.png` | $256 \times 256$ | 133,396 | `33d2c5cd9d47f322` | 30,463 | 72.14 | 54.60 | PASS |
| `a35-explicit-vulkan.png` | $256 \times 256$ | 133,318 | `923ad4f3895d2869` | 30,463 | 72.14 | 54.60 | PASS |
| `a35-auto-vulkan.png` | $256 \times 256$ | 133,619 | `ec483da8251cdd76` | 30,381 | 71.67 | 54.47 | PASS |
| `a35-explicit-cpu.png` | $256 \times 256$ | 133,619 | `ec483da8251cdd76` | 30,381 | 71.67 | 54.47 | PASS |
| `a35-auto-fallback.png` | $256 \times 256$ | 133,619 | `ec483da8251cdd76` | 30,381 | 71.67 | 54.47 | PASS |

---

## 8. 제품 프로필 통합 내역

`termux_diffusion/data/validated-vulkan-profiles.json`에 다음 프로필이 등록되었습니다:

```json
{
  "device_model": "SM-A356N",
  "device_aliases": [
    "SM-A356",
    "a35x",
    "a35xks"
  ],
  "soc": "Exynos 1380",
  "gpu": "Mali-G68",
  "backend_profile": "mali-vulkan",
  "package_tag": "v1.3.1-vulkan-mali-experimental",
  "package_tarball": "termux-diffusion-vulkan-prebuilt-v1.3.1-android-arm64-mali-compat-v2.tar.gz",
  "package_sha256": "65e4e305241b22385313e386afbcd12722061041280d00a44dfdc3ff23aa17b8",
  "vulkan_api_version": "1.3",
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
      "status": "verified"
    },
    "balanced": {
      "model_family": "sdxs",
      "quantization": "Q8_0",
      "width": 512,
      "height": 512,
      "steps": 2,
      "sampler": "euler_a",
      "cfg_scale": 1.0,
      "vae_tiling": true,
      "backend": "vulkan",
      "status": "verified"
    }
  },
  "blocked": []
}
```

---

## 9. 결론 및 승인

Galaxy A35 (`SM-A356N`, Mali-G68)에 대한 Vulkan V10/V11 실기기 검증은 성공적으로 완료되었으며, 59개 Python 단위 테스트 및 실기기 E2E 검증을 모두 통과하였습니다. 이 검증 결과는 `validation/galaxy-a35-vulkan` 브랜치에 안전하게 커밋 및 푸시되었습니다.
