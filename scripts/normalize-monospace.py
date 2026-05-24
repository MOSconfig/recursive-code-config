#!/usr/bin/env python3
"""normalize-monospace.py — Stage 5: fix Windows Terminal alignment.

The nerd-fonts-patcher (stage 3) sees that we have ASCII glyphs at advance
600 and CJK / icon glyphs at advance 1200, decides the font is "not strictly
fixed-pitch," and writes `post.isFixedPitch = 0`. The font *is* monospace
(everything sits on the 600-unit grid), but Windows Terminal and DirectWrite
both consult `post.isFixedPitch` directly. When it's 0, WT falls back to a
per-glyph DirectWrite shaping path with subpixel advances, and accumulated
rounding error walks plain ASCII text off the cell grid — visible as "VERSION"
not lining up between rows. macOS / iTerm / Alacritty / Kitty check PANOSE or
infer fixed-pitch from advance widths and don't show the bug.

Fix: rewrite `post.isFixedPitch = 1` on every output TTF. Also set
`OS/2.xAvgCharWidth = 600` (the ASCII cell width — some Windows layout code
uses it for spacing hints) and assert `panose.bProportion = 9` (Monospaced).

Second Windows-only drift source: `head.flags` bit 4 ("Instructions may
alter advance width"). Recursive ships with this bit set, and the patcher
preserves it. When set, DirectWrite consults the TrueType hint program
(`cvt`/`prep`/per-glyph `glyf` instructions) to compute per-glyph advances
at the rendering ppem, instead of trusting the static `hmtx` value. Even
when every ASCII glyph nominally has advance 600, hinting can nudge widths
by a subpixel during gridfitting; the accumulated rounding walks plain
ASCII text like "VERSION" off the terminal cell grid. Core Text /
HarfBuzz ignore hint-driven advance changes for monospace, which is why
the bug is Windows-only. Clearing bit 4 tells the rasterizer to trust
`hmtx` as authoritative.

Idempotent: re-running on already-fixed files is a no-op. Safe to call from
build-all.sh or by hand.

Usage:
    python3 scripts/normalize-monospace.py fonts/RecMonoBaker/*.ttf
    python3 scripts/normalize-monospace.py fonts/**/*.ttf
"""

import sys
from pathlib import Path

from fontTools.ttLib import TTFont

ASCII_CELL = 600  # Recursive's monospace cell width at UPEM=1000.
HEAD_FLAG_INSTR_ALTER_ADVANCE = 0x10  # head.flags bit 4.


def normalize(path: Path) -> bool:
    """Return True iff the file was modified."""
    f = TTFont(str(path))
    post, os2, head = f["post"], f["OS/2"], f["head"]
    changed = False

    if post.isFixedPitch != 1:
        post.isFixedPitch = 1
        changed = True

    if os2.xAvgCharWidth != ASCII_CELL:
        os2.xAvgCharWidth = ASCII_CELL
        changed = True

    if head.flags & HEAD_FLAG_INSTR_ALTER_ADVANCE:
        head.flags &= ~HEAD_FLAG_INSTR_ALTER_ADVANCE
        changed = True

    if os2.panose.bProportion != 9:
        # Don't silently rewrite — surface as a warning. If this fires, the
        # upstream font has changed in a way that warrants investigation.
        print(
            f"  WARN {path.name}: panose.bProportion={os2.panose.bProportion} "
            f"(expected 9 = Monospaced)",
            file=sys.stderr,
        )

    if changed:
        f.save(str(path))
    return changed


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__, file=sys.stderr)
        return 2
    paths = [Path(p) for p in argv[1:]]
    missing = [p for p in paths if not p.is_file()]
    if missing:
        for p in missing:
            print(f"ERROR: not a file: {p}", file=sys.stderr)
        return 1

    for p in paths:
        modified = normalize(p)
        flag = "fixed" if modified else "already-ok"
        print(f"  [{flag}] {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
