#!/usr/bin/env python3
"""
Merge CJK (Chinese) glyphs from a CJK source font into a monospace target font.

Handles:
- Em-size normalization between source and target
- Synthetic emboldening of CJK glyphs to match thin Latin strokes
- Proper double-width (2x mono cell) for CJK, single-width for halfwidth forms
- Vertical alignment matched to Latin metrics
- Horizontal centering within advance width
"""

import fontforge
import sys


DOUBLE_WIDTH_RANGES = [
    (0x2E80, 0x2EFF), (0x2F00, 0x2FDF), (0x3000, 0x303F),
    (0x3040, 0x309F), (0x30A0, 0x30FF), (0x3100, 0x312F),
    (0x3130, 0x318F), (0x31A0, 0x31BF), (0x31F0, 0x31FF),
    (0x3200, 0x32FF), (0x3300, 0x33FF), (0x3400, 0x4DBF),
    (0x4DC0, 0x4DFF), (0x4E00, 0x9FFF), (0xF900, 0xFAFF),
    (0xFE30, 0xFE4F), (0xFF01, 0xFF60), (0xFFE0, 0xFFE6),
]

HALFWIDTH_RANGES = [
    (0xFF61, 0xFF9F), (0xFFA0, 0xFFDC), (0xFFE8, 0xFFEF),
]

ALL_RANGES = DOUBLE_WIDTH_RANGES + HALFWIDTH_RANGES


def get_cjk_vertical_bounds(source):
    sample_cps = [0x4E2D, 0x6587, 0x5B57, 0x4EBA, 0x5927, 0x5C0F, 0x56FD, 0x7684]
    y_mins, y_maxs = [], []
    for cp in sample_cps:
        if cp in source and source[cp].isWorthOutputting():
            bbox = source[cp].boundingBox()
            y_mins.append(bbox[1])
            y_maxs.append(bbox[3])
    if y_mins and y_maxs:
        return min(y_mins), max(y_maxs)
    return None, None


def merge_cjk(target_path, cjk_source_path, output_path, embolden=0, cjk_scale=1.0):
    print("Opening target: %s" % target_path)
    target = fontforge.open(target_path)

    print("Opening CJK source: %s" % cjk_source_path)
    source = fontforge.open(cjk_source_path)

    target_em = target.em
    source_em = source.em
    em_scale = float(target_em) / float(source_em)
    print("Target em: %d, Source em: %d, em_scale: %.4f" % (target_em, source_em, em_scale))
    if embolden:
        print("Synthetic embolden: +%d units" % embolden)
    if cjk_scale != 1.0:
        print("CJK scale factor: %.2f" % cjk_scale)

    mono_cell = 600
    double_width = mono_cell * 2

    target_ascender = target.os2_typoascent
    target_descender = target.os2_typodescent

    src_ymin, src_ymax = get_cjk_vertical_bounds(source)
    if src_ymin is not None:
        src_height = src_ymax - src_ymin
        target_body = float(target_ascender - target_descender)
        scaled_height = src_height * em_scale
        if scaled_height > target_body:
            total_scale = em_scale * (target_body / scaled_height)
        else:
            total_scale = em_scale
    else:
        total_scale = em_scale

    # Apply user-specified CJK scale factor
    total_scale *= cjk_scale

    final_ymin = src_ymin * total_scale if src_ymin else 0
    final_ymax = src_ymax * total_scale if src_ymax else target_em
    target_center = (target_ascender + target_descender) / 2.0
    glyph_center = (final_ymax + final_ymin) / 2.0
    v_offset = target_center - glyph_center
    print("Scale: %.4f (with cjk_scale=%.2f), v_offset: %.1f" % (total_scale, cjk_scale, v_offset))

    # Copy all glyphs
    copied = 0
    for start, end in ALL_RANGES:
        for cp in range(start, end + 1):
            source.selection.select(cp)
            source.copy()
            target.selection.select(cp)
            target.paste()
            copied += 1
    print("Copied %d glyph slots" % copied)

    dw_set = set()
    for start, end in DOUBLE_WIDTH_RANGES:
        for cp in range(start, end + 1):
            dw_set.add(cp)

    # Scale, embolden, align, and set widths
    fixed = 0
    for start, end in ALL_RANGES:
        for cp in range(start, end + 1):
            if cp in target and target[cp].isWorthOutputting():
                glyph = target[cp]
                is_double = cp in dw_set
                target_width = double_width if is_double else mono_cell

                # Scale + vertical shift
                glyph.transform((total_scale, 0, 0, total_scale, 0, v_offset))

                # Synthetic embolden: expand outlines to thicken strokes
                if embolden > 0:
                    glyph.stroke("circular", embolden, "round", "round")
                    glyph.removeOverlap()
                    glyph.simplify()

                # Center horizontally
                bbox = glyph.boundingBox()
                glyph_w = bbox[2] - bbox[0]
                if glyph_w > 0:
                    h_offset = (target_width / 2.0) - ((bbox[0] + bbox[2]) / 2.0)
                    glyph.transform((1, 0, 0, 1, h_offset, 0))

                glyph.width = target_width
                fixed += 1

    print("Processed %d glyphs" % fixed)

    # ------------------------------------------------------------------
    # Height normalization: scale up shorter CJK glyphs so they match
    # the typical body height, preventing some chars (e.g. 理 研 想)
    # from appearing too small on low-DPI / non-retina screens.
    # ------------------------------------------------------------------
    CJK_IDEOGRAPH_RANGE = (0x4E00, 0x9FFF)
    cjk_heights = []
    for cp in range(CJK_IDEOGRAPH_RANGE[0], CJK_IDEOGRAPH_RANGE[1] + 1):
        if cp in target and target[cp].isWorthOutputting():
            bbox = target[cp].boundingBox()
            h = bbox[3] - bbox[1]
            if h > 200:
                cjk_heights.append(h)

    if cjk_heights:
        cjk_heights.sort()
        ref_height = cjk_heights[len(cjk_heights) * 3 // 4]  # P75
        norm_threshold = ref_height * 0.97
        min_height = ref_height * 0.50  # don't touch structurally short chars
        normalized = 0

        for start, end in ALL_RANGES:
            for cp in range(start, end + 1):
                if cp in target and target[cp].isWorthOutputting():
                    glyph = target[cp]
                    bbox = glyph.boundingBox()
                    h = bbox[3] - bbox[1]
                    if h < norm_threshold and h > min_height:
                        s = ref_height / h
                        cx = (bbox[0] + bbox[2]) / 2.0
                        cy = (bbox[1] + bbox[3]) / 2.0
                        glyph.transform((s, 0, 0, s,
                                         cx * (1 - s), cy * (1 - s)))

                        is_double = cp in dw_set
                        tw = double_width if is_double else mono_cell
                        new_bbox = glyph.boundingBox()
                        gw = new_bbox[2] - new_bbox[0]
                        if gw > tw:
                            sx = tw / gw * 0.95
                            gcx = (new_bbox[0] + new_bbox[2]) / 2.0
                            glyph.transform((sx, 0, 0, 1,
                                             gcx * (1 - sx), 0))
                            new_bbox = glyph.boundingBox()

                        if gw > 0:
                            ho = (tw / 2.0) - ((new_bbox[0] + new_bbox[2]) / 2.0)
                            glyph.transform((1, 0, 0, 1, ho, 0))
                        glyph.width = tw
                        normalized += 1

        print("Height normalization: ref_height=%.0f, threshold=%.0f, normalized %d glyphs"
              % (ref_height, norm_threshold, normalized))

    target.os2_codepages = (target.os2_codepages[0] | (1 << 17) | (1 << 18), target.os2_codepages[1])
    target.generate(output_path)
    print("Saved: %s" % output_path)
    target.close()
    source.close()


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: %s <target_font> <cjk_source_font> <output_font> [embolden_units] [cjk_scale]" % sys.argv[0])
        print("  cjk_scale: multiplier for CJK glyph size (e.g. 1.15 = 15%% larger, default 1.0)")
        sys.exit(1)
    embolden = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    cjk_scale = float(sys.argv[5]) if len(sys.argv) > 5 else 1.0
    merge_cjk(sys.argv[1], sys.argv[2], sys.argv[3], embolden, cjk_scale)
