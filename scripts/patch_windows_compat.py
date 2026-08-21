#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Heretek AI
"""
patch_windows_compat.py: Apply Windows compatibility patches to CachyLLama source tree.

Addresses POSIX-only headers and functions (<sys/mman.h>, <unistd.h>, getpagesize(),
madvise(), POSIX mkdir) when building on MSVC or Clang on Windows.
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def patch_file(path: Path, replacements: list[tuple[str, str]]) -> bool:
    if not path.exists():
        print(f"[-] File not found: {path}")
        return False

    content = path.read_text(encoding="utf-8")
    original = content

    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
        else:
            print(f"[!] Warning: target substring not found in {path.name}: {old[:40]}...")

    if content != original:
        path.write_text(content, encoding="utf-8")
        print(f"[+] Patched {path}")
        return True
    else:
        print(f"[*] No changes applied to {path}")
        return False


def main():
    target_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "CachyLLama")
    if not target_dir.is_dir():
        print(f"[-] Error: directory '{target_dir}' does not exist.")
        sys.exit(1)

    print(f"[>] Patching CachyLLama source tree in: {target_dir.resolve()}")

    # 1. Patch src/llama-moe-residency.cpp
    residency_cpp = target_dir / "src" / "llama-moe-residency.cpp"
    patch_file(
        residency_cpp,
        [
            (
                '#include <sys/mman.h>\n#include <unistd.h>',
                '#ifndef _WIN32\n#include <sys/mman.h>\n#include <unistd.h>\n#else\n#include <windows.h>\n#include <memoryapi.h>\nstatic inline size_t getpagesize() {\n    SYSTEM_INFO si;\n    GetSystemInfo(&si);\n    return si.dwPageSize ? (size_t)si.dwPageSize : (size_t)4096;\n}\n#endif',
            ),
            (
                '(void) madvise(reinterpret_cast<void *>(page_start), aligned_len, advice);',
                '#ifndef _WIN32\n    (void) madvise(reinterpret_cast<void *>(page_start), aligned_len, advice);\n#else\n    (void)page_start;\n    (void)aligned_len;\n    (void)advice;\n#endif',
            ),
        ],
    )

    # 2. Patch src/llama-moe-coact.cpp
    coact_cpp = target_dir / "src" / "llama-moe-coact.cpp"
    patch_file(
        coact_cpp,
        [
            (
                '#include "llama-moe-coact.h"',
                '#include "llama-moe-coact.h"\n#ifdef _WIN32\n#include <direct.h>\n#define mkdir(dir, mode) _mkdir(dir)\n#else\n#include <sys/stat.h>\n#endif',
            ),
        ],
    )

    print("[+] CachyLLama Windows compatibility patch completed successfully.")


if __name__ == "__main__":
    main()
