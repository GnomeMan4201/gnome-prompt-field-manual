#!/usr/bin/env python3
"""Print a compact, bounded structural inventory for a large HTML manual.

The output is intended for CI diagnosis when the source is too large to inspect
comfortably through repository APIs. It never modifies the input file and does
not make network requests.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path


_WHITESPACE = re.compile(r"\s+")


@dataclass
class Element:
    tag: str
    line: int
    depth: int
    element_id: str = ""
    classes: tuple[str, ...] = ()
    role: str = ""
    text_parts: list[str] = field(default_factory=list)

    def summary(self) -> str:
        selector = self.tag
        if self.element_id:
            selector += f"#{self.element_id}"
        if self.classes:
            selector += "".join(f".{name}" for name in self.classes[:6])
            if len(self.classes) > 6:
                selector += f".+{len(self.classes) - 6}"
        if self.role:
            selector += f'[role="{self.role}"]'
        text = _WHITESPACE.sub(" ", " ".join(self.text_parts)).strip()
        if len(text) > 120:
            text = text[:117] + "..."
        return f"line={self.line:>5} depth={self.depth:<2} {selector:<72} text={text!r}"


class StructureParser(HTMLParser):
    VOID_TAGS = {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[Element] = []
        self.elements: list[Element] = []
        self.body_depth: int | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        values = {key.lower(): value or "" for key, value in attrs}
        line, _ = self.getpos()
        element = Element(
            tag=tag,
            line=line,
            depth=len(self.stack),
            element_id=values.get("id", "").strip(),
            classes=tuple(values.get("class", "").split()),
            role=values.get("role", "").strip(),
        )
        self.elements.append(element)
        if tag == "body":
            self.body_depth = element.depth
        if tag not in self.VOID_TAGS:
            self.stack.append(element)

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        self.handle_starttag(tag, attrs)
        if tag.lower() not in self.VOID_TAGS:
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                return

    def handle_data(self, data: str) -> None:
        text = _WHITESPACE.sub(" ", data).strip()
        if not text:
            return
        for element in self.stack[-4:]:
            if sum(len(part) for part in element.text_parts) < 300:
                element.text_parts.append(text)


def inspect(path: Path, max_lines: int) -> str:
    parser = StructureParser()
    parser.feed(path.read_text(encoding="utf-8", errors="replace"))
    parser.close()

    selected: list[Element] = []
    seen: set[tuple[int, str]] = set()

    def include(element: Element) -> None:
        key = (element.line, element.tag)
        if key not in seen:
            selected.append(element)
            seen.add(key)

    for element in parser.elements:
        if element.tag in {"html", "head", "body", "main", "header", "nav", "article", "section", "aside", "footer"}:
            include(element)
        if element.tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            include(element)
        if element.element_id or element.role:
            include(element)
        if parser.body_depth is not None and element.depth <= parser.body_depth + 3:
            include(element)

    selected.sort(key=lambda item: (item.line, item.depth, item.tag))
    class_counts: dict[str, int] = {}
    tag_counts: dict[str, int] = {}
    for element in parser.elements:
        tag_counts[element.tag] = tag_counts.get(element.tag, 0) + 1
        for name in element.classes:
            class_counts[name] = class_counts.get(name, 0) + 1

    output = [
        f"source={path}",
        f"elements={len(parser.elements)}",
        f"body_depth={parser.body_depth}",
        "",
        "SELECTED STRUCTURE",
    ]
    output.extend(element.summary() for element in selected[:max_lines])
    if len(selected) > max_lines:
        output.append(f"... omitted {len(selected) - max_lines} selected elements")

    output.extend(["", "TOP TAG COUNTS"])
    output.extend(
        f"{tag:<16} {count}"
        for tag, count in sorted(tag_counts.items(), key=lambda item: (-item[1], item[0]))[:30]
    )
    output.extend(["", "TOP CLASS COUNTS"])
    output.extend(
        f"{name:<48} {count}"
        for name, count in sorted(class_counts.items(), key=lambda item: (-item[1], item[0]))[:60]
    )
    return "\n".join(output) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", type=Path, default=Path("index.html"))
    parser.add_argument("--max-elements", type=int, default=240)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.input.is_file():
        raise SystemExit(f"manual not found: {args.input}")
    if not 1 <= args.max_elements <= 1000:
        raise SystemExit("--max-elements must be between 1 and 1000")
    print(inspect(args.input, args.max_elements), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
