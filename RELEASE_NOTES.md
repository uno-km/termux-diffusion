# Release Notes - termux-diffusion v1.6.9

**Release Tag**: `v1.6.9`  
**Distribution Channels**: PyPI (`termux-diffusion`), NPM (`termux-diffusion`), GitHub Releases  
**Target Platform**: Android Termux (ARM64 / aarch64 Bionic)  
**License**: Apache-2.0  

---

## Highlights & Key Architectural Changes

### 1. 100% Zero-Hardcoding Dynamic Provisioning Architecture
- **Purged Static Version Fallbacks**: Permanently eliminated static version strings (`v1.6.8`) from `index.js`.
- **Unified 3-Tier Resolution Protocol**:
  1. **Tier 1 (Explicit Environment Overrides)**: Prioritizes `TERMUX_DIFFUSION_RELEASE_BASE` and `TERMUX_DIFFUSION_RELEASE_TAG`.
  2. **Tier 2 (GitHub Releases Latest Canonical SSOT)**: Directly fetches canonical unversioned binaries (`sd-cli-cpu-android-arm64.tar.gz`, `libomp-android-arm64.so`) from `https://github.com/uno-km/termux-diffusion/releases/latest/download/`.
  3. **Tier 3 (Runtime Dynamic Version Resolution)**: Leverages dynamic `package.json` and `_version.py` version matching.
- **Dynamic HTTP Headers**: User-Agent headers dynamically bind to active runtime package versions.

### 2. Dual Engine Python & Node.js SSOT Synchronization
- **Node.js Zero-Touch Stream Provisioning**: Fast-track CPU baseline binaries are auto-provisioned seamlessly into `$PREFIX/bin` and `$PREFIX/lib`.
- **Full Packaging Parity**: Fully aligned `pyproject.toml`, `setup.py`, `package.json`, and `_version.py` to `1.6.9`.

---

## Detailed Changelog

### Changed
- `index.js`: Swapped hardcoded `v1.6.8` with dynamic `package.json` reading and prioritized latest release downloads.
- `termux_diffusion/installer.py`: Reordered prebuilt candidate URLs to place invariant latest download endpoint before versioned fallback.
- `setup.py`: Updated stale version string to `1.6.9`.
- `CHANGELOG.md`: Documented `v1.6.9` changes.
- Package manifests bumped to `1.6.9`.

### Removed
- Static release URL fragments referencing older version tags.
