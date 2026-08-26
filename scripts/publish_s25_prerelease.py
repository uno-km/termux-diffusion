#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Pre-release Publisher for termux-diffusion v1.3.1-vulkan-experimental.
Uploads the 4 official candidate assets to GitHub Pre-release.
"""

import argparse
import subprocess
import sys
from pathlib import Path

TARGET_TAG = "v1.3.1-vulkan-experimental"
TARGET_TITLE = "Termux-Diffusion v1.3.1 (Experimental Adreno Vulkan Pre-release)"

REQUIRED_ASSETS = [
    "termux-diffusion-vulkan-prebuilt-v1.3.1-android-arm64-adreno.tar.gz",
    "manifest-v1.3.1-vulkan-experimental.json",
    "manifest-v1.3.1-vulkan-experimental.json.sig",
    "SHA256SUMS"
]

def publish_prerelease(asset_dir: Path, notes_file: Path):
    print(f"[*] Validating release assets in {asset_dir}...")
    for asset in REQUIRED_ASSETS:
        p = asset_dir / asset
        if not p.exists():
            print(f"[-] Missing required asset: {asset}")
            sys.exit(1)
        print(f"  [+] Found: {asset} ({p.stat().st_size} bytes)")
        
    print(f"[*] Creating GitHub Pre-release {TARGET_TAG}...")
    notes_arg = f"--notes-file {notes_file}" if notes_file and notes_file.exists() else f"--notes \"Experimental Adreno Vulkan prebuilt release for Galaxy S25\""
    
    asset_paths = " ".join([f'"{asset_dir / asset}"' for asset in REQUIRED_ASSETS])
    
    cmd = (
        f"gh release create {TARGET_TAG} {asset_paths} "
        f"--title \"{TARGET_TITLE}\" "
        f"--prerelease {notes_arg}"
    )
    print(f"Executing: {cmd}")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.returncode == 0:
        print(f"[+] GitHub Pre-release {TARGET_TAG} created successfully!\n{res.stdout}")
    else:
        print(f"[-] Release creation failed (RC={res.returncode}):\n{res.stderr}")
        sys.exit(res.returncode)

def main():
    parser = argparse.ArgumentParser(description="Publish termux-diffusion experimental pre-release.")
    parser.add_argument("--asset-dir", type=Path, default=Path("dist_vulkan"), help="Path to assets directory")
    parser.add_argument("--notes", type=Path, default=Path("docs/handover/GALAXY_S25_ADRENO_VULKAN_RELEASE_HANDOVER.md"), help="Path to release notes")
    args = parser.parse_args()
    
    publish_prerelease(args.asset_dir, args.notes)

if __name__ == "__main__":
    main()
