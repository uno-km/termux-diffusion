#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ed25519 Manifest Signer & Verifier for termux-diffusion Release Engineering.
Validates manifest JSON against release-key-2026-01.
"""

import argparse
import sys
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.exceptions import InvalidSignature

# Embedded Public Key: release-key-2026-01
PUBLIC_KEY_HEX = "ea58ee6d830ca51164a3968c38e4abbad7fe39ebb761164821cba00524c15721"

def verify_manifest(manifest_path: Path, sig_path: Path) -> bool:
    manifest_bytes = manifest_path.read_bytes()
    sig_bytes = sig_path.read_bytes()
    
    if len(sig_bytes) != 64:
        print(f"[-] Invalid signature length: {len(sig_bytes)} bytes (expected 64)")
        return False
        
    pubkey = ed25519.Ed25519PublicKey.from_public_bytes(bytes.fromhex(PUBLIC_KEY_HEX))
    try:
        pubkey.verify(sig_bytes, manifest_bytes)
        print(f"[+] Signature VALID for {manifest_path.name} against key release-key-2026-01")
        return True
    except InvalidSignature:
        print(f"[-] Signature INVALID for {manifest_path.name}")
        return False

def sign_manifest(manifest_path: Path, private_key_path: Path, output_sig_path: Path):
    manifest_bytes = manifest_path.read_bytes()
    priv_bytes = private_key_path.read_bytes()
    
    if len(priv_bytes) == 32:
        privkey = ed25519.Ed25519PrivateKey.from_private_bytes(priv_bytes)
    elif len(priv_bytes) == 64:
        privkey = ed25519.Ed25519PrivateKey.from_private_bytes(priv_bytes[:32])
    else:
        # Try loading from hex string
        privkey = ed25519.Ed25519PrivateKey.from_private_bytes(bytes.fromhex(priv_bytes.decode('utf-8').strip()))
        
    sig = privkey.sign(manifest_bytes)
    output_sig_path.write_bytes(sig)
    print(f"[+] Successfully signed {manifest_path.name} -> {output_sig_path.name} ({len(sig)} bytes)")

def main():
    parser = argparse.ArgumentParser(description="Sign or verify termux-diffusion release manifests.")
    subparsers = parser.add_subparsers(dest="action", required=True)
    
    # Verify subparser
    ver_parser = subparsers.add_parser("verify")
    ver_parser.add_argument("manifest", type=Path, help="Path to manifest JSON")
    ver_parser.add_argument("signature", type=Path, help="Path to .sig file")
    
    # Sign subparser
    sign_parser = subparsers.add_parser("sign")
    sign_parser.add_argument("manifest", type=Path, help="Path to manifest JSON")
    sign_parser.add_argument("--key", type=Path, required=True, help="Path to offline Ed25519 private key")
    sign_parser.add_argument("--output", type=Path, required=False, help="Path to output .sig file")
    
    args = parser.parse_args()
    if args.action == "verify":
        ok = verify_manifest(args.manifest, args.signature)
        sys.exit(0 if ok else 1)
    elif args.action == "sign":
        out_sig = args.output or args.manifest.with_suffix(args.manifest.suffix + ".sig")
        sign_manifest(args.manifest, args.key, out_sig)

if __name__ == "__main__":
    main()
