# CachyLLama-BUILDER 🚀

Automated nightly builds, multi-backend packaging, and release automation for **[fewtarius/CachyLLama](https://github.com/fewtarius/CachyLLama)** and **[fewtarius/llama-ai](https://github.com/fewtarius/llama-ai)**.

Modeled after the architecture of [lemonade-sdk/llamacpp-rocm](https://github.com/lemonade-sdk/llamacpp-rocm) and [lemonade-sdk/llama.cpp](https://github.com/lemonade-sdk/llama.cpp), this repository delivers portable, self-contained binaries optimized for AMD APUs (Strix Halo, Strix Point, Phoenix, Steam Deck) and discrete GPUs, as well as multi-backend builds (Vulkan RADV, CUDA, Apple Metal, CPU).

---

## 🌟 Highlights

- **Zero Host ROCm Dependency**: Standalone Linux and Windows packages bundle all required ROCm runtime libraries (`rocblas`, `hipblaslt`, `amdhip64`, `libamd_comgr`, etc.) with `RPATH=$ORIGIN` patchelf configurations.
- **Nightly AMD TheRock Integration**: Automatically pulls the newest daily ROCm toolchains from `https://rocm.nightlies.amd.com/tarball-multi-arch`.
- **Comprehensive GPU / APU Target Matrix**:
  - `gfx1151`: AMD Strix Halo (Ryzen AI Max+ 395 / Radeon 8060S)
  - `gfx1150`: AMD Strix Point (Ryzen AI 9 HX 370 / Radeon 890M)
  - `gfx120X`: AMD RDNA4 (gfx1200, gfx1201)
  - `gfx110X`: AMD RDNA3 (Radeon 780M, RX 7900 XTX / 7900 XT / 7800 XT / 7700 XT)
  - `gfx103X`: AMD RDNA2 (Steam Deck / Van Gogh 0405, 680M, RX 6000 series)
  - `gfx90a`, `gfx908`: AMD CDNA / CDNA2 datacenter accelerators (MI100 / MI200)
- **Turnkey `llama-ai` Bundles**: Pre-packaged distribution archives combining `fewtarius/llama-ai`, the runtime solver (`scripts/optimize.sh`), `llama-run.sh`, systemd service definitions, and pre-compiled CachyLLama binaries.
- **Vulkan RADV Backend**: Optimized for rock-solid stability on Linux AMD APUs without requiring ROCm kernel drivers.
- **Automated GitHub Releases**: Builds on a nightly schedule (1:00 PM UTC / 5:00 AM PST) with sequential `bXXXX` release tagging.

---

## 📦 Download & Quick Start

### 1. Using Turnkey `llama-ai` Bundle (Recommended for APU Users)

Download the latest release bundle from [GitHub Releases](../../releases):

```bash
# Extract the release bundle
tar -xzf llama-ai-b1001-linux-x64.tar.gz
cd llama-ai

# Start the server (auto-detects hardware and solver profile)
./llama-run.sh --server

# Or specify a model and backend
./llama-run.sh --server path/to/model.gguf --backend vulkan
```

### 2. Using Standalone CachyLLama Binaries

Download the appropriate archive for your operating system and GPU target:

- **Linux ROCm (Strix Halo)**: `cachy-llama-bXXXX-ubuntu-rocm-gfx1151-x64.zip`
- **Linux ROCm (Strix Point)**: `cachy-llama-bXXXX-ubuntu-rocm-gfx1150-x64.zip`
- **Linux ROCm (Phoenix / 780M)**: `cachy-llama-bXXXX-ubuntu-rocm-gfx110X-x64.zip`
- **Linux Vulkan (Universal APU)**: `cachy-llama-bXXXX-bin-ubuntu-vulkan-x64.tar.gz`
- **Windows ROCm (Strix Halo)**: `cachy-llama-bXXXX-windows-rocm-gfx1151-x64.zip`
- **macOS Metal (Apple Silicon)**: `cachy-llama-bXXXX-bin-macos-arm64.tar.gz`

Extract and run directly:
```bash
unzip cachy-llama-b1001-ubuntu-rocm-gfx1151-x64.zip -d cachy-llama
cd cachy-llama
./llama-cli -m /path/to/model.gguf -ngl 99 -p "Hello CachyLLama!"
```

---

## 🛠️ GitHub Actions Workflows

| Workflow | Schedule / Triggers | Description |
| :--- | :--- | :--- |
| **`build-cachyllama-rocm.yml`** | `0 13 * * *` (Daily) / Manual | Multi-arch Windows & Ubuntu ROCm builds with AMD TheRock tarballs & bundled dependencies. |
| **`build-cachyllama-all.yml`** | `0 */12 * * *` / Manual | Multi-backend release matrix (Linux Vulkan, Linux CPU x64/arm64, Linux CUDA sm_75..sm_121, Windows CPU/CUDA, macOS Metal). |
| **`build-llama-ai-bundle.yml`** | Post-CachyLLama / Manual | Turnkey `llama-ai` package assembly with solver, runner scripts, and prebuilt binaries. |
| **`test-cachyllama-rocm.yml`** | Post-Build / Manual | Automated smoke testing of release artifacts with small GGUF models on self-hosted or standard runners. |

### Manual Dispatch Inputs

Every workflow supports manual execution via the **Actions** tab with configurable inputs:
- `operating_systems`: comma-separated list (`windows,ubuntu`)
- `gfx_target`: AMD GPU architectures (`gfx1151,gfx1150,gfx120X,gfx110X,gfx103X,gfx90a,gfx908`)
- `rocm_version`: ROCm version string or `latest` (auto-detected from AMD TheRock multi-arch index)
- `cachyllama_version`: branch, tag, or commit hash in `fewtarius/CachyLLama` (default: `master`)
- `create_release`: boolean (`true`/`false`) to publish a GitHub release

---

## ⚙️ Repository Setup & Maintenance

### Permissions
Workflows use `permissions: contents: write` to publish GitHub Releases automatically. Ensure GitHub Actions has **Read and write permissions** in:
`Settings -> Actions -> General -> Workflow permissions`.

### Secrets (Optional)
- `GH_TOKEN`: Optional Personal Access Token (PAT) if you wish to trigger downstream workflows in other repositories or push cross-organization releases. If not provided, the workflow falls back seamlessly to standard `github.token`.

---

## 💻 Local Build Scripts

Helper scripts are provided in the `scripts/` directory for developer testing:

```bash
# Build ROCm backend locally on Linux
./scripts/build_rocm_local.sh --target gfx1151

# Build Vulkan backend locally on Linux
./scripts/build_vulkan_local.sh

# Inspect and gather dynamic ROCm library dependencies
python3 scripts/gather_required_rocm_libs.py --rocm-dir /opt/rocm --dest-dir ./build/bin
```

---

## 📄 License

This builder automation repository is licensed under the [MIT License](LICENSE).
The upstream projects [fewtarius/CachyLLama](https://github.com/fewtarius/CachyLLama) and [fewtarius/llama-ai](https://github.com/fewtarius/llama-ai) are licensed under their respective open-source licenses (GPL-3.0 / MIT).
