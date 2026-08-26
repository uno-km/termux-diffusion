# 🛠️ Galaxy S25 CPU All-White 출력 고장 모드 수정 인수인계서

- **문서 버전**: 1.0.0
- **대상 기기**: Samsung Galaxy S25 (`SM-S931N`, Qualcomm Oryon ARMv8.2-A)
- **고장 증상**: CPU 백엔드 추론 시 `9,405 bytes` / `9,951 bytes` 단색 순백색(All-White, Mean=255.0, StdDev=0.0) PNG 출력
- **정밀 원인 판정**: `PENDING_LATENT_AND_VAE_AUDIT`

---

## 1. 고장 개요
CPU 백엔드(`sd-cli-cpu`)에서 Anime(4-step, 6-step) 및 Realistic Vision 추론 시 UNet 샘플링은 정상 완료되나, 최종 출력 이미지가 순백색으로 생성되어 픽셀 품질 검증에서 부적격 판정되었습니다.

### 대상 모델 및 파일 크기
- `s25_anime_512_4s_cpu.png`: `9,405 bytes` (Mean 255.0, StdDev 0.0, Unique Colors 1)
- `s25_anime_512_6s_cpu.png`: `9,405 bytes` (Mean 255.0, StdDev 0.0, Unique Colors 1)
- `s25_real_512_6s_cpu.png`: `9,951 bytes` (Mean 255.0, StdDev 0.0, Unique Colors 1)

---

## 2. 다음 수정 에이전트 계측 지침
1. **UNet Latent Telemetry 수집**:
   - `LATENT_MIN`, `LATENT_MAX`, `LATENT_MEAN`, `LATENT_STDDEV`, `LATENT_NAN_COUNT`, `LATENT_INF_COUNT`.
2. **VAE Input / Output 계측**:
   - `VAE_OUTPUT_PRE_CLAMP_MIN/MAX/MEAN/STDDEV` 측정하여 VAE 디코드 내부 발산 여부 확인.
3. **수정 전 제품 정책**:
   - CPU Anime 및 CPU Realistic 프리셋은 사용자 UI 및 벤치마크 비교표에서 완전 비활성화 유지.
