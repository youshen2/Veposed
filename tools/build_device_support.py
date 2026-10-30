import os
from pathlib import Path
import shutil


def executable(name):
    explicit = os.environ.get(name.upper().replace("-", "_"))
    found = explicit or shutil.which(name)
    for candidate in (
        found,
        f"/opt/homebrew/opt/llvm/bin/{name}",
        f"/usr/local/opt/llvm/bin/{name}",
    ):
        if candidate and Path(candidate).is_file():
            return candidate
    raise ValueError(f"Missing {name}; install LLVM or set {name.upper().replace('-', '_')}")
