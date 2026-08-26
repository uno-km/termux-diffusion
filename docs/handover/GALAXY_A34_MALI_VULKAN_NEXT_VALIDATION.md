# Galaxy A34 (Mali-G68 MC4 / Dimensity 1080) 차기 Vulkan 검증 인수인계서

**Target Device**: Galaxy A34 5G (`SM-A346N` / `SM-A346B` / `SM-A3460`)  
**Target SoC**: MediaTek Dimensity 1080 (MT6877V)  
**Target GPU**: ARM `Mali-G68 MC4`  
**Reference Document**: `docs/reports/GALAXY_A35_MALI_G68_VULKAN_V10_V11_VALIDATION.md`  

---

## 1. 개요 및 하드웨어 연관성

Galaxy A34 5G는 MediaTek Dimensity 1080 SoC를 탑재하고 있으며, GPU로 Galaxy A35(Exynos 1380)와 동일한 아키텍처 계열인 **ARM Mali-G68 (4-Core MC4)**를 사용합니다.

Galaxy A35 실기기 검증에서 `mali-compat-v2` 바이너리가 Mali-G68 아키텍처에서 무수정 100% 호환(V10 GGML MatMul 무오차, V11 SDXS 15.72초 추론)됨이 입증되었으므로, Galaxy A34에서도 동일한 prebuilt 패키지 재사용을 1순위로 채택합니다.

---

## 2. 재사용 가능한 자산 (Proven Reusable Assets)

1. **Prebuilt 바이너리 패키지**:
   - 아카이브: `termux-diffusion-vulkan-prebuilt-v1.3.1-android-arm64-mali-compat-v2.tar.gz`
   - Release Tag: `v1.3.1-vulkan-mali-experimental`
   - SHA256: `65e4e305241b22385313e386afbcd12722061041280d00a44dfdc3ff23aa17b8`
2. **검증된 파라미터 및 프로필**:
   - `sdxs.gguf` (Q8_0), 256x256, 1-step, sampler=`euler_a`, cfg=1.0
   - Python Gateway: `--device auto`, `--device vulkan`, `--device cpu`
3. **런타임 의존성**:
   - Bionic libc++ / OpenMP: `libc++_shared.so`, `libomp.so`

---

## 3. A34 전용 브랜치 분기 지침 (중요)

> [!CAUTION]
> **A35 검증 브랜치(`validation/galaxy-a35-vulkan`)에서 A34 검증 작업을 직접 시작하지 마십시오.**  
> A35 브랜치 PR이 `main`에 병합된 후, `main` 브랜치를 기준으로 `validation/galaxy-a34-vulkan` 브랜치를 새로 생성하여 작업을 진행해야 합니다.

```bash
# 1. 최신 main 브랜치 동기화
git checkout main
git pull --ff-only origin main

# 2. A34 전용 검증 브랜치 생성 및 전환
git checkout -b validation/galaxy-a34-vulkan
```

---

## 4. Galaxy A34 검증 절차 (Step-by-Step)

### Step 1: 텔레메트리 게이트 확인
Galaxy A34 실기기 Termux SSH 연결 후 다음 정보 확인:
```bash
getprop ro.product.model      # SM-A346N / SM-A346B
getprop ro.board.platform     # mt6877
getprop ro.build.version.release # Android 14 / 15 / 16
```

### Step 2: V10 GGML MatMul 정밀도 검증
```bash
LD_LIBRARY_PATH=./staging/lib ./staging/bin/v10-self-test
# Expected: Mismatches=0/1024, MaxAbsErr < 0.001, RC=0
```

### Step 3: V11 SDXS 추론 검증
```bash
LD_LIBRARY_PATH=./staging/lib ./staging/bin/sd-cli-vulkan \
  -m models/sdxs.gguf \
  -p "a small red robot on a wooden workbench, photorealistic" \
  -n "" -W 256 -H 256 --steps 1 --seed 42 --cfg-scale 1.0 \
  --sampling-method euler_a --backend vulkan0 -t 4 \
  -o outputs/a34-v11-sdxs-mali-g68.png
```

### Step 4: Python CLI E2E 및 폴백 정책 검증
1. `--device auto` $\rightarrow$ Vulkan 선택, 정상 생성
2. `--device vulkan` $\rightarrow$ Vulkan 선택, 정상 생성
3. `--device cpu` $\rightarrow$ CPU NEON 선택, 정상 생성
4. Vulkan 장애 주입 시 `--device auto` $\rightarrow$ CPU 자동 폴백 (RC=0)
5. Vulkan 장애 주입 시 `--device vulkan` $\rightarrow$ Fail-Fast 중단 (RC!=0)

### Step 5: 프로필 등록 및 아티팩트 커밋
- `termux_diffusion/data/validated-vulkan-profiles.json`에 `SM-A346N` / `SM-A346B` 프로필 추가
- `validation/galaxy-a34/vulkan/` 디렉토리에 10개 JSON 및 `SHA256SUMS` 기록
- `pytest tests/` 전체 통과 확인 후 커밋 및 푸시
