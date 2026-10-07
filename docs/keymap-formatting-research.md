# QMK `LAYOUT()` formatting research

*Checked 2026-10-06*

## Finding

A purpose-built third-party formatter exists: [`qmk-layout-fmt`](https://github.com/OneDeadKey/qmk-layout-fmt), published as [`qmk-layout-fmt` on PyPI](https://pypi.org/project/qmk-layout-fmt/). It aligns columns in C `LAYOUT()` blocks, supports check-only mode, and accepts custom shapes.

It is not QMK-supported, so it should be validated by reviewing the diff and compiling before adoption. Its shape model handles split rows and thumb clusters, but it does not derive arbitrary staggered geometry from `keyboard.json`.

## QMK-supported tooling

- [`qmk format-c`](https://docs.qmk.fm/cli_commands#qmk-format-c) runs `clang-format`; it is not a keyboard-layout formatter.
- QMK's [C conventions](https://docs.qmk.fm/coding_conventions_c#auto-formatting-with-clang-format) warn that some things, including `LAYOUT` macros, are destroyed by `clang-format`. Use `// clang-format off` and `// clang-format on` around layout-sensitive code if needed.
- [`qmk format-json`](https://docs.qmk.fm/cli_commands#qmk-format-json) formats JSON, not C. [`qmk c2json`](https://docs.qmk.fm/cli_commands#qmk-c2json) is not a reliable replacement for preserving a hand-written C layout.
- QMK's [clang-format issue #6146](https://github.com/qmk/qmk_firmware/issues/6146) concerns formatting core directories, not physical keymap layout alignment.
- QMK [PR #26404](https://github.com/qmk/qmk_firmware/pull/26404) concerns row-aware JSON keymap formatting, not C `LAYOUT()` formatting.

## `qmk-layout-fmt`

The Silakka layout has four main rows of six keys per side, followed by three thumb keys per side. Its shape can be expressed as:

- `--main-rows 4`
- `--cols-per-side 6`
- `--thumb-per-side 3`

The package tracks nested parentheses, so wrappers such as `MT(...)`, `TD(...)`, `UM(...)`, and `LCMD(...)` should be parseable. However, its parser is not a complete C lexer; comments and strings are potential edge cases. The project is small and marked beta, so it should be treated as an opt-in formatter rather than a guaranteed QMK standard.

Recommended workflow:

1. Install it in an isolated tool environment with `uv tool install qmk-layout-fmt` or `pipx install qmk-layout-fmt`.
2. Run its check-only mode first.
3. Format a copy or review the diff carefully.
4. Confirm the split and thumb row still match the keyboard.
5. Compile with `qmk compile -kb silakka54 -km dannyb101`.

### Local check result

The formatter was tested against the current keymap with:

```text
qmk-layout-fmt --check --uniform --main-rows 4 --cols-per-side 6 --thumb-per-side 3 keyboards/silakka54/keymaps/dannyb101/keymap.c
```

It recognized all three `LAYOUT()` blocks and correctly handled the nested keycode expressions, but its proposed rendering puts the left and right halves on separate lines. That does not match the desired keyboard-shaped presentation, where both halves share each physical row. It should therefore not be adopted as the project's formatter without extending or wrapping it.

## Bespoke fallback

A local script is justified only if the package cannot produce the desired shape. It should:

- Target only `LAYOUT()` calls and preserve all non-whitespace tokens.
- Read `keyboards/silakka54/keyboard.json` for the 54-key layout and physical coordinates.
- Use a lexical scanner that tracks nested `()`, `[]`, and `{}` and ignores delimiters in strings/comments.
- Fail without writing if a layout has the wrong argument count or cannot be parsed safely.
- Render rows by physical `y`, preserve argument order, add a centre gap, and render the 3+3 thumb row separately.
- Provide `--check` and in-place modes.
- Be idempotent: running it twice must produce no second diff.
- Test nested keycode expressions, comments, strings, multiple layers, argument-count failures, and token-order preservation.

A suitable location would be `util/format_silakka54_layout.py`. It should be validated by compiling the keymap after formatting.

## Recommendation

Do not use `clang-format` for this requirement, and do not adopt `qmk-layout-fmt` unchanged: the local check showed that its output shape is wrong for the desired presentation. A small repo-local formatter is justified. It should be deliberately limited to this keyboard's C `LAYOUT()` blocks and tested for idempotence and compile success. QMK does not currently provide a layout-aware C formatter.

Other community options exist, such as [`go-qmk-keymap`](https://github.com/jurgen-kluft/go-qmk-keymap) and [`qmk-format-mode`](https://github.com/sgpthomas/qmk-format-mode), but they are less suitable here: the former is alpha and limited, while the latter is an Emacs mode.
