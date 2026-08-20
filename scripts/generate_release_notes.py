#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Heretek AI
"""
===============================================================================
CachyLLama-BUILDER: Release Notes & Checksum Generator
===============================================================================
Generates Markdown release notes for automated GitHub Releases, including:
- Upstream commit links (fewtarius/CachyLLama and fewtarius/llama-ai)
- Detected ROCm version from AMD TheRock multi-arch index
- Detailed description of targeted AMD APU & GPU architectures
- Computed SHA256 checksums and file size table for all built archives
"""

import argparse
import datetime
import hashlib
import os
from pathlib import Path


# Human-readable hardware descriptions for AMD GPU target architectures
GPU_TARGET_DESCRIPTIONS = {
    "gfx1151": "AMD Strix Halo (Ryzen AI Max+ 395 / Radeon 8060S - 128 GB Unified Memory)",
    "gfx1150": "AMD Strix Point (Ryzen AI 9 HX 370 / 365 / Radeon 890M / 880M)",
    "gfx120X": "AMD RDNA4 Architecture (gfx1200, gfx1201)",
    "gfx110X": "AMD RDNA3 Architecture (Radeon 780M / 760M / RX 7900 XTX / 7900 XT / 7800 XT)",
    "gfx103X": "AMD RDNA2 Architecture (Steam Deck / Van Gogh 0405 / 680M / RX 6000 series)",
    "gfx90a": "AMD CDNA2 Architecture (Instinct MI200 / MI250X Data Center Accelerators)",
    "gfx908": "AMD CDNA Architecture (Instinct MI100 Data Center Accelerators)",
}


def calculate_sha256(file_path: Path) -> str:
    """Compute SHA256 hex digest for a file efficiently in 64KB chunks."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def main():
    parser = argparse.ArgumentParser(description="Generate release notes for CachyLLama builds")
    parser.add_argument("--tag", required=True, help="Release tag (e.g., b1001)")
    parser.add_argument("--cachyllama-commit", default="latest", help="CachyLLama commit hash")
    parser.add_argument("--llama-ai-commit", default="latest", help="llama-ai commit hash")
    parser.add_argument("--rocm-version", default="N/A", help="ROCm version used (e.g. 7.14.0a20260612)")
    parser.add_argument("--targets", default="", help="Comma-separated GPU targets (e.g. gfx1151,gfx1150)")
    parser.add_argument("--os-list", default="windows,ubuntu", help="Comma-separated OS list")
    parser.add_argument("--artifacts-dir", type=Path, default=Path("."), help="Directory containing release archives")
    parser.add_argument("--output", type=Path, default=Path("release_notes.md"), help="Output markdown file")
    args = parser.parse_args()

    targets = [t.strip() for t in args.targets.split(",") if t.strip()]
    os_list = [o.strip() for o in args.os_list.split(",") if o.strip()]
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    lines = [
        f"# CachyLLama & llama-ai Release `{args.tag}`",
        "",
        f"**Build Date**: `{now}`  ",
        f"**CachyLLama Source**: [`{args.cachyllama_commit}`](https://github.com/fewtarius/CachyLLama/commit/{args.cachyllama_commit})  ",
    ]

    if args.llama_ai_commit != "latest":
        lines.append(f"**llama-ai Source**: [`{args.llama_ai_commit}`](https://github.com/fewtarius/llama-ai/commit/{args.llama_ai_commit})  ")

    if args.rocm_version != "N/A":
        lines.append(f"**ROCm Toolchain**: `{args.rocm_version}` (AMD TheRock Multi-Arch Nightly)")

    lines.extend([
        "",
        "## 🎮 Supported AMD GPU / APU Architectures",
        "",
    ])

    for target in targets:
        desc = GPU_TARGET_DESCRIPTIONS.get(target, "AMD GPU target")
        lines.append(f"- **`{target}`**: {desc}")

    lines.extend([
        "",
        "## 🚀 Highlights & Features in this Release",
        "- **Zero Host Dependencies**: Standalone binaries bundle all required runtime libraries (`rocblas`, `hipblaslt`, `amd_comgr`, DLLs/.so).",
        "- **$ORIGIN RPATH Portability**: Linux binaries dynamically link locally with zero system package collisions.",
        "- **CachyLLama APU Subsystems**: Persistent SSD-backed KV cache, MoE expert residency, DeepSeek-V4 Lightning Indexer, and dynamic prompt cache reuse.",
        "- **llama-ai Ready**: Fully compatible with the optimistic-first APU profile solver (`scripts/optimize.sh`) and `llama-run.sh`.",
        "",
    ])

    # Discover built archive files and generate SHA256 checksum table
    archive_files = list(args.artifacts_dir.glob("*.zip")) + list(args.artifacts_dir.glob("*.tar.gz"))
    if archive_files:
        lines.extend([
            "## 🔐 SHA256 Checksums",
            "",
            "| Filename | Size (MB) | SHA256 Checksum |",
            "| :--- | :---: | :--- |",
        ])
        for f in sorted(archive_files):
            size_mb = f.stat().st_size / (1024 * 1024)
            sha = calculate_sha256(f)
            lines.append(f"| `{f.name}` | {size_mb:.1f} MB | `{sha}` |")
        lines.append("")

    content = "\n".join(lines)
    args.output.write_text(content, encoding="utf-8")
    print(f"[OK] Generated release notes at {args.output}")


if __name__ == "__main__":
    main()
