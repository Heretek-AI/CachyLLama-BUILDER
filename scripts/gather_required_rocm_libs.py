#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Heretek AI
"""
Inspect binaries/shared libraries and gather all required ROCm runtime libraries.
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


# Core ROCm library patterns commonly needed for portable distribution
LINUX_ROCM_PATTERNS = [
    "libhipblas.so*",
    "librocblas.so*",
    "libamdhip64.so*",
    "librocsolver.so*",
    "libroctx64.so*",
    "libhipblaslt.so*",
    "librocprofiler-register.so*",
    "libamd_comgr.so*",
    "libamd_comgr_loader.so*",
    "libhsa-runtime64.so*",
    "librocroller.so*",
    "liborigami.so*",
    "librocm_kpack.so*",
    "libLLVM.so*",
    "libclang-cpp.so*",
]

LINUX_SYSDEP_PATTERNS = [
    "librocm_sysdeps_liblzma.so*",
    "librocm_sysdeps_numa.so*",
    "librocm_sysdeps_z.so*",
    "librocm_sysdeps_zstd.so*",
    "librocm_sysdeps_elf.so*",
    "librocm_sysdeps_drm.so*",
    "librocm_sysdeps_drm_amdgpu.so*",
    "librocm_sysdeps_bz2.so*",
]

WINDOWS_ROCM_PATTERNS = [
    "amdhip64_*.dll",
    "rocm_kpack.dll",
    "amd_comgr*.dll",
    "libhipblas.dll",
    "rocblas.dll",
    "rocsolver.dll",
    "hipblaslt.dll",
    "libhipblaslt.dll",
    "hipblas.dll",
    "origami.dll",
]


def copy_patterns(src_dir: Path, dest_dir: Path, patterns: list[str]) -> int:
    copied = 0
    if not src_dir.exists():
        return copied
    for pattern in patterns:
        for file_path in src_dir.glob(pattern):
            dest_file = dest_dir / file_path.name
            if file_path.is_file() or file_path.is_symlink():
                shutil.copy2(file_path, dest_file, follow_symlinks=False)
                print(f"Copied: {file_path.name}")
                copied += 1
    return copied


def copy_directory(src_dir: Path, dest_dir: Path, name: str):
    target = src_dir / name
    if target.exists() and target.is_dir():
        dest = dest_dir / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(target, dest)
        print(f"Copied directory tree: {name}")
    else:
        print(f"Directory not found: {target}")


def main():
    parser = argparse.ArgumentParser(description="Gather required ROCm runtime libraries into build destination.")
    parser.add_argument("--rocm-dir", type=Path, default=Path("/opt/rocm"), help="ROCm installation directory")
    parser.add_argument("--dest-dir", type=Path, required=True, help="Destination directory (e.g. build/bin)")
    parser.add_argument("--platform", choices=["linux", "windows"], default="linux", help="Target platform")
    args = parser.parse_args()

    rocm_dir: Path = args.rocm_dir
    dest_dir: Path = args.dest_dir
    dest_dir.mkdir(parents=True, exist_ok=True)

    print(f"Gathering ROCm libraries from {rocm_dir} -> {dest_dir} ({args.platform})")

    if args.platform == "linux":
        lib_dir = rocm_dir / "lib"
        sysdeps_dir = rocm_dir / "lib" / "rocm_sysdeps" / "lib"
        llvm_lib_dir = rocm_dir / "lib" / "llvm" / "lib"

        copy_patterns(lib_dir, dest_dir, LINUX_ROCM_PATTERNS)
        copy_patterns(sysdeps_dir, dest_dir, LINUX_SYSDEP_PATTERNS)
        copy_patterns(llvm_lib_dir, dest_dir, ["libLLVM.so*", "libclang-cpp.so*"])

        # Copy data directories
        copy_directory(rocm_dir / "lib" / "rocblas", dest_dir / "rocblas", "library")
        copy_directory(rocm_dir / "lib" / "hipblaslt", dest_dir / "hipblaslt", "library")

    elif args.platform == "windows":
        bin_dir = rocm_dir / "bin"
        copy_patterns(bin_dir, dest_dir, WINDOWS_ROCM_PATTERNS)
        copy_directory(bin_dir / "rocblas", dest_dir / "rocblas", "library")
        copy_directory(bin_dir / "hipblaslt", dest_dir / "hipblaslt", "library")

    print(f"ROCm library collection complete for {dest_dir}")


if __name__ == "__main__":
    main()
