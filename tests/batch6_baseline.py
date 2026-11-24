"""Read immutable Batch 5 post-state evidence from the parent Git history."""
import subprocess
from functools import cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE_COMMIT = "5061755c9fbaf88c5ea9a07e406de7366798940f"
CURRENT_SOURCE_SHA = "1562471af6710a1a4c46e7409131abf7e55d2953262e88f652a2fb0167b73061"


@cache
def baseline_bytes(path: str) -> bytes:
    try:
        return subprocess.check_output(["git", "show", f"{BASELINE_COMMIT}:{path}"], cwd=ROOT)
    except subprocess.CalledProcessError as error:
        raise RuntimeError(f"Batch 6 requires Git history containing {BASELINE_COMMIT}") from error
