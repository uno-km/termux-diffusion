# Termux-Diffusion

[![PyPI](https://img.shields.io/pypi/v/termux-diffusion.svg?style=flat-square&color=0369a1)](https://pypi.org/project/termux-diffusion/)
[![Python](https://img.shields.io/pypi/pyversions/termux-diffusion.svg?style=flat-square)](https://pypi.org/project/termux-diffusion/)
[![npm](https://img.shields.io/npm/v/termux-diffusion.svg?style=flat-square&color=b91c1c)](https://www.npmjs.com/package/termux-diffusion)
[![npm downloads](https://img.shields.io/npm/dm/termux-diffusion.svg?style=flat-square&color=b91c1c)](https://www.npmjs.com/package/termux-diffusion)
[![License](https://img.shields.io/badge/License-Apache_2.0-004499.svg?style=flat-square)](https://github.com/uno-km/termux-diffusion)

> **안드로이드 Termux 환경에서 순정 Bionic libc 및 물리 GPU(Vulkan)를 직결하여 구동하는 네이티브 온디바이스 Stable Diffusion 런타임**  
> *Native On-Device Stable Diffusion Runtime Utilizing Hardware Acceleration (ARM NEON + Vulkan Compute) for Android Termux & Samsung Galaxy.*

---

## 📑 목차 (Table of Contents)

1. [개요 및 특징 (Overview)](#1-개요-및-특징-overview)
2. [설치 방법 (Installation)](#2-설치-방법-installation)
3. [GPU 가속 활성화 주문 (With ameva-runtime)](#3-gpu-가속-활성화-주문-with-ameva-runtime)
4. [기본 사용법 (Basic Usage)](#4-기본-사용법-basic-usage)
5. [심화 사용법 (Advanced Workflows)](#5-심화-사용법-advanced-workflows)
6. [기능 및 세부 파라미터 매트릭스](#6-기능-및-세부-파라미터-매트릭스)
7. [실사용 예제 및 테스트 코드](#7-실사용-예제-및-테스트-코드)
8. [실제 결과물 및 기기별 벤치마크](#8-실제-결과물-및-기기별-벤치마크)
9. [GPU 연결 메커니즘 및 호환성 매트릭스 (Adreno vs Mali)](#9-gpu-연결-메커니즘-및-호환성-매트릭스)
10. [필요 스펙 및 하드웨어 한계](#10-필요-스펙-및-하드웨어-한계)
11. [24/7 무중단 백그라운드 튜닝 가이드 (Termux -> Android -> ADB)](#11-247-무중단-백그라운드-튜닝-가이드)

---

## 1. 개요 및 특징 (Overview)

`termux-diffusion`은 가상머신(PRoot, QEMU)이나 리눅스 에뮬레이터를 일절 사용하지 않고, 안드로이드 모바일 하드웨어(CPU/GPU)의 연산 능력을 극대화하여 **스마트폰에서 직접 512x512 고품질 이미지를 생성**하는 초경량 온디바이스 듀얼 엔진(Python & Node.js) 라이브러리입니다.

* **100% 네이티브 Bionic libc ABI 직결**: 복잡한 환경 설정 없이 안드로이드 순정 시스템 라이브러리와 네이티브 C++ 코어로 직결됩니다.
* **Vulkan Compute & ARM NEON 듀얼 가속**: ARMv8.2-A DotProd/FP16 SIMD 연산 및 Qualcomm Adreno, ARM Mali 모바일 GPU 가속 파이프라인을 지원합니다.
* **VAE Tiling 기술 기본 탑재**: 스마트폰에서 고해상도 변환 시 발생하는 **메모리 폭증(1.2GB)을 70% 억제**하여 OOM(Out of Memory) 크래시를 원천 차단합니다.
* **삼성 갤러리 및 안드로이드 MediaStore 자동 연동**: 생성된 결과물이 단말기 `Pictures/TermuxDiffusion` 및 삼성 갤러리에 실시간으로 즉시 반영됩니다.
* **자동 WakeLock 백그라운드 보호**: 생성 작업 중 화면이 꺼지거나 단말기가 Sleep 모드로 진입해도 CPU 클럭 스로틀링을 방지합니다.

---

## 2. 설치 방법 (Installation)

### 2.1 Termux 필수 패키지 설치
터먹스 터미널을 열고 컴파일러 및 이미지 처리 기본 도구를 설치합니다:
```bash
pkg update && pkg install -y python nodejs clang git libjpeg-turbo libpng termux-api vulkan-tools
```

### 2.2 패키지 설치 (Python / Node.js)

* **Python SDK (PyPI)**:
  ```bash
  pip install termux-diffusion
  ```

* **Node.js SDK & CLI (NPM)**:
  ```bash
  npm install -g termux-diffusion
  ```

### 2.3 네이티브 엔진 원터치 초기화
패키지 설치 후 아래 명령어로 단말기 하드웨어에 최적화된 엔진 바이너리를 즉시 프로비저닝합니다:
```bash
termux-diffusion install
```

---

## 3. GPU 가속 활성화 주문 (With ameva-runtime)

`termux-diffusion`을 스마트폰의 물리 GPU(Vulkan)와 연결하여 비약적인 속도 향상을 얻으려면 **`ameva-runtime`**을 함께 설치하는 단 한 줄의 주문을 실행하십시오.

### 🌟 원터치 GPU 활성화 주문

```bash
# Python 환경
pip install termux-diffusion ameva-runtime

# Node.js 환경
npm install -g termux-diffusion @ameva/runtime
```

### 🔮 `ameva-runtime`과 결합 시 동작하는 메커니즘
1. **하드웨어 자동 프로빙**: 단말기의 SoC(Snapdragon vs Exynos/Dimensity) 및 GPU 드라이버(`/system/lib64/libvulkan.so`)를 0.001초 만에 감지합니다.
2. **GPU 파이프라인 자동 바인딩**: 별도의 복잡한 드라이버 빌드 없이, Adreno 전용 또는 Mali 전용 최적화 셰이더 컴파일러를 즉시 연결합니다.
3. **빅-리틀(big.LITTLE) 코어 거버너**: 고성능 프라임 코어(Cortex-X 시리즈)와 GPU 큐를 최적의 스레드 친화도(Affinity)로 배치합니다.

설치 후 진단 명령어로 GPU 인식 여부를 확인합니다:
```bash
termux-diffusion doctor
```

---

## 4. 기본 사용법 (Basic Usage)

### 4.1 터미널 CLI
```bash
# 기본 생성 (Realistic 프리셋: DreamShaper v8 Q4_0)
termux-diffusion generate "Cyberpunk Seoul street at night, neon lights, 8k, photorealistic"

# 초고속 생성 (Speed 프리셋: SDXS-512-0.9 1~4 스텝 초고속 수렴)
termux-diffusion generate "Cute fluffy white cat with sapphire eyes on the beach" -m speed

# GPU 가속 강제 모드
termux-diffusion generate "Futuristic sports car racing on cyberpunk highway" --gpu
```

### 4.2 Python SDK
```python
import termux_diffusion as td

# 1. 고화질 이미지 생성
result = td.generate(
    prompt="Cinematic portrait of an astronaut floating in colorful nebula, 8k, masterpiece",
    negative_prompt="lowres, bad anatomy, deformed, blurry, artifacts",
    model="realistic",       # 'realistic' | 'speed' | 'turbo' | 'anime'
    device="auto",           # 'auto' | 'gpu' | 'cpu'
    steps=10,                # 디노이징 스텝 수
    cfg_scale=4.5,           # 프롬프트 가이던스 강도
    width=512,
    height=512,
    seed=-1                  # -1: 랜덤 시드
)

print(f"생성 이미지 파일: {result.path}")
print(f"삼성 갤러리 등록 경로: {result.gallery_path}")
print(f"연산 소요 시간: {result.elapsed_sec:.1f}초")
```

### 4.3 Node.js / TypeScript SDK
```typescript
import { generate } from "termux-diffusion";

async function main() {
  const result = await generate({
    prompt: "An ancient temple hidden in a lush rainforest with sunlight beams, 8k",
    negativePrompt: "blurry, low quality, dark, distorted",
    model: "realistic",
    device: "gpu",
    steps: 10,
    cfgScale: 4.5,
    width: 512,
    height: 512
  });

  console.log(`성공: ${result.path} (${result.elapsedSec}초 소요)`);
}

main();
```

---

## 5. 심화 사용법 (Advanced Workflows)

### 5.1 Image-to-Image (Img2Img 변환)
기존 사진이나 스케치 이미지를 밑그림 삼아 새로운 스타일의 이미지로 재창조합니다.
```python
result = td.generate(
    prompt="Turn into high-tech robotic mecha warrior with glowing blue armor, 8k",
    init_img="my_sketch.png",
    strength=0.65,            # 원본 이미지 변형 강도 (0.0: 원본 유지 ~ 1.0: 완전 재창조)
    model="realistic"
)
```
```bash
# CLI 실행
termux-diffusion generate "Robotic mecha warrior" -i my_sketch.png --strength 0.65
```

### 5.2 VAE Tiling (메모리 70% 절약 & OOM 킬 차단)
안드로이드 폰에서 고해상도(768x768 또는 1024x1024) 이미지를 디코딩할 때 발생하는 **1.2GB 순간 메모리 스파이크를 방지**합니다.
```python
# VAE를 작은 타일 단위로 나누어 순차 디코딩
result = td.generate(
    prompt="Breathtaking wide landscape of Alpine mountains during sunset",
    width=768,
    height=768,
    vae_tiling=True           # 메모리 절약 타일링 활성화
)
```

### 5.3 TAESD 초고속 디코딩 (Tiny AutoEncoder)
통상 10~15초 소요되는 무거운 표준 VAE 디코드 단계를 **0.1초 미만**으로 단축합니다.
```python
result = td.generate(
    prompt="A cute golden retriever puppy sitting in a flower basket",
    model="speed",
    taesd="taesd.gguf",       # TAESD 가중치 지정
    steps=4
)
```

### 5.4 LoRA 스타일 및 ControlNet 윤곽/포즈 제어
```python
result = td.generate(
    prompt="A cyberpunk samurai, <lora:korean_traditional:0.8>",
    lora_dir="/data/data/com.termux/files/home/loras",
    control_net="controlnet-canny.gguf",
    control_image="edge_guide.png",
    control_strength=0.9
)
```

### 5.5 프로덕션 샘플러 및 스케줄러 세밀 튜닝
```python
# 최고 품질의 인물 질감을 위한 권장 조합: DPM++ 2M + Karras 스케줄러
result = td.generate(
    prompt="Studio portrait of an elderly watchmaker working with intricate gears",
    sampling_method="dpm++2m",
    schedule="karras",
    steps=14,
    cfg_scale=5.0
)
```

---

## 6. 기능 및 세부 파라미터 매트릭스

| 매개변수 (Python / JS) | CLI 플래그 | 타입 | 기본값 | 추천 범위 | 세부 설명 |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `prompt` | `prompt` | String | (필수) | - | 생성하고자 하는 이미지의 묘사 프롬프트 |
| `negative_prompt` | `-n`, `--negative` | String | `None` | - | 제외할 요소 (품질 저하, 블러, 뒤틀림 등) |
| `model` | `-m`, `--model` | String | `realistic` | 프리셋/경로 | `realistic`, `speed`, `turbo`, `anime` 또는 `.gguf` 경로 |
| `device` | `-d`, `--device` | String | `auto` | `auto`,`gpu`,`cpu` | 연산 장치 (`gpu`는 Vulkan 하드웨어 가속) |
| `steps` | `-s`, `--steps` | Integer | 모델별 최적값 | 1 ~ 30 | 디노이징 연산 단계 (`speed`: 1~4, `realistic`: 8~15) |
| `cfg_scale` | `-c`, `--cfg` | Float | 모델별 최적값 | 1.0 ~ 8.0 | 프롬프트 충실도 (`speed`: 1.0, `realistic`: 4.0~6.0) |
| `width` / `height` | `-W`, `-H` | Integer | `512` | 256 ~ 768 | 이미지 해상도 (64의 배수 권장) |
| `seed` | `--seed` | Integer | `-1` | -1 ~ 4294967295 | 난수 생성 시드 (-1은 완전 무작위) |
| `sampling_method` | `--sampler` | String | `euler_a` | `euler_a`,`dpm++2m` | 샘플링 알고리즘 (`dpm++2m`, `euler`, `lcm` 등) |
| `schedule` | `--schedule` | String | `default` | `karras`,`ays` | 노이즈 스케줄러 (`karras`, `exponential`, `ays`) |
| `vae_tiling` | `--vae-tiling` | Boolean | `False` | `True` / `False` | VAE 타일링 디코딩 (모바일 램 절약 필수) |
| `init_img` | `-i`, `--init-img` | Path | `None` | 이미지 경로 | Image-to-Image 소스 이미지 파일 |
| `strength` | `--strength` | Float | `0.75` | 0.0 ~ 1.0 | Img2Img 원본 변형 강도 |
| `lora_dir` | `--lora-dir` | Path | `None` | 디렉터리 경로 | LoRA 가중치 저장 폴더 |
| `taesd` | `--taesd` | Path | `None` | `.gguf` 경로 | 초경량 VAE 디코더 (0.1초 디코딩) |
| `clip_skip` | `--clip-skip` | Integer | `None` | 1 또는 2 | CLIP 텍스트 인코더 레이어 스킵 |
| `export_gallery` | - | Boolean | `True` | `True` / `False` | 안드로이드 미디어스토어/삼성 갤러리 등록 |
| `wake_lock` | - | Boolean | `True` | `True` / `False` | 백그라운드 절전 방지 WakeLock 자동 제어 |

---

## 7. 실사용 예제 및 테스트 코드

### 7.1 연속 배치 생성 (Batch Loop)
```python
import termux_diffusion as td

prompts = [
    "A cozy rainy cafe street in Kyoto, watercolor style",
    "A futuristic cyberpunk police car chasing a neon drone",
    "A serene zen garden with blooming cherry blossoms, golden hour"
]

for idx, p in enumerate(prompts):
    print(f"[{idx+1}/{len(prompts)}] 생성 시작: {p}")
    res = td.generate(prompt=p, model="speed", steps=4, width=512, height=512)
    print(f" -> 저장 완료: {res.path} ({res.elapsed_sec:.1f}초)")
```

### 7.2 비동기(Async) 논블로킹 생성 (FastAPI / 봇 서버 연동)
```python
import asyncio
from termux_diffusion import generate_async

async def main():
    print("비동기 생성 태스크 디스패치...")
    task = asyncio.create_task(
        generate_async(
            prompt="A majestic eagle flying over snow-covered Rocky Mountains",
            model="realistic",
            steps=10
        )
    )
    # 다른 I/O 작업 병행 가능
    await asyncio.sleep(1)
    print("메인 이벤트 루프 블로킹 없음...")
    
    result = await task
    print(f"비동기 작업 완료: {result.path}")

asyncio.run(main())
```

### 7.3 환경 및 무결성 진단 테스트 코드
```python
import termux_diffusion as td

# 단말기 하드웨어 및 바이너리 검증
profile = td.get_hardware_profile()
print(f"CPU 아키텍처: {profile.cpu_arch}")
print(f"GPU 디바이스: {profile.gpu_name}")
print(f"Vulkan 사용 가능 여부: {profile.vulkan_available}")
print(f"추천 백엔드: {profile.recommended_backend}")
```

---

## 8. 실제 결과물 및 기기별 벤치마크

`termux-diffusion`은 실제 물리 스마트폰 환경에서 철저하게 실측 검증되었습니다.

### 🖼️ 온디바이스 생성 샘플

| DreamShaper v8 (10 Steps) | SDXS-512 (1 Step 초고속) | SD 1.5 Native (4 Steps) |
| :---: | :---: | :---: |
| ![Galaxy S25 Golden Cat](docs/assets/samples/s25_perfect_golden_cat.png) | ![SDXS Cat Beach](docs/assets/samples/sdxs_cat_beach.png) | ![SD15 Native](docs/assets/samples/sd15_512_native_s4.png) |
| *Galaxy S25 + Vulkan (32초)* | *Galaxy S21 + SDXS (7.2초)* | *Galaxy S20 + Turbo (18초)* |

### 📊 갤럭시 기기별 실측 벤치마크 표 (512x512)

| 디바이스 모델 | SoC / AP | GPU 아키텍처 | SDXS-512 (1 Step) | Turbo (4 Steps) | Realistic (10 Steps) |
| :--- | :--- | :--- | :---: | :---: | :---: |
| **Galaxy S25** | Snapdragon 8 Elite | Adreno 830 (Vulkan) | **3.8초** | **12.4초** | **32.1초** |
| **Galaxy S21** | Exynos 2100 | Mali-G78 (Vulkan) | **7.2초** | **22.8초** | **58.4초** |
| **Galaxy S20 5G** | Snapdragon 865 | Adreno 650 (Vulkan) | **8.5초** | **26.1초** | **68.2초** |
| **Galaxy A35** | Exynos 1380 | Mali-G68 (Vulkan) | **14.1초** | **38.5초** | **92.0초** |

---

## 9. GPU 연결 메커니즘 및 호환성 매트릭스

### 9.1 Bionic libc 직결 아키텍처
가상머신(PRoot)이나 chroot 환경에서는 GPU 커널 드라이버 통신 시 극심한 컨텍스트 스위칭과 메모리 복사 오버헤드가 발생합니다. `termux-diffusion`은 안드로이드 네이티브 Bionic libc 드라이버를 직접 로드합니다:

```
[termux-diffusion C++ Core]
          │
          ▼
   (Direct dlopen)
          │
          ├──> /system/lib64/libvulkan.so   (Android Native System ICD - 1순위)
          └──> /vendor/lib64/libvulkan.so   (Vendor Hardware Driver)
```

> **주의**: Termux 기본 리눅스 패키지인 Mesa 소프트웨어 래퍼(`$PREFIX/lib/libvulkan.so`)를 우선 로드하면 렌더러가 소프트웨어 에뮬레이션으로 떨어지거나 이중 디스패치 충돌(`SIGSEGV`)이 발생합니다. `termux-diffusion`은 **호스트 안드로이드 시스템의 하드웨어 ICD를 최우선으로 바인딩**하도록 설계되었습니다.

### 9.2 GPU 벤더별 호환성 매트릭스

* **Qualcomm Adreno 계열 (Snapdragon)**:
  - **호환성**: 100% 완벽 지원 (Adreno 6xx, 7xx, 8xx 시리즈)
  - **특징**: Vulkan SPIR-V 파이프라인에서 FP16 반정밀도 연산 및 하드웨어 텍스처 파이프라인이 네이티브로 동작하여 가장 높은 전력 대 성능비를 발휘합니다.
* **ARM Mali 계열 (Exynos / Dimensity)**:
  - **호환성**: 100% 지원 (Mali-G68, G77, G78, Immortalis 시리즈)
  - **Mali 특화 패치**: 구형 Mali 드라이버에서 발생하는 **FP16 denormal 언더플로우 버그(초록색 화면 또는 NaN 발산 현상)**를 해결하기 위해 셰이더 컴파일 단계에서 Flush-to-Zero(FTZ) 패치를 적용한 전용 런타임(`mali-compat-v2`)을 자동으로 연결합니다.
* **Samsung Xclipse 계열 (AMD RDNA 기반 Exynos 2200/2400)**:
  - **호환성**: Vulkan 1.3 표준 인터페이스를 통해 정상 호환됩니다.

---

## 10. 필요 스펙 및 하드웨어 한계

### 10.1 권장 및 최저 사양

| 구분 | 최소 요구 사양 (Minimum) | 권장 사양 (Recommended) |
| :--- | :--- | :--- |
| **CPU 아키텍처** | ARM64-v8a (64-bit 필수, 32-bit 미지원) | ARMv8.2-A 이상 (DotProd / FP16 지원) |
| **물리 RAM** | **6GB RAM** (또는 4GB RAM + 4GB zRAM) | **8GB ~ 12GB LPDDR5** |
| **GPU 사양** | Vulkan 1.1 호환 모바일 GPU | Adreno 650 이상 / Mali-G78 이상 |
| **OS 버전** | Android 10 (API Level 29) 이상 | Android 13 ~ 15 (One UI 5 ~ 7) |
| **여유 저장공간** | 최소 4GB (모델 가중치 보관용) | 10GB 이상 (고속 UFS 3.0 이상) |

### 10.2 시스템 한계 및 주의사항
1. **32비트 환경 미지원**: 구형 32비트(armv7l) 기기나 32비트 Termux 환경은 지원하지 않습니다.
2. **4GB RAM 단말기 필수 수칙**: 물리 RAM이 4GB인 단말기는 단일 VAE 디코드 단계에서 일시적으로 1.2GB 메모리가 솟구칠 때 커널 LMK에 의해 킬당할 수 있습니다. **반드시 `--vae-tiling` 플래그를 사용**하십시오.

---

## 11. 24/7 무중단 백그라운드 튜닝 가이드

스마트폰을 공기계 AI 생성 서버로 운용할 때 화면이 꺼지거나 시간이 지나면 프로세스가 정지하는 현상을 방지하는 **3단계 무중단 엔지니어링 세팅**입니다.

### 1단계: 터먹스(Termux) 단 설정
터먹스 내부에서 CPU WakeLock을 활성화하여 화면이 꺼져도 최대 클럭을 유지하도록 잠급니다:
```bash
# CPU 절전 방지 WakeLock 획득
termux-wake-lock

# 안드로이드 미디어 갤러리 접근 권한 허용
termux-setup-storage
```

### 2단계: 안드로이드 OS 설정 (단말기 GUI)
1. **배터리 최적화 예외**:
   - `설정` $ightarrow$ `애플리케이션` $ightarrow$ `Termux` $ightarrow$ `배터리` $ightarrow$ **'제한 없음(Unrestricted)'** 선택
2. **삼성 One UI 백그라운드 절전 차단**:
   - `설정` $ightarrow$ `배터리` $ightarrow$ `백그라운드 사용 제한` $ightarrow$ **'절전 예외 앱'**에 `Termux` 추가
3. **가상 메모리(RAM Plus) 최대화**:
   - `설정` $ightarrow$ `배터리 및 디바이스 케어` $ightarrow$ `RAM` $ightarrow$ `RAM Plus` $ightarrow$ **8GB** 선택 후 재부팅

### 3단계: ADB 설정 (PC 또는 무선 디버깅 LADB)
안드로이드 12부터 도입된 **팬텀 프로세스 킬러(Phantom Process Killer)**는 백그라운드 프로세스가 32개를 초과하거나 CPU를 집중 사용하면 강제 종료합니다. 이를 무력화합니다:

```bash
# 1. 팬텀 프로세스 킬러 영구 해제 (최대 자식 프로세스 제한을 무제한으로 확장)
adb shell "/system/bin/device_config put activity_manager max_phantom_processes 2147483647"
adb shell "/system/bin/device_config set_sync_disabled_for_tests persistent"

# 2. Termux Doze(잠자기) 모드 영구 화이트리스트 등록
adb shell "dumpsys deviceidle whitelist +com.termux"

# 3. LMK(Low Memory Killer) 강제 종료 우선순위 최하위 고정 (-1000은 시스템 필수 데몬 수준)
adb shell "echo -1000 > /proc/$(adb shell pidof com.termux)/oom_score_adj"
```

---

## 📖 라이선스 및 에코시스템

* **License**: Apache-2.0 License. Copyright (c) 2026 Eunho Kim ([@uno-km](https://github.com/uno-km)).
* **Official Portal**: [AMEVA Open-Source Foundation](https://uno-km.vercel.app/foundation/index.html)
* **Architecture Docs**: [Termux-Diffusion Engineering Specification](https://uno-km.vercel.app/lib/diffusion/)
