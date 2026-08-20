#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Heretek AI
# Local Vulkan build helper for CachyLLama

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
BUILD_DIR="$ROOT_DIR/build-vulkan"
SRC_DIR="${SRC_DIR:-$ROOT_DIR/CachyLLama}"

if [ ! -d "$SRC_DIR" ]; then
    echo "[INFO] Cloning fewtarius/CachyLLama..."
    git clone --depth 1 https://github.com/fewtarius/CachyLLama.git "$SRC_DIR"
fi

echo "[INFO] Building CachyLLama with Vulkan backend..."
echo "[INFO] Source: $SRC_DIR"
echo "[INFO] Build Dir: $BUILD_DIR"

mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

cmake "$SRC_DIR" -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DGGML_VULKAN=ON \
    -DGGML_CPU=ON \
    -DGGML_NATIVE=OFF \
    -DBUILD_SHARED_LIBS=ON \
    -DLLAMA_BUILD_TESTS=OFF \
    -DLLAMA_BUILD_TOOLS=ON \
    -DLLAMA_BUILD_SERVER=ON \
    -DGGML_RPC=ON \
    -DCMAKE_INSTALL_RPATH='$ORIGIN' \
    -DCMAKE_BUILD_WITH_INSTALL_RPATH=ON

ninja -j"$(nproc)"

echo "[OK] Vulkan build completed successfully in $BUILD_DIR/bin"
