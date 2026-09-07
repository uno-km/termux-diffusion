# 📱 Galaxy S25 Vulkan GPU vs CPU Benchmark & Runtime Audit Report

- **Document Version**: 1.0.0
- **Device**: Samsung Galaxy S25 (`SM-S931N`, Snapdragon 8 Elite)
- **Branch**: `validation/galaxy-s25`
- **Status**: `AUDITED_EXPERIMENTAL_BASELINE`

---

## 1. Hardware Ground Truth & Telemetry

- **CPU**: 2x Oryon Prime @ 4.32 GHz + 6x Oryon Performance @ 3.53 GHz
- **GPU**: Qualcomm Adreno 830 (12 compute units, 1.1 GHz)
- **Vulkan Driver**: Qualcomm proprietary driver v512.784
- **Performance Summary**: Vulkan FP16 delivers ~1.08s per iteration at 512x512 resolution.
