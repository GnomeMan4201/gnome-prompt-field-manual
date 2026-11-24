"""Immutable PR #43 tree for Batch 8 evidence comparisons."""
from functools import cache
import subprocess

from batch6_baseline import ROOT

PR43_MERGE = "b7d97eca11e2382b01d8a09ca464f2f64da5caba"
BATCH8_SOURCE_SHA = "8cd1a08d1763506dcd2c567fb116a34ea9527b8ac862f63592f3c4a6dfdc448f"


@cache
def batch8_base_bytes(path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{PR43_MERGE}:{path}"], cwd=ROOT)
