"""Verified read-only Batch 3 source snapshot for historical source-bound research tests."""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE_SHA = "1f06445eb18295fce20ef0bf350d0237ead9d8713005ea2177e1281854210c19"
ARCHIVE = ROOT / "tests/fixtures/batch3-canonical-1f06445e.html"


def materialize_batch3_source(directory: Path) -> Path:
    raw = ARCHIVE.read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    if actual != BASELINE_SHA:
        raise ValueError(f"Frozen Batch 3 source SHA mismatch: {actual}")
    dest = directory / "index.html"
    dest.write_bytes(raw)
    return dest
