"""Immutable PR #43 tree for Batch 8 evidence comparisons."""
from functools import cache
import subprocess

from batch6_baseline import ROOT

PR43_MERGE = "b7d97eca11e2382b01d8a09ca464f2f64da5caba"
BATCH8_SOURCE_SHA = "bf6e9a6ee4c32d4ae517c4f8a5d9eebadc0e0a2da3d2bf2398667c1525353e25"


@cache
def batch8_base_bytes(path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{PR43_MERGE}:{path}"], cwd=ROOT)
