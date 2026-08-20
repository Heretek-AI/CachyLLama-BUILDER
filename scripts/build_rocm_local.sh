#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Heretek AI
# Local ROCm build helper for CachyLLama

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
BUILD_DIR="$ROOT_DIR/build-rocm"
SRC_DIR="${SRC_DIR:-$ROOT_DIR/CachyLLama}"
ROCM_PATH="${ROCM_PATH:-/opt/rocm}"
GFX_TARGET="${1:-gfx1151}"

if [ ! -d "$SRC_DIR" ]; then
    echo "[INFO] Cloning fewtarius/CachyLLama..."
    git clone --depth 1 https://github.com/fewtarius/CachyLLama.git "$SRC_DIR"
fi

echo "[INFO] Building CachyLLama with ROCm for target: $GFX_TARGET"
echo "[INFO] ROCm Path: $ROCM_PATH"
echo "[INFO] Source: $SRC_DIR"
echo "[INFO] Build Dir: $BUILD_DIR"

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

echo "[OK] Build completed successfully in $BUILD_DIR/bin"
