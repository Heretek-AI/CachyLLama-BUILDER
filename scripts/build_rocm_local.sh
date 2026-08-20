#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Heretek AI
# =============================================================================
# CachyLLama-BUILDER: Local Linux ROCm Build Script
# =============================================================================
# Builds fewtarius/CachyLLama with ROCm/HIP acceleration locally on a Linux workstation.
#
# Usage:
#   ./scripts/build_rocm_local.sh [GFX_TARGET]
#
# Examples:
#   ./scripts/build_rocm_local.sh gfx1151   # Strix Halo (8060S)
#   ./scripts/build_rocm_local.sh gfx1150   # Strix Point (890M)
#   ./scripts/build_rocm_local.sh gfx1100   # RX 7900 XTX / 7900 XT
#   ./scripts/build_rocm_local.sh gfx1103   # Phoenix (780M / 7840U)
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
BUILD_DIR="$ROOT_DIR/build-rocm"
SRC_DIR="${SRC_DIR:-$ROOT_DIR/CachyLLama}"
ROCM_PATH="${ROCM_PATH:-/opt/rocm}"
GFX_TARGET="${1:-gfx1151}"

if [ ! -d "$SRC_DIR" ]; then
    echo "[INFO] CachyLLama source not found at $SRC_DIR. Cloning from GitHub..."
    git clone --depth 1 https://github.com/fewtarius/CachyLLama.git "$SRC_DIR"
fi

if [ ! -d "$ROCM_PATH" ]; then
    echo "[ERROR] ROCm toolchain directory not found at $ROCM_PATH."
    echo "[HINT] Install ROCm or download an AMD TheRock multi-arch nightly SDK into /opt/rocm."
    exit 1
fi

echo "========================================================================"
echo " Building CachyLLama (ROCm / HIP)"
echo " GFX Target:  $GFX_TARGET"
echo " ROCm Path:   $ROCM_PATH"
echo " Source Path: $SRC_DIR"
echo " Output Dir:  $BUILD_DIR"
echo "========================================================================"

mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

cmake "$SRC_DIR" -G Ninja \
    -DCMAKE_C_COMPILER="$ROCM_PATH/llvm/bin/clang" \
    -DCMAKE_CXX_COMPILER="$ROCM_PATH/llvm/bin/clang++" \
    -DCMAKE_CXX_FLAGS="-I$ROCM_PATH/include" \
    -DCMAKE_BUILD_TYPE=Release \
    -DGPU_TARGETS="$GFX_TARGET" \
    -DBUILD_SHARED_LIBS=ON \
    -DLLAMA_BUILD_TESTS=OFF \
    -DLLAMA_BUILD_TOOLS=ON \
    -DLLAMA_BUILD_SERVER=ON \
    -DGGML_HIP=ON \
    -DGGML_OPENMP=OFF \
    -DGGML_RPC=ON \
    -DGGML_HIP_ROCWMMA_FATTN=OFF \
    -DGGML_NATIVE=OFF \
    -DCMAKE_INSTALL_RPATH='$ORIGIN' \
    -DCMAKE_BUILD_WITH_INSTALL_RPATH=ON

ninja -j"$(nproc)"

echo "[OK] ROCm build completed successfully! Binaries are in: $BUILD_DIR/bin"
