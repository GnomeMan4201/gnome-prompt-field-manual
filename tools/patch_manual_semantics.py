#!/usr/bin/env python3
"""Apply a one-time, hash-gated semantic repair to the current PTSP artifact.

The transformation is intentionally narrow: it adds publication metadata, one
main landmark, one document h1, and seven top-level section h2 elements. It
refuses unknown input and never rewrites content text.
"""

from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path

EXPECTED_SOURCE_SHA256 = "b576496ce0f496536b50e07526c081174e032cd38eb8f4659b67e517c3f950d5"
DESCRIPTION = (
    "Production workspace and embedded reader for the GNOME Prompt Field Manual, "
    "including the PTSP pending-entry drafting plan."
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def replace_exact(text: str, old: str, new: str, *, expected: int = 1) -> str:
    count = text.count(old)
    if count != expected:
        raise ValueError(f"expected {expected} occurrences of {old!r}; found {count}")
    return text.replace(old, new)


def already_patched(text: str) -> bool:
    checks = (
        text.count(f'<meta name="description" content="{DESCRIPTION}">') == 1,
        text.count('<div class="wrap" role="main">') == 1,
        text.count('<h1 class="hdr-title" style="margin:0">PTSP — Pending Entry Draft Plan</h1>') == 1,
        len(re.findall(r'<h2 class="section-title">.*?</h2>', text)) == 7,
        '<div class="hdr-title">PTSP — Pending Entry Draft Plan</div>' not in text,
        '<div class="wrap">' not in text,
        '<div class="section-title">' not in text,
    )
    return all(checks)


def patch(path: Path) -> bool:
    raw = path.read_bytes()
    text = raw.decode("utf-8")
    digest = sha256(raw)

    if digest != EXPECTED_SOURCE_SHA256:
        if already_patched(text):
            print(f"semantic repair already present; source_sha256={digest}")
            return False
        raise ValueError(
            "refusing unknown index.html: "
            f"expected {EXPECTED_SOURCE_SHA256}, observed {digest}"
        )

    text = replace_exact(
        text,
        "<title>PTSP — Pending Entry Draft Plan</title>",
        "<title>PTSP — Pending Entry Draft Plan</title>\n"
        f'  <meta name="description" content="{DESCRIPTION}">',
    )
    text = replace_exact(
        text,
        '<div class="hdr-title">PTSP — Pending Entry Draft Plan</div>',
        '<h1 class="hdr-title" style="margin:0">PTSP — Pending Entry Draft Plan</h1>',
    )
    text = replace_exact(
        text,
        '<div class="wrap">',
        '<div class="wrap" role="main">',
    )

    section_pattern = re.compile(r'<div class="section-title">(.*?)</div>')
    text, count = section_pattern.subn(r'<h2 class="section-title">\1</h2>', text)
    if count != 7:
        raise ValueError(f"expected 7 section-title elements; transformed {count}")

    if not already_patched(text):
        raise ValueError("postcondition failed after semantic transformation")

    path.write_text(text, encoding="utf-8", newline="")
    print(f"patched {path}; source_sha256={digest}; output_sha256={sha256(path.read_bytes())}")
    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", type=Path, default=Path("index.html"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.input.is_file():
        raise SystemExit(f"manual not found: {args.input}")
    try:
        patch(args.input)
    except (UnicodeDecodeError, ValueError) as exc:
        raise SystemExit(f"semantic repair failed: {exc}") from exc
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
