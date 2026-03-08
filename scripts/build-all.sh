#!/usr/bin/env bash
# build-all.sh — Build all font families in parallel
#
# Usage:
#   ./scripts/build-all.sh [cjk_scale]
#
# Example:
#   ./scripts/build-all.sh 1.15

set -euo pipefail
cd "$(dirname "$0")/.."

CJK_SCALE="${1:-1.15}"
SCRIPT_DIR="scripts"
CONFIGS=(config.baker.yaml config.helens.yaml)
PIDS=()
LOGS=()

echo "=== Building all fonts in parallel (CJK scale: ${CJK_SCALE}) ==="
echo ""

for cfg in "${CONFIGS[@]}"; do
    family=$(grep '^Family Name:' "$cfg" | sed 's/^Family Name: *//')
    log=$(mktemp)
    LOGS+=("$log")
    echo "Starting: Rec Mono ${family} (${cfg})..."
    "${SCRIPT_DIR}/build.sh" "$cfg" "$CJK_SCALE" > "$log" 2>&1 &
    PIDS+=($!)
done

# Wait for all builds; track failures
FAILED=0
for i in "${!PIDS[@]}"; do
    pid="${PIDS[$i]}"
    cfg="${CONFIGS[$i]}"
    if wait "$pid"; then
        echo "✓ ${cfg} completed successfully."
    else
        echo "✗ ${cfg} FAILED (see log below)."
        FAILED=1
    fi
done

echo ""

# Print logs
for i in "${!CONFIGS[@]}"; do
    cfg="${CONFIGS[$i]}"
    log="${LOGS[$i]}"
    echo "────────────────────────────────────────"
    echo "Log: ${cfg}"
    echo "────────────────────────────────────────"
    cat "$log"
    rm -f "$log"
    echo ""
done

if [ "$FAILED" -ne 0 ]; then
    echo "=== Some builds failed! ==="
    exit 1
fi

echo "=== All fonts built successfully! ==="
ls -lh fonts/RecMono*/*.ttf
