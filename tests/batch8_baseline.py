"""Immutable PR #43 tree for Batch 8 evidence comparisons."""
from functools import cache
import subprocess

from batch6_baseline import ROOT

PR43_MERGE = "b7d97eca11e2382b01d8a09ca464f2f64da5caba"
BATCH8_SOURCE_SHA = "bf6e9a6ee4c32d4ae517c4f8a5d9eebadc0e0a2da3d2bf2398667c1525353e25"


@cache
def batch8_base_bytes(path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{PR43_MERGE}:{path}"], cwd=ROOT)


PR44_MERGE = "39b9c0d06a9df2d5efcf5d0e8b98d776e0d14353"
BATCH8_DISPOSITION_SOURCE_SHA = "108d443e3f39e745bddbcbb030de1876f36f328180308a32eae2cb107d133f80"


@cache
def corrected_batch8_bytes(path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{PR44_MERGE}:{path}"], cwd=ROOT)
