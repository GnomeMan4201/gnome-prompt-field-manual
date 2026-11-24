"""Immutable PR #46 correction and the Batch 9 disposition source digest."""
from functools import cache
import subprocess

from batch6_baseline import ROOT

PR46_MERGE = "859658e479206ed3311629190a0f2f5e7e410b2d"
BATCH9_SOURCE_SHA = "8e3ec363f32f200ac8b01f479986043a9854a8b4868efec8497b62a4288403d6"
BATCH9_DISPOSITION_SOURCE_SHA = "208211b102aa75bf9f35fefbd2c33cf7f89365a8468058abd8567b8b442937d6"


@cache
def batch9_correction_bytes(path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{PR46_MERGE}:{path}"], cwd=ROOT)
