# 📱 Galaxy S25 Vulkan GPU vs. CPU 벤치마크 및 런타임/품질 감사 보고서

- **문서 버전**: 1.0.0
- **수행 기기**: Samsung Galaxy S25 (`SM-S931N`, codename `pa1q`)
- **수행 브랜치**: `validation/galaxy-s25`
- **상태**: `AUDITED_EXPERIMENTAL_BASELINE`

---

## 1. 하드웨어 환경 실측 정정 (Hardware Ground Truth)

| 항목 | 실측 값 (Ground Truth) | 비고 |
| :--- | :--- | :--- |
| **단말 모델** | `SM-S931N` | Samsung Galaxy S25 (국내판) |
| **SoC / AP** | `Qualcomm Snapdragon 8 Elite (SM8750)` | 2x Prime 4.32GHz + 6x Perf 3.53GHz |
| **GPU** | `Qualcomm Adreno (TM) 830` | Vulkan API 1.3.284 / Driver `vulkan.adreno.so v0800.64.7` |
| **안드로이드 버전** | `Android 16` | API Level 36 |
| **빌드 핑거프린트** | `samsung/pa1qksx/pa1q:16/BP4A.251205.006/S931NKSSBCZG3_OKRBCZG3:user/release-keys` | 실기기 `getprop` 실측 |
| **커널 버전** | `Linux 6.6.98-android15-8-pd6ff1cd-abogkiS931NKSSBCZG3-4k` | `uname -a` 실측 |
| **시스템 메모리** | `12.0 GB LPDDR5X (UMA=1)` | CPU/GPU 통합 메모리 |

---

## 2. 바이너리 신원 및 무결성 감사 (Binary Identity Audit)

- **CPU 벤치마크 바이너리**:
  - 경로: `/data/data/com.termux/files/home/.cache/termux-diffusion/bin/sd-cli-cpu`
  - 크기: `57,691,680 bytes`
  - SHA-256: `f438993187b87603a1a33336c033deacbdd3b2c594d9a11c172606fcc91f131d`
  - 링킹: 순수 ARMv8.2-A NEON (`libvulkan.so` 동적 링킹 없음)
- **Vulkan 벤치마크 바이너리**:
  - 경로: `/data/data/com.termux/files/home/.cache/termux-diffusion/bin/sd-cli-vulkan`
  - 크기: `91,310,288 bytes`
  - SHA-256: `efce9303c59aa7001845d4823e7cb1750f42eb7f61ccfb44e52f1b37401e4b53`
  - 링킹: Adreno 830 Vulkan 백엔드 (`libvulkan.so` 바인딩)
- **판정**: `CPU_EQUALS_VULKAN_BINARY = FALSE` (완전히 상이한 독립 바이너리 검증 완료)

---

## 3. 정밀 벤치마크 실측 매트릭스

| 모델 계층 | 모델명 / 양자화 | 해상도 / 스텝 / 샘플러 | CPU (4T) 소요시간 | Vulkan GPU 소요시간 | 유효 가속 배율 | VRAM 점유 | 출력 이미지 무결성 |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **FAST** | **SDXS 512** (Q8_0) | **256×256 1스텝**, Euler A | 5.14 s (샘플링 1.43s) | **4.39 s** (샘플링 2.22s) | **1.17x** (Total) | **651.92 MB** | **PASS** (163KB, Colors: 35,729) |
| **BALANCED** | **SDXS 512** (Q8_0) | **512×512 2스텝**, Euler A | 21.09 s (샘플링 12.07s) | **16.24 s** (샘플링 9.46s) | **1.30x** (Total) / **1.28x** (Samp) | **651.92 MB** | **PASS** (660KB, Colors: 115,760) |
| **ANIME (Exp)** | **DreamShaper 8** (Q4_0)| **512×512 6스텝**, LCM | *353.97 s (All-White)* | **184.18 s** (샘플링 172.63s) | *1.31x (Sampling Ref)* | **1,550.08 MB** | **PASS** (529KB, Colors: 8,197) |
| *ANIME (4s)* | *DreamShaper 8 (Q4_0)* | *512×512 4스텝, LCM* | *268.84 s (All-White)* | *126.42 s (Decode Fail)* | **N/A (계산 제외)** | 1,550.08 MB | **FAIL (Decode Fail, RC 1)** |
| *REALISTIC* | *Realistic Vision (Q4_K)*| *512×512 6스텝, Euler A* | *354.40 s (All-White)* | *9.76 s (Fail-Fast 차단)* | **N/A (계산 제외)** | 1,546.84 MB | **FAIL (Pipeline Blocked)** |

---

## 4. 출력 이미지 픽셀 품질 및 고장 모드 분석

1. **SDXS 512×512 Vulkan (BALANCED)**:
   - 파일 크기: `660,583 bytes`
   - 픽셀 통계: Mean `154.95`, StdDev `100.63`, Unique Colors `115,760`
   - 판정: **`SDXS_512_VULKAN_OUTPUT_VALID = TRUE`** (네이티브 512x512 고품질 생성 확인)
2. **CPU Anime & Realistic All-White 실패**:
   - 증상: 출력 크기 `9,405 bytes` / `9,951 bytes`, Mean `255.0`, StdDev `0.0`, Unique Colors `1` (순백색 단색 이미지)
   - 공식 상태: **`EXACT_ROOT_CAUSE = PENDING_LATENT_AND_VAE_AUDIT`** (단순 추정 배제)
3. **Realistic Vision Q4_K Vulkan 실패**:
   - 오류: `ggml_vulkan: Pipeline 'mul_mat_vec_q4_k_f32_f32' create failed: vk::Device::createComputePipeline: ErrorUnknown (req_subgroup=0, wg={2,1,1})`
   - 공식 상태: **`EXACT_ROOT_CAUSE = PENDING_RUNTIME_INSTRUMENTATION`**
