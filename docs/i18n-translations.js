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
          "apiReference": "100% Full API Reference",
          "versions": "Version Archive",
          \"advancedParams\": \"Advanced Parameters\",
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
        "releaseTag": "v1.0.0 (듀얼 엔진)",
        "pypiBtn": "PyPI 패키지",
        "npmBtn": "npm 패키지",
        "githubBtn": "GitHub 저장소",
        "nav": {
          "overview": "문서 개요",
          "home": "홈 / 아키텍처",
          "installation": "설치 가이드",
          "quickstart": "퀵스타트 & 레시피",
          "models": "모델 허브 & 프리셋",
          "apiReference": "100% 풀 API 명세",
          "versions": "버전 아카이브",
          \"advancedParams\": \"Advanced Parameters\",
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
        "releaseTag": "v1.0.0 (デュアルエンジン)",
        "pypiBtn": "PyPI パッケージ",
        "npmBtn": "npm パッケージ",
        "githubBtn": "GitHub リポジトリ",
        "nav": {
          "overview": "ドキュメント概要",
          "home": "ホーム / アーキテクチャ",
          "installation": "インストールガイド",
          "quickstart": "クイックスタート & レシピ",
          "models": "モデルハブ & プリセット",
          "apiReference": "100% 完全APIリファレンス",
          "versions": "バージョン履歴",
          \"advancedParams\": \"Advanced Parameters\",
          "advanced": "AIエージェント仕様書"
        },
        "footerText": "© 2026 Termux-Diffusion Project (uno-km). MIT License."
      },
      "home": {
        "title": "Termux-Diffusion",
        "subtitle": "Android Termux & Samsung Galaxy 向けオンデバイス ARM64 Bionic Stable Diffusion 画像生成基盤",
        "quickInstallTitle": "ユーザー状況別クイックプレイブック",
        "quickInstallDesc": "端末環境に合わせて1行コマンドを実行してください:",
        "whyTitle": "モバイルオンデバイスAIの課題",
        "whyText": "従来のデスクトップStable DiffusionはCUDAや8GB以上のVRAMを必要とし、PRoot仮想化はメモリ過消費とAndroid LMKによる強制終了を招きます。",
        "solTitle": "アーキテクチャの突破口",
        "solText": "Termux-Diffusionは仮想化なしでAndroid Bionic libc上でARM64 NEONベクトル演算とGGUF量子化テンソルを直接駆動し、CPUスリープ防止(WakeLock)やSamsung Gallery自動登録を実現します。",
        "capTitle": "コア機能とモバイル堅牢性",
        "codeExampleTitle": "標準コード例 (Python & Node.js)"
      }
    },
    "zh": {
      "common": {
        "brand": "Termux-Diffusion",
        "releaseTag": "v1.0.0 (双引擎)",
        "pypiBtn": "PyPI 软件包",
        "npmBtn": "npm 软件包",
        "githubBtn": "GitHub 仓库",
        "nav": {
          "overview": "文档概览",
          "home": "主页 / 架构",
          "installation": "安装指南",
          "quickstart": "快速上手 & 最佳实践",
          "models": "模型中心 & 预设",
          "apiReference": "100% 完整API参考",
          "versions": "版本归档",
          \"advancedParams\": \"Advanced Parameters\",
          "advanced": "AI智能体规范"
        },
        "footerText": "© 2026 Termux-Diffusion Project (uno-km). MIT License."
      },
      "home": {
        "title": "Termux-Diffusion",
        "subtitle": "面向安卓 Termux 与三星 Galaxy 的端侧 Bionic ARM64 Stable Diffusion AI 图像生成框架",
        "quickInstallTitle": "用户场景速查指南",
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
