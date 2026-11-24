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


# PR #39's correction tree is immutable. Keep its digest above pinned while
# current-source bindings move forward.
PR39_MERGE = "0615d10bcc446796d8f97603f72594c18d9fd26f"
FINAL_SOURCE_SHA = "25fff84e54dd4db8d4131f65fdebcc5941b1c90738f4ebef82d4612a705b3c44"


@cache
def correction_bytes(path: str) -> bytes:
    try:
        return subprocess.check_output(["git", "show", f"{PR39_MERGE}:{path}"], cwd=ROOT)
    except subprocess.CalledProcessError as error:
        raise RuntimeError(f"Final Batch 6 verification requires Git history containing {PR39_MERGE}") from error


PR40_MERGE = "cc155b1190c968a8fe5c8f5448f49ea50742feff"
PARTIAL_SOURCE_SHA = "fd20842916d8c0f28fb4be9dad7846f31cc39f792b6e21d5e0f60d8acdd11458"


@cache
def adjudication_bytes(path: str) -> bytes:
    try:
        return subprocess.check_output(["git", "show", f"{PR40_MERGE}:{path}"], cwd=ROOT)
    except subprocess.CalledProcessError as error:
        raise RuntimeError(f"Partial Batch 6 verification requires Git history containing {PR40_MERGE}") from error
