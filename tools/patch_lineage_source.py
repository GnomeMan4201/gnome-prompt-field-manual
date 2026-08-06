#!/usr/bin/env python3
"""Apply one exact, temporary source repair to the lineage reconciler."""

from __future__ import annotations

from pathlib import Path

PATH = Path("tools/reconcile_entry_lineage.py")


def main() -> int:
    text = PATH.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)

    matches = [
        index
        for index, line in enumerate(lines)
        if "item.contexts[0]" in line and ".replace(" in line
    ]
    if len(matches) != 1:
        raise SystemExit(
            f"expected one unsafe f-string expression; found {len(matches)}"
        )
    lines[matches[0]] = (
        '        f"{_escape_table(item.contexts[0] if item.contexts else \'\')} |"\n'
    )
    text = "".join(lines)

    marker = "\ndef markdown_report(result: Reconciliation, failures: list[str]) -> str:\n"
    helper = (
        "\ndef _escape_table(value: str) -> str:\n"
        "    return value.replace(\"|\", \"\\\\|\").replace(\"\\n\", \" \")\n\n\n"
        "def markdown_report(result: Reconciliation, failures: list[str]) -> str:\n"
    )
    if text.count(marker) != 1:
        raise SystemExit("expected one markdown_report marker")
    text = text.replace(marker, helper, 1)

    PATH.write_text(text, encoding="utf-8", newline="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
