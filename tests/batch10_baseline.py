"""Immutable source pins for the Batch 10 correction and disposition."""
from functools import cache
import subprocess
from batch6_baseline import ROOT

PR47_MERGE = "15a389fb66c3cdc7459806b9cc104d56267161be"
PR48_MERGE = "bd03aeeade2b0a74cbcbc39e99f55fbbd0e26755"
BATCH10_SOURCE_SHA = "28fd210da6ec549d64d31b2aa79433843df3c04e6aeab3aa31b53ee5007c6dbd"
BATCH10_DISPOSITION_SOURCE_SHA = "fd76d2727545b202968664cbba4137537859536c979b3597ab943abd283858cf"


@cache
def batch10_base_bytes(path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{PR47_MERGE}:{path}"], cwd=ROOT)


@cache
def batch10_correction_bytes(path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{PR48_MERGE}:{path}"], cwd=ROOT)
