#!/usr/bin/env bash
# build.sh — Build a Rec Mono font family with CJK glyphs and Nerd Font icons
#
# Usage:
#   ./scripts/build.sh <config.yaml> [cjk_scale]
#
# Examples:
#   ./scripts/build.sh config.helens.yaml 1.15
#   ./scripts/build.sh config.baker.yaml 1.15

set -euo pipefail
cd "$(dirname "$0")/.."

CONFIG="${1:?Usage: $0 <config.yaml> [cjk_scale]}"
CJK_SCALE="${2:-1.15}"

# Extract family name from config
FAMILY=$(grep '^Family Name:' "$CONFIG" | sed 's/^Family Name: *//')
COMPACT="RecMono${FAMILY// /}"

echo "=== Building Rec Mono ${FAMILY} (CJK scale: ${CJK_SCALE}) ==="

# Activate venv
source venv/bin/activate

# ── Step 1: Instantiate base fonts from variable font ──
echo ""
echo "── Step 1: Instantiate base fonts ──"
python3 scripts/instantiate-code-fonts.py "$CONFIG"

BASE_DIR="fonts/${COMPACT}"
STYLES=("Regular" "Italic" "Bold" "BoldItalic")

# Find the base font files (they have version suffix like -1.085)
declare -a BASE_FILES
for style in "${STYLES[@]}"; do
    BASE_FILES+=("$(ls "${BASE_DIR}/${COMPACT}-${style}-"*.ttf 2>/dev/null | head -1)")
done

# ── Step 2: Merge CJK glyphs (parallel) ──
echo ""
echo "── Step 2: Merge CJK glyphs (Resource Han Rounded, scale ${CJK_SCALE}) ──"
CJK_DIR=$(mktemp -d)
trap "rm -rf '$CJK_DIR'" EXIT

CJK_REGULAR="font-data/ResourceHanRoundedCN-Regular.ttf"
CJK_BOLD="font-data/ResourceHanRoundedCN-Bold.ttf"

PIDS=()
for i in "${!STYLES[@]}"; do
    style="${STYLES[$i]}"
    base="${BASE_FILES[$i]}"
    if [[ "$style" == Bold* ]]; then
        cjk_src="$CJK_BOLD"
    else
        cjk_src="$CJK_REGULAR"
    fi
    echo "  Merging CJK into ${style}..."
    fontforge -script scripts/merge-cjk.py \
        "$base" "$cjk_src" \
        "${CJK_DIR}/${COMPACT}-${style}.ttf" 0 "$CJK_SCALE" 2>&1 | grep -E "^(Saved|Height|Processed|Copied)" &
    PIDS+=($!)
done
# Wait for all CJK merges to finish; fail if any failed
for pid in "${PIDS[@]}"; do wait "$pid" || exit 1; done
echo "  All CJK merges complete."

# ── Step 3: Patch Nerd Font icons (parallel) ──
echo ""
echo "── Step 3: Patch Nerd Font icons ──"
NF_DIR=$(mktemp -d)
trap "rm -rf '$CJK_DIR' '$NF_DIR'" EXIT

PIDS=()
for style in "${STYLES[@]}"; do
    echo "  Patching ${style}..."
    fontforge -script nerd-fonts-patcher/font-patcher --complete \
        -out "$NF_DIR" "${CJK_DIR}/${COMPACT}-${style}.ttf" 2>&1 | tail -1 &
    PIDS+=($!)
done
for pid in "${PIDS[@]}"; do wait "$pid" || exit 1; done
echo "  All Nerd Font patches complete."

# ── Step 4: Rename font family (strip "Nerd Font" suffix) ──
echo ""
echo "── Step 4: Rename font family ──"
rm -f "${BASE_DIR}/"*.ttf
python3 scripts/rename-font-family.py "$FAMILY" "$NF_DIR" "$BASE_DIR"

echo ""
echo "=== Done! Fonts saved to ${BASE_DIR}/ ==="
ls -lh "${BASE_DIR}/"*.ttf
