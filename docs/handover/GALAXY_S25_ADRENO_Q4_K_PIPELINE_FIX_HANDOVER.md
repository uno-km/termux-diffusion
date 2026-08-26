# 🛠️ Galaxy S25 Adreno 830 Q4_K Vulkan Pipeline 실패 수정 인수인계서

- **문서 버전**: 1.0.0
- **대상 기기**: Samsung Galaxy S25 (`SM-S931N` / Qualcomm Snapdragon 8 Elite / Adreno 830)
- **실패 분류**: `Q4_K_VULKAN_PIPELINE_CREATION_FAILED`
- **정밀 원인 판정**: `PENDING_RUNTIME_INSTRUMENTATION`

---

## 1. 장애 개요
Realistic Vision V6.0 B1 (`realisticVisionV60B1_v51HyperVAE-Q4_k.gguf`, Q4_K, 1.55GB) 추론 시, GGML Vulkan 백엔드 초기화 중 `mul_mat_vec_q4_k_f32_f32` 컴피우트 파이프라인 생성에 실패하며 프로세스가 즉시 안전하게 차단됩니다.

### 최초 발생 로그 (Raw Log)
```text
ggml_vulkan: Pipeline 'mul_mat_vec_q4_k_f32_f32' create failed: vk::Device::createComputePipeline: ErrorUnknown (req_subgroup=0, wg={2,1,1})
ggml_vulkan: CRITICAL - Attempted to dispatch null pipeline 'mul_mat_vec_q4_k_f32_f32'
```

---

## 2. 다음 수정 에이전트 계측 지침
1. **Shader SPIR-V SHA-256 추출 및 무결성 검증**:
   - `dmmv_q4_k_f32_f32` SPIR-V 바이트코드와 Adreno 830 드라이버 호환성 확인.
2. **Specialization Constants 계측**:
   - `constant_id=0` (BLOCK_SIZE), `constant_id=1` (NUM_ROWS), `constant_id=2` (NUM_COLS).
   - `local_size_x_id=0` (Workgroup Size = 64)과 BLOCK_SIZE(2) 불일치 여부를 런타임 디버거로 확인.
3. **Qualcomm Vulkan Driver Compiler Log 회수**:
   - `VK_EXT_debug_utils`를 활성화하여 Adreno 드라이버 컴파일러가 반환하는 내부 진단 메시지 수집.
4. **수정 전 제품 정책**:
   - Realistic Vision Q4_K는 제품 프리셋 및 자동 라우팅에서 완전 비활성화 유지.
