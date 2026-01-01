import os
import shutil
from pathlib import Path

def resolve_path(path: str, base_dir: str = None) -> Path:
    """Resolve a path relative to a base directory if it's not absolute."""
    p = Path(path)
    if p.is_absolute():
        return p
    if base_dir:
        return Path(base_dir) / p
    return p.absolute()

def ensure_dir(path: Path):
    """Ensure a directory exists."""
    path.mkdir(parents=True, exist_ok=True)

def has_aria2() -> bool:
    """Check if aria2c is available in the system path."""
    return shutil.which("aria2c") is not None
