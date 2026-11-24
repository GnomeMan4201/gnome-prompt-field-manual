"""Pinned Batch 9 disposition and Batch 10 correction source."""
from functools import cache
import subprocess
from batch6_baseline import ROOT
PR47_MERGE = "15a389fb66c3cdc7459806b9cc104d56267161be"
BATCH10_SOURCE_SHA = "28fd210da6ec549d64d31b2aa79433843df3c04e6aeab3aa31b53ee5007c6dbd"

@cache
def batch10_base_bytes(path):
    return subprocess.check_output(["git", "show", f"{PR47_MERGE}:{path}"], cwd=ROOT)
