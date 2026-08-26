# 🚀 Galaxy S25 Adreno Vulkan 제품 릴리스 관리 에이전트 인수인계서

- **문서 버전**: 1.1.0
- **작성 일자**: 2026-08-26
- **저장소**: `https://github.com/uno-km/termux-diffusion.git`
- **인계 브랜치**: `validation/galaxy-s25`
- **패키지 상태**: `PACKAGE_STATUS = VERIFIED_UNSIGNED_EXPERIMENTAL_CANDIDATE`
- **공개 배포 상태**: `PUBLISH_READY = FALSE` (Offline Root Key 서명 대기)

---

## 1. 운영 에이전트 핵심 인계 사항

### A. 검증 완료된 제품 프리셋 (Production Presets)
1. **`fast`**: SDXS 512 Q8_0 (256×256 1-step, Euler A, CFG 1.0, Vulkan GPU) -> 실측 **4.39s** (C++) / **7.68s** (CLI), 정상 이미지 검증 완료 (`VERIFIED`).
2. **`balanced`**: SDXS 512 Q8_0 (512×512 2-step, Euler A, CFG 1.0, Vulkan GPU, VAE Tiling) -> 실측 **16.24s** (샘플링 9.46s), 660KB 고품질 PNG 검증 완료 (`VERIFIED`).
3. **`anime_experimental`**: DreamShaper 8 LCM Q4_0 (512×512 6-step, LCM, CFG 1.5, Vulkan GPU, VAE Tiling) -> 실측 **184.18s**, 529KB 정상 PNG 검증 완료 (`VERIFIED_EXPERIMENTAL`, 명시적 요청 시에만 활성화).

### B. 비활성화된 실패 경로 (Disabled Failure Tracks)
- **Realistic Vision Q4_K (Vulkan)**: `BLOCKED_PIPELINE_CREATION` (`docs/handover/GALAXY_S25_ADRENO_Q4_K_PIPELINE_FIX_HANDOVER.md` 참조)
- **DreamShaper & Realistic (CPU)**: `BLOCKED_CPU_QUALITY_FAILURE` (`docs/handover/GALAXY_S25_CPU_ALL_WHITE_OUTPUT_FIX_HANDOVER.md` 참조)
- **DreamShaper 4-step (Vulkan)**: `FAILED_VAE_DECODE` (가속 배율 계산 및 제품 게시 전면 제외)

---

## 2. 릴리스 관리 에이전트 체크리스트
1. **`validation/galaxy-s25` 브랜치 최신화**:
   ```bash
   git fetch origin
   git switch validation/galaxy-s25
   git pull --ff-only origin validation/galaxy-s25
   ```
2. **오프라인 루트 키 서명 (Offline Root Signing)**:
   - 대상: `dist_vulkan/manifest-v1.3.1-vulkan-experimental.json`
   - 공식 릴리스 공개키: `ea58ee6d830ca51164a3968c38e4abbad7fe39ebb761164821cba00524c15721`
3. **GitHub Experimental Pre-release 생성 및 4대 Asset 업로드**:
   - `termux-diffusion-vulkan-prebuilt-v1.3.1-android-arm64-adreno.tar.gz` (`d1fc30fc...`)
   - `manifest-v1.3.1-vulkan-experimental.json`
   - `v10-self-test`
   - `SHA256SUMS`
4. **S25 실기기 Staging E2E 검증**:
   - V10 GGML MatMul Self-Test (PASS)
   - V11 FAST Smoke Test (PASS)
   - V11 BALANCED Smoke Test (PASS)
   - Rollback & CPU 보호 검증 (PASS)
5. **금지 사항**:
   - Q4_K 또는 CPU Anime/Realistic 활성화 금지
   - GitHub E2E 검증 전 PyPI/npm 게시 금지
   - 대형 바이너리 Git 커밋 금지
