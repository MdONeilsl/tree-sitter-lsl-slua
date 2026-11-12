#!/usr/bin/env bash
# scripts/assemble-dist.sh
#
# Cross-platform counterpart to scripts/assemble-dist.cmd.
# Assembles the drop-in distribution folder under dist/.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

case "$(uname -s)" in
    Linux*)  LIB_EXT=so    ;;
    Darwin*) LIB_EXT=dylib ;;
    *) echo "ERROR: unsupported OS: $(uname -s)"; exit 1 ;;
esac

DIST="$ROOT/dist"

# --- Required files ---------------------------------------------------
check_file() {
    if [ ! -e "$1" ]; then
        echo "ERROR: missing $1"
        exit 1
    fi
}

check_file "$ROOT/CMakeLists.txt"
check_file "$ROOT/README.md"

for F in \
    "lsl/CMakeLists.txt" \
    "lsl/include/lsl.h" \
    "lsl/src/parser.c" \
    "lsl/src/node-types.json" \
    "lsl/src/tree_sitter/parser.h" \
    "lsl/lsl.${LIB_EXT}" \
    "slua/CMakeLists.txt" \
    "slua/include/slua.h" \
    "slua/src/parser.c" \
    "slua/src/scanner.c" \
    "slua/src/node-types.json" \
    "slua/src/tree_sitter/parser.h" \
    "slua/slua.${LIB_EXT}"
do
    check_file "$ROOT/$F"
done

# --- Rebuild dist from scratch ----------------------------------------
echo "=== Cleaning $DIST ==="
rm -rf "$DIST"

echo "=== Creating layout ==="
mkdir -p "$DIST/lsl/include" "$DIST/lsl/src/tree_sitter"
mkdir -p "$DIST/slua/include" "$DIST/slua/src/tree_sitter"

echo "=== Copying root files ==="
cp -f "$ROOT/CMakeLists.txt" "$DIST/CMakeLists.txt"
cp -f "$ROOT/README.md"      "$DIST/README.md"
[ -f "$ROOT/LICENSE" ]                 && cp -f "$ROOT/LICENSE"                 "$DIST/LICENSE"                 || true
[ -f "$ROOT/THIRD_PARTY_NOTICES.md" ] && cp -f "$ROOT/THIRD_PARTY_NOTICES.md" "$DIST/THIRD_PARTY_NOTICES.md" || true

echo "=== Copying LSL ==="
cp -f "$ROOT/lsl/CMakeLists.txt"           "$DIST/lsl/CMakeLists.txt"
cp -f "$ROOT/lsl/include/lsl.h"            "$DIST/lsl/include/lsl.h"
cp -f "$ROOT/lsl/src/parser.c"             "$DIST/lsl/src/parser.c"
cp -f "$ROOT/lsl/src/node-types.json"      "$DIST/lsl/src/node-types.json"
cp -f "$ROOT/lsl/src/tree_sitter/parser.h" "$DIST/lsl/src/tree_sitter/parser.h"
cp -f "$ROOT/lsl/lsl.${LIB_EXT}"           "$DIST/lsl/lsl.${LIB_EXT}"
[ -f "$ROOT/lsl/src/grammar.json" ] && cp -f "$ROOT/lsl/src/grammar.json" "$DIST/lsl/src/grammar.json" || true

echo "=== Copying SLua ==="
cp -f "$ROOT/slua/CMakeLists.txt"           "$DIST/slua/CMakeLists.txt"
cp -f "$ROOT/slua/include/slua.h"           "$DIST/slua/include/slua.h"
cp -f "$ROOT/slua/src/parser.c"             "$DIST/slua/src/parser.c"
cp -f "$ROOT/slua/src/scanner.c"            "$DIST/slua/src/scanner.c"
cp -f "$ROOT/slua/src/node-types.json"      "$DIST/slua/src/node-types.json"
cp -f "$ROOT/slua/src/tree_sitter/parser.h" "$DIST/slua/src/tree_sitter/parser.h"
cp -f "$ROOT/slua/slua.${LIB_EXT}"          "$DIST/slua/slua.${LIB_EXT}"
[ -f "$ROOT/slua/src/grammar.json" ] && cp -f "$ROOT/slua/src/grammar.json" "$DIST/slua/src/grammar.json" || true

echo ""
echo "Package assembled at: $DIST"