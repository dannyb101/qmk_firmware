#!/usr/bin/env python3
"""Format silakka54 LAYOUT() arrays without changing key assignments."""

from __future__ import annotations

import argparse
import difflib
import re
import sys
from pathlib import Path


INDENT = "        "
# QMK uses spaces here; these values model four-space visual tab stops.
TAB_WIDTH = 4
CENTER_GAP = TAB_WIDTH * 2
MAIN_ROWS = 4
KEYS_PER_SIDE = 6
THUMB_KEYS_PER_SIDE = 3
EXPECTED_ARGUMENTS = MAIN_ROWS * KEYS_PER_SIDE * 2 + THUMB_KEYS_PER_SIDE * 2
IDENTIFIER = re.compile(r"\bLAYOUT\s*\(")


def split_arguments(body: str) -> list[str]:
    """Split a LAYOUT body on commas at nesting depth zero."""
    arguments: list[str] = []
    start = 0
    parens = brackets = braces = 0
    quote: str | None = None
    escaped = False
    line_comment = False
    block_comment = False
    index = 0

    while index < len(body):
        char = body[index]
        next_char = body[index + 1] if index + 1 < len(body) else ""

        if line_comment:
            if char == "\n":
                line_comment = False
            index += 1
            continue
        if block_comment:
            if char == "*" and next_char == "/":
                block_comment = False
                index += 2
            else:
                index += 1
            continue
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            index += 1
            continue
        if char == "/" and next_char == "/":
            line_comment = True
            index += 2
            continue
        if char == "/" and next_char == "*":
            block_comment = True
            index += 2
            continue
        if char in "\"'":
            quote = char
        elif char == "(":
            parens += 1
        elif char == ")":
            parens -= 1
        elif char == "[":
            brackets += 1
        elif char == "]":
            brackets -= 1
        elif char == "{":
            braces += 1
        elif char == "}":
            braces -= 1
        elif char == "," and not (parens or brackets or braces):
            arguments.append(body[start:index].strip())
            start = index + 1
        index += 1

    if quote or line_comment or block_comment or min(parens, brackets, braces) < 0:
        raise ValueError("unterminated string/comment or unbalanced delimiters")

    arguments.append(body[start:].strip())
    if any(not argument for argument in arguments):
        raise ValueError("empty top-level LAYOUT argument")
    return arguments


def find_call_end(text: str, opening: int) -> int:
    """Find the closing parenthesis for a LAYOUT call."""
    depth = 1
    quote: str | None = None
    escaped = False
    line_comment = False
    block_comment = False
    index = opening + 1

    while index < len(text):
        char = text[index]
        next_char = text[index + 1] if index + 1 < len(text) else ""
        if line_comment:
            if char == "\n":
                line_comment = False
            index += 1
            continue
        if block_comment:
            if char == "*" and next_char == "/":
                block_comment = False
                index += 2
            else:
                index += 1
            continue
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            index += 1
            continue
        if char == "/" and next_char == "/":
            line_comment = True
            index += 2
            continue
        if char == "/" and next_char == "*":
            block_comment = True
            index += 2
            continue
        if char in "\"'":
            quote = char
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return index
        index += 1

    raise ValueError("unterminated LAYOUT call")


def tab_stop(width: int) -> int:
    return ((width + TAB_WIDTH - 1) // TAB_WIDTH) * TAB_WIDTH


def cell(text: str, width: int) -> str:
    return (text + ",").ljust(width)


def column_widths(rows: list[list[str]], extras: dict[int, list[str]]) -> list[int]:
    """Return tab-stop widths for columns, including aligned thumb values."""
    widths = []
    for column in range(KEYS_PER_SIDE * 2):
        values = [row[column] for row in rows]
        values.extend(extras.get(column, []))
        # The maximum includes the comma and one separator before the next key.
        item_width = max(len(value) + 1 for value in values) + 1
        widths.append(tab_stop(item_width))
    return widths


def layout_parts(arguments: list[str]) -> tuple[list[list[str]], list[str], list[int]]:
    if len(arguments) != EXPECTED_ARGUMENTS:
        raise ValueError(
            f"expected {EXPECTED_ARGUMENTS} LAYOUT arguments, found {len(arguments)}"
        )

    rows = [
        arguments[row * KEYS_PER_SIDE * 2 : (row + 1) * KEYS_PER_SIDE * 2]
        for row in range(MAIN_ROWS)
    ]
    thumbs = arguments[MAIN_ROWS * KEYS_PER_SIDE * 2 :]
    widths = column_widths(
        rows,
        {
            3: [thumbs[0]],
            4: [thumbs[1]],
            5: [thumbs[2]],
            6: [thumbs[3]],
            7: [thumbs[4]],
            8: [thumbs[5]],
        },
    )
    return rows, thumbs, widths


def format_layout(arguments: list[str], shared_left_width: int | None = None) -> str:
    rows, thumbs, widths = layout_parts(arguments)
    left_width = sum(widths[:KEYS_PER_SIDE])
    left_width = max(left_width, shared_left_width or 0)

    rendered = []
    for row in rows:
        left = "".join(cell(token, widths[column]) for column, token in enumerate(row[:KEYS_PER_SIDE]))
        right = "".join(
            cell(token, widths[column + KEYS_PER_SIDE])
            for column, token in enumerate(row[KEYS_PER_SIDE:])
        )
        rendered.append(f"{INDENT}{left.ljust(left_width)}{' ' * CENTER_GAP}{right}".rstrip())

    left_prefix = "".join(" " * widths[column] for column in range(3))
    left_thumbs = "".join(
        cell(token, widths[column + 3]) for column, token in enumerate(thumbs[:3])
    )
    right_thumbs = "".join(
        cell(token, widths[column + 6]) for column, token in enumerate(thumbs[3:])
    ).rstrip().removesuffix(",")
    rendered.append(
        f"{INDENT}{(left_prefix + left_thumbs).ljust(left_width)}"
        f"{' ' * CENTER_GAP}{right_thumbs}"
    )
    return "\n".join(rendered)


def format_file(text: str) -> str:
    calls: list[tuple[int, int, list[str], str]] = []
    search_from = 0
    while match := IDENTIFIER.search(text, search_from):
        opening = text.find("(", match.start(), match.end())
        closing = find_call_end(text, opening)
        body = text[opening + 1 : closing]
        arguments = split_arguments(body)
        closing_line_start = text.rfind("\n", 0, closing) + 1
        closing_indent = text[closing_line_start:closing]
        calls.append((opening, closing, arguments, closing_indent))
        search_from = closing + 1

    shared_left_width = max(
        sum(layout_parts(arguments)[2][:KEYS_PER_SIDE])
        for _, _, arguments, _ in calls
    ) if calls else 0

    output: list[str] = []
    cursor = 0
    for opening, closing, arguments, closing_indent in calls:
        output.append(text[cursor : opening + 1])
        output.append(
            "\n"
            + format_layout(arguments, shared_left_width)
            + "\n"
            + closing_indent
        )
        cursor = closing
    output.append(text[cursor:])
    return "".join(output)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="fail if formatting is needed")
    mode.add_argument("--write", action="store_true", help="rewrite the file in place")
    args = parser.parse_args()

    original = args.file.read_text()
    try:
        formatted = format_file(original)
    except ValueError as error:
        print(f"{args.file}: {error}", file=sys.stderr)
        return 2

    if formatted == original:
        return 0
    if args.check:
        print(f"{args.file}: formatting required")
        return 1
    if args.write:
        args.file.write_text(formatted)
        return 0

    diff = difflib.unified_diff(
        original.splitlines(keepends=True),
        formatted.splitlines(keepends=True),
        fromfile=str(args.file),
        tofile=f"{args.file} (formatted)",
    )
    sys.stdout.writelines(diff)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
