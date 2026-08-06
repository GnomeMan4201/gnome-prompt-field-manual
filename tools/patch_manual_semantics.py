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

TITLE_PATTERN = re.compile(
    r'<div(?P<attrs>[^>]*\bclass="[^"]*\bhdr-title\b[^"]*"[^>]*)>'
    r'(?P<body>.*?)</div>',
    re.DOTALL,
)
WRAP_PATTERN = re.compile(
    r'<div(?P<attrs>[^>]*\bclass="[^"]*\bwrap\b[^"]*"[^>]*)>'
)
SECTION_PATTERN = re.compile(
    r'<div(?P<attrs>[^>]*\bclass="[^"]*\bsection-title\b[^"]*"[^>]*)>'
    r'(?P<body>.*?)</div>',
    re.DOTALL,
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def replace_exact(text: str, old: str, new: str, *, expected: int = 1) -> str:
    count = text.count(old)
    if count != expected:
        raise ValueError(f"expected {expected} occurrences of {old!r}; found {count}")
    return text.replace(old, new)


def sub_exact(
    pattern: re.Pattern[str],
    text: str,
    replacement,
    *,
    expected: int,
    label: str,
) -> str:
    updated, count = pattern.subn(replacement, text)
    if count != expected:
        raise ValueError(f"expected {expected} {label} elements; transformed {count}")
    return updated


def sub_first(
    pattern: re.Pattern[str],
    text: str,
    replacement,
    *,
    label: str,
) -> str:
    if pattern.search(text) is None:
        raise ValueError(f"expected at least one {label} element; found 0")
    return pattern.sub(replacement, text, count=1)


def already_patched(text: str) -> bool:
    return all(
        (
            text.count(f'<meta name="description" content="{DESCRIPTION}">') == 1,
            len(re.findall(r'<div[^>]*\bclass="[^"]*\bwrap\b[^"]*"[^>]*\brole="main"[^>]*>', text)) == 1,
            len(re.findall(r'<h1[^>]*\bclass="[^"]*\bhdr-title\b[^"]*"[^>]*>.*?</h1>', text, re.DOTALL)) == 1,
            len(re.findall(r'<h2[^>]*\bclass="[^"]*\bsection-title\b[^"]*"[^>]*>.*?</h2>', text, re.DOTALL)) == 7,
            text.count(".hdr-title { margin: 0; }") == 1,
            not TITLE_PATTERN.search(text),
            not SECTION_PATTERN.search(text),
        )
    )


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
        "</style>",
        "    .hdr-title { margin: 0; }\n  </style>",
    )
    text = sub_exact(
        TITLE_PATTERN,
        text,
        lambda match: f'<h1{match.group("attrs")}>{match.group("body")}</h1>',
        expected=1,
        label="hdr-title",
    )
    text = sub_first(
        WRAP_PATTERN,
        text,
        lambda match: f'<div{match.group("attrs")} role="main">',
        label="primary wrap",
    )
    text = sub_exact(
        SECTION_PATTERN,
        text,
        lambda match: f'<h2{match.group("attrs")}>{match.group("body")}</h2>',
        expected=7,
        label="section-title",
    )

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
