# AGENTS.md

Technical reference and operational guidelines for AI agents (and human maintainers) working on **CachyLLama-BUILDER**.

---

## 🧭 Repository Mission & Architecture

**CachyLLama-BUILDER** is an automated CI/CD and release orchestration repository for:
1. **[fewtarius/CachyLLama](https://github.com/fewtarius/CachyLLama)** — High-performance AMD APU/GPU-optimized fork of [llama.cpp](https://github.com/ggml-org/llama.cpp) featuring persistent SSD-backed KV cache, MoE expert residency, DeepSeek-V4 Lightning Indexer, and dynamic prompt cache reuse.
2. **[fewtarius/llama-ai](https://github.com/fewtarius/llama-ai)** — Autonomous APU/GPU runtime orchestrator with runtime solver (`scripts/optimize.sh`), `llama-run.sh`, systemd service definitions, and automated hardware detection.

This repository is modeled after the dual architecture of [lemonade-sdk/llamacpp-rocm](https://github.com/lemonade-sdk/llamacpp-rocm) and [lemonade-sdk/llama.cpp](https://github.com/lemonade-sdk/llama.cpp).

```
CachyLLama-BUILDER/
├── .github/
│   ├── workflows/
│   │   ├── build-cachyllama-rocm.yml      # Dedicated ROCm nightly multi-arch builder (TheRock)
│   │   ├── build-cachyllama-all.yml       # Multi-backend release (Vulkan, CPU, CUDA, Metal)
│   │   ├── build-llama-ai-bundle.yml      # Turnkey llama-ai distribution bundler
│   │   └── test-cachyllama-rocm.yml       # Post-build smoke & GPU offload test harness
│   ├── actions/
│   │   ├── get-tag-name/                  # Resolves next sequential release tag (bXXXX)
│   │   └── test-cachyllama-build/         # Cross-platform GGUF execution test
│   └── ISSUE_TEMPLATE/                    # Bug report and feature request forms
├── scripts/
│   ├── gather_required_rocm_libs.py       # Transitive ROCm library harvester
│   ├── generate_release_notes.py          # Markdown release notes with SHA256 tables
│   ├── build_rocm_local.sh                # Local Linux ROCm build script
│   └── build_vulkan_local.sh              # Local Linux Vulkan build script
├── README.md                              # Public SEO and user documentation
├── AGENTS.md                              # Core agent operational guidelines (this file)
├── CLAUDE.md                              # Claude Code instructions
├── GEMINI.md                              # Gemini / Antigravity instructions
├── LICENSE                                # MIT License
└── .gitignore                             # Clean build and submodule isolation
```

---

## 🛠️ Workflows & CI Architecture

### 1. `build-cachyllama-rocm.yml` (TheRock Multi-Arch Standalone)
- **Schedule**: `0 13 * * *` (1:00 PM UTC / 5:00 AM PST, ~2 hours after daily AMD TheRock tarballs publish).
- **Matrix OS**: Ubuntu 22.04 (`ubuntu-22.04`).
- **Matrix Targets**: `gfx1151`, `gfx1150`, `gfx120X`, `gfx110X`, `gfx103X`, `gfx90a`, `gfx908`.
- **Target Mappings**:
  - `gfx110X` ➔ `gfx1100;gfx1101;gfx1102;gfx1103`
  - `gfx103X` ➔ `gfx1030;gfx1031;gfx1032;gfx1034`
  - `gfx120X` ➔ `gfx1200;gfx1201`
  - `gfx1151` ➔ `gfx1151`
  - `gfx1150` ➔ `gfx1150`
- **AMD TheRock Scraping**: Fetches `https://rocm.nightlies.amd.com/tarball-multi-arch/` and extracts `const files = [...]` JSON to find newest `YYYYMMDD` build date matching `therock-dist-linux-<target>-<version>.tar.gz`.
- **Portability Layer**:
  - Linux: Copies `.so` libraries, `librocm_sysdeps_*`, `rocblas/library`, `hipblaslt/library`, and executes `patchelf --set-rpath '$ORIGIN' "$file"`.

### 2. `build-cachyllama-all.yml` (Multi-Backend Release)
- **Schedule**: `0 2 * * *` (2:00 AM UTC).
- **Backends**:
  - **Linux Vulkan (x64)**: Uses `-DGGML_VULKAN=ON` (RADV driver priority for AMD APUs).
  - **Linux CPU (x64 / ARM64)**: OpenMP, AVX2, AVX512 variants.
  - **Linux CUDA**: Architectures `sm_75`, `sm_80`, `sm_86`, `sm_89`, `sm_90`, `sm_100`, `sm_120`, `sm_121`.

### 3. `build-llama-ai-bundle.yml` (Turnkey Distribution)
- Assembles `fewtarius/llama-ai` with pre-compiled CachyLLama binaries, the solver (`scripts/optimize.sh`), `llama-run.sh`, and systemd units.
- Generates ready-to-run release archive: `llama-ai-${TAG}-linux-x64.tar.gz`.

---

## 🏷️ Release Tagging Convention

- **Format**: `bXXXX` (sequential 4-digit build numbers, e.g. `b1001`, `b1002`).
- **Resolver**: The `.github/actions/get-tag-name` composite action checks `gh release list` and `git tag -l` to find the highest number and increments it by 1.
- **Asset Pattern**:
  - ROCm: `cachy-llama-${TAG}-ubuntu-rocm-${target}-x64.zip`
  - Vulkan: `cachy-llama-${TAG}-bin-ubuntu-vulkan-x64.tar.gz`
  - llama-ai Bundle: `llama-ai-${TAG}-linux-x64.tar.gz`

---

## 📋 Agent Operational Guidelines

1. **Maintain CMake and ROCm Flags**:
   - Always ensure `-DGGML_HIP=ON`, `-DLLAMA_BUILD_SERVER=ON`, `-DLLAMA_BUILD_TOOLS=ON`, `-DGGML_RPC=ON`, and `-DCMAKE_INSTALL_RPATH='$ORIGIN'` are preserved when modifying ROCm workflows.
2. **Verify Script Syntax Before Committing**:
   - Always run `python3 -m py_compile scripts/*.py` and `bash -n scripts/*.sh`.
   - Always run `yaml.safe_load` on modified `.github/workflows/*.yml` files.
3. **Clean Submodule Handling**:
   - Local subfolders `CachyLLama/`, `llama-ai/`, `llama.cpp/`, `llamacpp-rocm/` are gitignored to allow local development and inspection without polluting the builder git repository.
