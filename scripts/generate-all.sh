#!/usr/bin/env bash
# scripts/generate-all.sh
#
# Cross-platform counterpart to scripts/generate-all.cmd.
# Auto-downloads the tree-sitter CLI if not present at the repo root,
# then regenerates grammar.json, parser.c, and the shared library for
# each grammar.
#
# Usage (from anywhere):
#     bash scripts/generate-all.sh

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# --- Detect platform ---------------------------------------------------
case "$(uname -s)" in
    Linux*)  OS=linux ; LIB_EXT=so    ;;
    Darwin*) OS=macos ; LIB_EXT=dylib ;;
    *) echo "ERROR: unsupported OS: $(uname -s)"; exit 1 ;;
esac

case "$(uname -m)" in
    x86_64|amd64)   ARCH=x64 ;;
    arm64|aarch64)  ARCH=arm64 ;;
    *) echo "ERROR: unsupported arch: $(uname -m)"; exit 1 ;;
esac

CLI_VERSION="0.27.2"
TS="$ROOT/tree-sitter"

# --- Download the CLI if missing ---------------------------------------
if [ ! -x "$TS" ]; then
    echo "=== Downloading tree-sitter CLI ${CLI_VERSION} (${OS}-${ARCH}) ==="
    URL="https://github.com/tree-sitter/tree-sitter/releases/download/v${CLI_VERSION}/tree-sitter-cli-${OS}-${ARCH}.zip"
    TMP="$(mktemp -d)"
    trap 'rm -rf "$TMP"' EXIT

    if ! command -v curl >/dev/null 2>&1; then
        echo "ERROR: curl is required. Install curl and re-run." >&2
        exit 1
    fi
    curl -fL "$URL" -o "$TMP/cli.zip"

    # Python is a dependency anyway; use it to unpack the zip portably.
    python3 -m zipfile -e "$TMP/cli.zip" "$TMP"

    FOUND="$(find "$TMP" -type f -name tree-sitter | head -n1 || true)"
    if [ -z "${FOUND}" ]; then
        echo "ERROR: tree-sitter binary not found in downloaded archive" >&2
        exit 1
    fi
    cp "$FOUND" "$TS"
    chmod +x "$TS"
fi

echo "=== tree-sitter: $("$TS" --version) ==="

# --- Generate and build each grammar -----------------------------------
for G in lsl slua; do
    GEN="$ROOT/$G/generate_${G}_grammar.py"
    if [ ! -f "$GEN" ]; then
        echo "Skipping $G (no generate_${G}_grammar.py yet)"
        continue
    fi

    echo "=== Generating grammar.json for $G ==="
    ( cd "$ROOT/$G" && python3 "generate_${G}_grammar.py" )

    echo "=== Generating parser.c for $G ==="
    ( cd "$ROOT/$G" && "$TS" generate grammar.json )

    echo "=== Staging grammar.json into src/ for $G ==="
    cp "$ROOT/$G/grammar.json" "$ROOT/$G/src/grammar.json"

    echo "=== Building $G shared library (${G}.${LIB_EXT}) ==="
    ( cd "$ROOT/$G" && "$TS" build --output "${G}.${LIB_EXT}" . )
done

echo "All grammars generated and built."