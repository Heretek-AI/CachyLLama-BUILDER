# GEMINI.md

Developer reference for Google Gemini / Antigravity agents working in **CachyLLama-BUILDER**.

---

## 🤖 Antigravity & Gemini Operational Protocols

### Workspace Context
- **Repository**: `Heretek-AI/CachyLLama-BUILDER`
- **Upstream Targets**:
  - `fewtarius/CachyLLama` (C++ inference engine fork)
  - `fewtarius/llama-ai` (APU/GPU orchestrator and solver)
- **Reference Architectures**:
  - `lemonade-sdk/llamacpp-rocm`
  - `lemonade-sdk/llama.cpp`

### Core Development Principles
1. **Never Break CI Portability**: Standalone binaries must function without system-installed ROCm or CUDA drivers by bundling all required DLLs/shared objects and setting `RPATH=$ORIGIN`.
2. **AMD APU Priority**: Strix Halo (`gfx1151`), Strix Point (`gfx1150`), and Phoenix (`gfx110X`) are primary targets. Always test that shader compile flags, subgroup configurations, and memory allocators align with CachyLLama defaults.
3. **Keep Toolchain Pinned on Windows**: Maintain `windows-2022` for ROCm builds due to the MSVC 14.51 `<cmath>` header collision.
4. **Planning Protocol**: For complex workflow restructuring, always use the `/plan` workflow: create a detailed implementation plan artifact, seek user review, verify with automated checks, and generate a walkthrough.

### Quick Verification Suite
```bash
# Validate YAML workflow schemas
python3 -c "import yaml, glob; [yaml.safe_load(open(f)) for f in glob.glob('.github/workflows/*.yml') + glob.glob('.github/actions/**/*.yml', recursive=True)]"

# Check Python and shell scripts
python3 -m py_compile scripts/*.py && bash -n scripts/*.sh
```
