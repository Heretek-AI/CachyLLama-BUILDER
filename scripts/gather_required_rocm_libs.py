#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Heretek AI
"""
===============================================================================
CachyLLama-BUILDER: ROCm Dynamic Runtime Library Harvester
===============================================================================
Inspects the ROCm SDK / toolchain directory and gathers all required dynamic
runtime libraries, shared objects, and data files (e.g., rocblas and hipblaslt
kernel code object libraries) into the destination binary directory.

This enables 100% portable, standalone binary distribution without requiring
end users to have ROCm installed on their host system.
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


# =============================================================================
# Core ROCm Runtime Library Patterns (Linux)
# =============================================================================
# These libraries are required by ggml-hip and CachyLLama executables.
LINUX_ROCM_PATTERNS = [
    "libhipblas.so*",               # HIP BLAS API wrapper
    "librocblas.so*",               # Core ROCm BLAS computational routines
    "libamdhip64.so*",              # AMD HIP runtime library
    "librocsolver.so*",             # ROCm LAPACK solvers
    "libroctx64.so*",               # ROCm code object tracking & profiling
    "libhipblaslt.so*",             # Lightweight GEMM / tensor operation library
    "librocprofiler-register.so*",   # Profiler registration hook
    "libamd_comgr.so*",             # AMD Code Object Manager (JIT / kernel loader)
    "libamd_comgr_loader.so*",      # Comgr stub loader
    "libhsa-runtime64.so*",         # Heterogeneous System Architecture runtime
    "librocroller.so*",             # Kernel execution scheduler
    "liborigami.so*",               # Optimized memory layouts
    "librocm_kpack.so*",            # ROCm kernel packaging
    "libLLVM.so*",                  # ROCm LLVM runtime (for runtime compilation)
    "libclang-cpp.so*",             # ROCm Clang runtime
]

# =============================================================================
# ROCm System Dependencies (Linux)
# =============================================================================
# Bundled by AMD TheRock multi-arch distribution to avoid host glibc / sysdep issues.
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

# =============================================================================
# Core ROCm Runtime DLL Patterns (Windows)
# =============================================================================
# Bundled into Windows build zip archives alongside llama-cli.exe & llama-server.exe.
WINDOWS_ROCM_PATTERNS = [
    "amdhip64_*.dll",               # HIP runtime DLL (versioned)
    "rocm_kpack.dll",               # Kernel pack loader
    "amd_comgr*.dll",               # Code Object Manager DLL
    "libhipblas.dll",               # HIP BLAS interface
    "rocblas.dll",                  # rocBLAS implementation
    "rocsolver.dll",                # rocSOLVER implementation
    "hipblaslt.dll",                # hipBLASLt interface
    "libhipblaslt.dll",             # hipBLASLt implementation
    "hipblas.dll",                  # Alternate hipblas naming
    "origami.dll",                  # Origami memory layout DLL
]


def copy_patterns(src_dir: Path, dest_dir: Path, patterns: list[str]) -> int:
    """
    Find files matching glob patterns in src_dir and copy them to dest_dir.
    Preserves symlinks when possible.
    """
    copied = 0
    if not src_dir.exists():
        return copied
    for pattern in patterns:
        for file_path in src_dir.glob(pattern):
            dest_file = dest_dir / file_path.name
            if file_path.is_file() or file_path.is_symlink():
                shutil.copy2(file_path, dest_file, follow_symlinks=False)
                print(f"[HARVEST] Copied: {file_path.name}")
                copied += 1
    return copied


def copy_directory(src_dir: Path, dest_dir: Path, name: str):
    """
    Recursively copy a directory tree (e.g. rocblas/library code objects).
    """
    target = src_dir / name
    if target.exists() and target.is_dir():
        dest = dest_dir / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(target, dest)
        print(f"[HARVEST] Copied directory tree: {name}")
    else:
        print(f"[WARN] Directory not found: {target}")


def main():
    parser = argparse.ArgumentParser(
        description="Gather required ROCm runtime libraries for standalone CachyLLama distribution."
    )
    parser.add_argument(
        "--rocm-dir",
        type=Path,
        default=Path("/opt/rocm"),
        help="ROCm root installation directory (default: /opt/rocm)",
    )
    parser.add_argument(
        "--dest-dir",
        type=Path,
        required=True,
        help="Destination directory where executables reside (e.g. CachyLLama/build/bin)",
    )
    parser.add_argument(
        "--platform",
        choices=["linux", "windows"],
        default="linux",
        help="Target operating system platform (linux or windows)",
    )
    args = parser.parse_args()

    rocm_dir: Path = args.rocm_dir
    dest_dir: Path = args.dest_dir
    dest_dir.mkdir(parents=True, exist_ok=True)

    print(f"[INFO] Harvesting ROCm dependencies: {rocm_dir} -> {dest_dir} (Platform: {args.platform})")

    if args.platform == "linux":
        lib_dir = rocm_dir / "lib"
        sysdeps_dir = rocm_dir / "lib" / "rocm_sysdeps" / "lib"
        llvm_lib_dir = rocm_dir / "lib" / "llvm" / "lib"

        copy_patterns(lib_dir, dest_dir, LINUX_ROCM_PATTERNS)
        copy_patterns(sysdeps_dir, dest_dir, LINUX_SYSDEP_PATTERNS)
        copy_patterns(llvm_lib_dir, dest_dir, ["libLLVM.so*", "libclang-cpp.so*"])

        # Copy data directories containing GPU architecture code objects
        copy_directory(rocm_dir / "lib" / "rocblas", dest_dir / "rocblas", "library")
        copy_directory(rocm_dir / "lib" / "hipblaslt", dest_dir / "hipblaslt", "library")

    elif args.platform == "windows":
        bin_dir = rocm_dir / "bin"
        copy_patterns(bin_dir, dest_dir, WINDOWS_ROCM_PATTERNS)
        copy_directory(bin_dir / "rocblas", dest_dir / "rocblas", "library")
        copy_directory(bin_dir / "hipblaslt", dest_dir / "hipblaslt", "library")

    print(f"[OK] ROCm library harvesting completed successfully for {dest_dir}")


if __name__ == "__main__":
    main()
