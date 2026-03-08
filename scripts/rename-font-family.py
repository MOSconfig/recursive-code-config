#!/usr/bin/env python3
"""
Rename font family from nerd-fonts-patcher output back to the original family name.

The nerd-fonts-patcher appends "Nerd Font" (or "Nerd Font Mono") to the font
family name. This script strips that suffix and restores the target family name.

Usage:
    python3 scripts/rename-font-family.py <family_name> <input_dir> <output_dir>

Example:
    python3 scripts/rename-font-family.py "St.Helens" /tmp/helens-nf fonts/RecMonoSt.Helens
"""

import os
import sys
from fontTools.ttLib import TTFont


def build_replacements(family_name):
    """Build replacement map for a given family name."""
    compact = family_name.replace(" ", "")
    spaced = f"Rec Mono {family_name}"
    joined = f"RecMono{compact}"
    return {
        f"{joined} Nerd Font Mono": spaced,
        f"{joined} Nerd Font": spaced,
        f"{joined}NFM": joined,
        f"{joined}NF": joined,
        f"{joined}NerdFontMono": joined,
        f"{joined}NerdFont": joined,
    }


def rename_font(src_path, dst_path, replacements):
    f = TTFont(src_path)
    for record in f["name"].names:
        orig = record.toUnicode()
        new_val = orig
        for old, new in replacements.items():
            new_val = new_val.replace(old, new)
        if new_val != orig:
            record.string = new_val
    f.save(dst_path)
    f.close()


def main():
    if len(sys.argv) < 4:
        print(f"Usage: {sys.argv[0]} <family_name> <input_dir> <output_dir>")
        sys.exit(1)

    family_name = sys.argv[1]
    input_dir = sys.argv[2]
    output_dir = sys.argv[3]
    os.makedirs(output_dir, exist_ok=True)

    replacements = build_replacements(family_name)

    for fname in sorted(os.listdir(input_dir)):
        if not fname.endswith(".ttf"):
            continue
        src = os.path.join(input_dir, fname)
        dst_name = fname
        for old, new in replacements.items():
            dst_name = dst_name.replace(old, new)
        dst = os.path.join(output_dir, dst_name)
        rename_font(src, dst, replacements)
        print(f"  {fname} -> {dst_name}")

    print("Done.")


if __name__ == "__main__":
    main()
