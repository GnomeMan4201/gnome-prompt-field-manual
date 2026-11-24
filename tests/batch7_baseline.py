"""Immutable pre-Batch-7 tree for historical checks and scoped page comparisons."""
from functools import cache
import subprocess

from batch6_baseline import ROOT

PR41_MERGE = "c93608da305eb70e231613403edb8a275d7e1bbe"
BATCH7_SOURCE_SHA = "8ba47c93f4561c0daffa6bfce5d16401cded9f34a887bd8f300bcea38612e084"


@cache
def merged_disposition_bytes(path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{PR41_MERGE}:{path}"], cwd=ROOT)


PR42_MERGE = "793f35a29961f4ba77e431a54791e6f406e82988"
BATCH7_DISPOSITION_SOURCE_SHA = "3b02599e745910f647d4800160b6f22ef0192ff9520d61e4e08ae6f63ddd63ef"


@cache
def corrected_sec06_bytes(path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{PR42_MERGE}:{path}"], cwd=ROOT)
