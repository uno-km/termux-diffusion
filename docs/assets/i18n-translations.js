/**
 * Termux-Diffusion - Official Documentation Translation Dictionary (AMEVA Ecosystem Design)
 * Languages: English (en), Korean (ko), Japanese (ja), Chinese (zh), Spanish (es), Hindi (hi)
 */

(function(global) {
  'use strict';

  const translations = {
    "en": {
      "common": {
        "brand": "Termux-Diffusion",
        "releaseTag": "v1.1.1 (Dual Engine)",
        "pypiBtn": "PyPI Package",
        "npmBtn": "npm Package",
        "githubBtn": "GitHub Repo",
        "nav": {
          "overview": "Overview",
          "home": "Home / Architecture",
          "installation": "Installation Guide",
          "quickstart": "Quickstart & Recipes",
          "models": "Model Hub & Presets",
          "gallery": "Visual Showcase & Gallery",
          "apiReference": "100% Full API Reference",
          "advancedParams": "High-Precision Parameters",
          "benchmarks": "Benchmarks & Hardware",
          "versions": "Version Archive",
          "advanced": "AI Agent Specifications"
        },
        "footerText": "© 2026 Termux-Diffusion Project (uno-km). Released under the MIT License."
      },
      "home": {
        "title": "Termux-Diffusion",
        "subtitle": "Production On-Device AI Image Generation for Android Termux & Samsung Galaxy (ARM64 Bionic)",
        "quickInstallTitle": "User Scenario Playbook (Quick Start)",
        "quickInstallDesc": "Select your scenario and run the 1-line installation in Termux:",
        "whyTitle": "The Mobile Engineering Challenge",
        "whyText": "Standard desktop Stable Diffusion requires CUDA and 8GB+ VRAM. On Android mobile devices, PRoot Linux introduces 40% memory overhead and triggers Android LMK (Low Memory Killer) aborts.",
        "solTitle": "The Architectural Breakthrough",
        "solText": "Termux-Diffusion runs directly on Android Bionic libc with ARM64 NEON SIMD vectorization, GGUF tensor quantization, automatic CPU WakeLock management, and Samsung Gallery MediaScanner sync.",
        "capTitle": "Key Capabilities & Mobile Hardening",
        "codeExampleTitle": "Canonical Usage Example (Python & Node.js)"
      },
      "installation": {
        "title": "Installation Guide & Scenarios",
        "subtitle": "Step-by-step setup instructions for fresh installs, CLI drafting, and custom models.",
        "tabPip": "Python (pip)",
        "tabNpm": "Node.js (npm)",
        "tabCurl": "1-Click Bootstrap",
        "tabSource": "Build from Source",
        "prereqTitle": "System Prerequisites",
        "verifyTitle": "Installation Verification"
      },
      "quickstart": {
        "title": "Quickstart & Production Recipes",
        "subtitle": "Ready-to-use recipes for photorealism, mobile prototyping, and hardware device targeting."
      },
      "models": {
        "title": "Model Hub & GGUF Quantization Presets",
        "subtitle": "Curated mobile-optimized weights and custom Hugging Face repository streaming."
      },
      "gallery": {
        "title": "Visual Showcase & Render Gallery",
        "subtitle": "Empirical image generation gallery across all 5 model presets, photorealistic Img2Img transforms, and high-precision parameter configurations."
      },
      "api": {
        "title": "100% Full API Reference Manual",
        "subtitle": "Complete parameter tables, storage routing APIs, memory diagnostics, and CLI tool matrix."
      },
      "versions": {
        "title": "Version Archive & Changelog",
        "subtitle": "Release logs, breaking change alerts, and upgrade migration guides."
      }
    },
    "ko": {
      "common": {
        "brand": "Termux-Diffusion",
        "releaseTag": "v1.1.1 (듀얼 엔진)",
        "pypiBtn": "PyPI 패키지",
        "npmBtn": "npm 패키지",
        "githubBtn": "GitHub 저장소",
        "nav": {
          "overview": "문서 개요",
          "home": "홈 / 아키텍처",
          "installation": "설치 가이드",
          "quickstart": "퀵스타트 & 레시피",
          "models": "모델 허브 & 프리셋",
          "gallery": "실전 렌더 갤러리 & 쇼케이스",
          "apiReference": "100% 풀 API 명세",
          "advancedParams": "고정밀 제어 인자",
          "benchmarks": "벤치마크 & 하드웨어",
          "versions": "버전 아카이브",
          "advanced": "AI 에이전트 사양서"
        },
        "footerText": "© 2026 Termux-Diffusion 프로젝트 (김은호 / uno-km). MIT 라이선스에 따라 배포됩니다."
      },
      "home": {
        "title": "Termux-Diffusion",
        "subtitle": "안드로이드 Termux & 삼성 갤럭시 환경을 위한 온디바이스 Bionic ARM64 Stable Diffusion 이미지 생성 프레임워크",
        "quickInstallTitle": "사용자 상황별 실전 플레이북 (초고속 시작)",
        "quickInstallDesc": "본인의 상황에 맞춰 터미널에 1줄만 복사하여 붙여넣으세요:",
        "whyTitle": "모바일 온디바이스 AI 엔지니어링 난제",
        "whyText": "기존 데스크톱 Stable Diffusion은 CUDA와 8GB 이상의 VRAM을 요구하며, PRoot 리눅스 가상화는 40% 이상의 메모리 낭비와 안드로이드 LMK(Low Memory Killer) 강제 종료를 유발합니다.",
        "solTitle": "아키텍처 혁신 및 해결책",
        "solText": "Termux-Diffusion은 가상화 없이 안드로이드 Bionic libc에서 ARM64 NEON 벡터 연산과 GGUF 4비트 양자화 텐서를 직접 구동하며, CPU 슬립 방지(WakeLock) 및 삼성 갤러리 미디어스캐너 자동 동기화를 지원합니다.",
        "capTitle": "핵심 기술 역량 & 모바일 최적화",
        "codeExampleTitle": "대표 표준 코드 예제 (Python & Node.js)"
      },
      "installation": {
        "title": "설치 가이드 & 상황별 가이드",
        "subtitle": "아무것도 없는 사용자, CLI 즉시 생성, 커스텀 모델 사용자를 위한 단계별 안내.",
        "tabPip": "파이썬 (pip)",
        "tabNpm": "노드 (npm)",
        "tabCurl": "원클릭 부트스트랩",
        "tabSource": "소스코드 빌드",
        "prereqTitle": "사전 시스템 요구사항",
        "verifyTitle": "설치 검증 및 진단"
      },
      "quickstart": {
        "title": "퀵스타트 & 실전 레시피",
        "subtitle": "실사 포토리얼리즘, 초저지연 모바일 프로토타이핑, GPU 하드웨어 가속 레시피."
      },
      "models": {
        "title": "모델 허브 & GGUF 프리셋",
        "subtitle": "5대 모바일 최적화 프리셋 및 허깅페이스 커스텀 가중치 자동 스트리밍."
      },
      "gallery": {
        "title": "실전 렌더 갤러리 & 비주얼 쇼케이스",
        "subtitle": "전체 5종 모델 프리셋별 생성 이미지, 원본 사진 기반 Img2Img 변환, 그리고 파라미터별 실제 렌더링 결과 모음."
      },
      "api": {
        "title": "100% 풀 API 공식 레퍼런스",
        "subtitle": "모든 파라미터 전수 명세표, 스토리지 캐시 라우팅, 메모리 진단 및 CLI 명령어 매트릭스."
      },
      "versions": {
        "title": "버전 아카이브 & 변경 이력",
        "subtitle": "공식 릴리즈 로그 및 업데이트 안내."
      }
    },
    "ja": {
      "common": {
        "brand": "Termux-Diffusion",
        "releaseTag": "v1.1.1 (デュアルエンジン)",
        "pypiBtn": "PyPI パッケージ",
        "npmBtn": "npm パッケージ",
        "githubBtn": "GitHub リポジトリ",
        "nav": {
          "overview": "ドキュメント概要",
          "home": "ホーム / アーキテクチャ",
          "installation": "インストールガイド",
          "quickstart": "クイックスタート & レシピ",
          "models": "モデルハブ & プリセット",
          "gallery": "ビジュアルギャラリー & 生成結果",
          "apiReference": "100% 完全APIリファレンス",
          "advancedParams": "高精度パラメータ",
          "benchmarks": "ベンチマーク & ハードウェア",
          "versions": "バージョン履歴",
          "advanced": "AIエージェント仕様書"
        },
        "footerText": "© 2026 Termux-Diffusion Project (uno-km). MIT License."
      },
      "gallery": {
        "title": "ビジュアルギャラリー & 実写ショーケース",
        "subtitle": "5大モデルプリセット、Img2Img変換、各種パラメータによる生成結果一覧。"
      }
    },
    "zh": {
      "common": {
        "brand": "Termux-Diffusion",
        "releaseTag": "v1.1.1 (双引擎)",
        "pypiBtn": "PyPI 软件包",
        "npmBtn": "npm 软件包",
        "githubBtn": "GitHub 仓库",
        "nav": {
          "overview": "文档概览",
          "home": "主页 / 架构",
          "installation": "安装指南",
          "quickstart": "快速上手 & 最佳实践",
          "models": "模型中心 & 预设",
          "gallery": "视觉画廊与生成示例",
          "apiReference": "100% 完整API参考",
          "advancedParams": "高精度控制参数",
          "benchmarks": "基准测试 & 硬件",
          "versions": "版本归档",
          "advanced": "AI智能体规范"
        },
        "footerText": "© 2026 Termux-Diffusion Project (uno-km). MIT License."
      },
      "gallery": {
        "title": "视觉画廊与渲染展示",
        "subtitle": "全系列 5 大模型预设、图生图 (Img2Img) 及各项参数设置的真实生成效果展示。"
      }
    }
        "quickInstallDesc": "根据您的环境选择对应的一键命令直接运行:",
        "whyTitle": "移动端设备工程挑战",
        "whyText": "传统桌面级Stable Diffusion依赖CUDA和8GB以上显存，PRoot虚拟化容器导致40%额外内存损耗并极易触发安卓LMK崩溃。",
        "solTitle": "端侧架构突破与创新",
        "solText": "Termux-Diffusion直接在安卓Bionic libc上原生驱动ARM64 NEON SIMD与GGUF量化张量，支持WakeLock电源防休眠与三星相册自动同步。",
        "capTitle": "核心能力与移动端加固",
        "codeExampleTitle": "标准代码示例 (Python & Node.js)"
      }
    }
  };

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = translations;
  } else if (global.I18nManager) {
    global.i18nTranslations = translations;
  } else {
    global.i18nTranslations = translations;
  }

})(typeof window !== 'undefined' ? window : global);
