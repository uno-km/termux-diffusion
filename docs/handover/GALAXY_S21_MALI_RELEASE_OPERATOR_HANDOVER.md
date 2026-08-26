# Galaxy S21 Mali-G78 Release Operator Handover Document

## 1. Release Identification & Publication Summary

- **Repository**: `https://github.com/uno-km/termux-diffusion`
- **Source Branch**: `feature/gpu`
- **Source Commit**: `8359dac1170fad5b83f500c7b9633092e9cbd277`
- **GitHub Release Tag**: `v1.3.1-vulkan-mali-experimental`
- **GitHub Release URL**: `https://github.com/uno-km/termux-diffusion/releases/tag/v1.3.1-vulkan-mali-experimental`
- **Release Channel**: `UNSIGNED_EXPERIMENTAL`
- **Signature Status**: `OFFLINE_ROOT_SIGNATURE_PENDING` (Integrity secured via SHA-256)
- **Target Hardware**: Samsung Galaxy S21 (`SM-G991N` / `o1s` / Exynos 2100 / ARM Mali-G78 MP14)

---

## 2. Public Release Assets

| Asset Name | Public Download URL | SHA-256 Checksum | Size |
|---|---|---|---|
| **Mali Package Tarball** | [Download](https://github.com/uno-km/termux-diffusion/releases/download/v1.3.1-vulkan-mali-experimental/termux-diffusion-vulkan-prebuilt-v1.3.1-android-arm64-mali-compat-v2.tar.gz) | `65e4e305241b22385313e386afbcd12722061041280d00a44dfdc3ff23aa17b8` | 56,678,669 B |
| **Manifest** | [Download](https://github.com/uno-km/termux-diffusion/releases/download/v1.3.1-vulkan-mali-experimental/manifest-v1.3.1-vulkan-mali-experimental.json) | `00ded672b5c8bab0a3df443c0caf7d42000048aef8f1fd198267bec394eadcda` | 952 B |
| **SHA256SUMS** | [Download](https://github.com/uno-km/termux-diffusion/releases/download/v1.3.1-vulkan-mali-experimental/SHA256SUMS) | `d088d3e713849a094518df95019191ea87c72e3d56af153601d4be320691a0b7` | 658 B |

### Internal Binary Hashes (Verified upon Extraction)
- `bin/sd-cli-vulkan`: `1f10b3c91b34764cbeb79bc2a8360c8e2f1580cbd41d7160b028a0b512ced6db`
- `bin/v10-self-test`: `c60280d65e75e8c089325979973386754f6eff0b831d3d1eae91bb488f45e110`

---

## 3. Operator Instructions for One-Touch Installer & E2E

### Step 1: Clone or Pull feature/gpu
```bash
git clone https://github.com/uno-km/termux-diffusion.git
cd termux-diffusion
git switch feature/gpu
git pull --ff-only origin feature/gpu
```

### Step 2: Download & Verify Public Asset
```bash
curl -LO https://github.com/uno-km/termux-diffusion/releases/download/v1.3.1-vulkan-mali-experimental/termux-diffusion-vulkan-prebuilt-v1.3.1-android-arm64-mali-compat-v2.tar.gz
sha256sum termux-diffusion-vulkan-prebuilt-v1.3.1-android-arm64-mali-compat-v2.tar.gz
# Must match: 65e4e305241b22385313e386afbcd12722061041280d00a44dfdc3ff23aa17b8
```

### Step 3: Run Self-Tests & Smoke Test
```bash
mkdir -p staging_test && tar -xzf termux-diffusion-vulkan-prebuilt-v1.3.1-android-arm64-mali-compat-v2.tar.gz -C staging_test
export LD_LIBRARY_PATH=./staging_test/lib:$LD_LIBRARY_PATH
./staging_test/bin/v10-self-test
./staging_test/bin/sd-cli-vulkan --mode img_gen -m ~/.cache/termux-diffusion/models/sdxs.gguf --prompt "a beautiful flower" -W 256 -H 256 --steps 1 --seed 42 -o test.png
```

### Step 4: Downstream Rollout Matrix
1. **Galaxy A35 (Mali-G68)**: Test same package candidate (`mali-compat-v2`).
2. **Galaxy A34 (Mali-G68)**: Test same package candidate (`mali-compat-v2`).
3. **Galaxy S20**: Determine SoC (Exynos $\to$ Mali package, Snapdragon $\to$ Adreno package).
4. **PyPI / npm**: Maintain Stable CPU v1.3.0 as default; release GPU update only after offline root signature.
