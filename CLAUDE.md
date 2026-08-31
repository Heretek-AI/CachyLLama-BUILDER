# CLAUDE.md

Guidelines and command reference for Anthropic's Claude Code agent in **CachyLLama-BUILDER**.

---

## ⚡ Essential Commands

### Syntax & Workflow Linting
```bash
# Validate all GitHub Actions workflow and action YAML files
python3 -c "import yaml, glob; [yaml.safe_load(open(f)) for f in glob.glob('.github/workflows/*.yml') + glob.glob('.github/actions/**/*.yml', recursive=True)]"

# Validate Python helper scripts
python3 -m py_compile scripts/*.py

# Validate Bash scripts
bash -n scripts/*.sh
```

### Local Build Simulation
```bash
# Build CachyLLama with ROCm locally (Linux)
./scripts/build_rocm_local.sh gfx1151

# Build CachyLLama with Vulkan locally (Linux)
./scripts/build_vulkan_local.sh

# Harvest ROCm dynamic libraries from local installation
python3 scripts/gather_required_rocm_libs.py --rocm-dir /opt/rocm --dest-dir ./build/bin --platform linux

# Dry-run release notes generation
python3 scripts/generate_release_notes.py --tag b1001 --cachyllama-commit master --rocm-version "7.14.0" --targets "gfx1151,gfx1150,gfx110X" --output test_notes.md
```

### GitHub CLI Release Management
```bash
# List releases
gh release list

# Trigger nightly ROCm build workflow manually
gh workflow run build-cachyllama-rocm.yml -f operating_systems=ubuntu -f gfx_target=gfx1151,gfx1150,gfx110X

# Trigger multi-backend release workflow manually
gh workflow run build-cachyllama-all.yml

# Trigger llama-ai turnkey bundle build
gh workflow run build-llama-ai-bundle.yml
```

---

## 📐 Code Style & Conventions

- **GitHub Actions Workflows**: Use clean YAML with explicit step names, strict error trapping (`set -euo pipefail`), and matrix outputs. Keep matrix targets alphabetically or hierarchically sorted.
- **Shell Scripts**: Always start with `set -euo pipefail`. Use `$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)` for resilient path resolution.
- **Python Scripts**: Standard library only (no external pip dependencies in builder helper scripts like `gather_required_rocm_libs.py` or `generate_release_notes.py`).
- **Git Hygiene**: Keep repository lightweight. Do not commit `.zip`, `.tar.gz`, `.gguf`, or binary files. Keep local checkouts (`CachyLLama/`, `llama-ai/`) gitignored.
