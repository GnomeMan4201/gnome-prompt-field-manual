"""Immutable pre-Batch-7 tree for historical checks and scoped page comparisons."""
from functools import cache
import subprocess

from batch6_baseline import ROOT

PR41_MERGE = "c93608da305eb70e231613403edb8a275d7e1bbe"
BATCH7_SOURCE_SHA = "8ba47c93f4561c0daffa6bfce5d16401cded9f34a887bd8f300bcea38612e084"


@cache
def merged_disposition_bytes(path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{PR41_MERGE}:{path}"], cwd=ROOT)
