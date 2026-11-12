"""
Grammar test runner for LSL and SLua.

Discovers *.lsl under tests/grammar/lsl/ and *.slua under tests/grammar/slua/.
For each file:

  - loads the corresponding grammar's .dll
  - parses the file
  - asserts `has_error == False` unless overridden
  - checks any additional assertions in the adjacent <name>.json file

Options in the JSON meta (all optional):

  skip            : true                 — do not run this test; print [SKIP]
  expect_error    : true                 — invert the has_error assertion
  must_contain    : ["node_type", ...]   — every named node must appear
  must_not_contain: ["node_type", ...]   — none of these may appear
  max_parse_ms    : <number>             — fail if parse exceeds this time
  note            : "..."                — printed with [SKIP] or on failure

Run from the repo root:

    scripts\\generate-all.cmd
    python tests\\grammar\\run_tests.py
"""

import ctypes
import json
import pathlib
import sys
import time
import warnings

from tree_sitter import Language, Parser

def _lib_ext() -> str:
    if sys.platform == "win32":   return ".dll"
    if sys.platform == "darwin":  return ".dylib"
    return ".so"


HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def load_language(dll_path, name):
    lib = ctypes.cdll.LoadLibrary(str(dll_path))
    sym = getattr(lib, f"tree_sitter_{name}")
    sym.restype = ctypes.c_void_p
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="int argument support is deprecated",
            category=DeprecationWarning,
        )
        return Language(sym())


def collect_named_types(root):
    types = set()
    stack = [root]
    while stack:
        n = stack.pop()
        if n.is_named:
            types.add(n.type)
        stack.extend(n.children)
    return types


def find_error_nodes(root):
    errors = []
    stack = [root]
    while stack:
        n = stack.pop()
        if n.type == "ERROR" or n.is_missing:
            errors.append(n)
        stack.extend(n.children)
    return errors


def read_meta(meta_path):
    """
    Load the per-test JSON meta file if present.

    Uses utf-8-sig to strip a Windows BOM; treats an empty or
    whitespace-only file as "no meta"; names the file on any JSON
    error so the fix is obvious.
    """
    if not meta_path.exists():
        return {}
    raw = meta_path.read_text(encoding="utf-8-sig")
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise SystemExit(
            f"ERROR: {meta_path} is not valid JSON: {e}\n"
            f"       first 32 bytes: {raw[:32]!r}"
        )


def run_one_test(source_path, parser, verbose):
    meta = read_meta(source_path.with_suffix(".json"))

    rel = source_path.relative_to(HERE)
    note = meta.get("note", "")

    if meta.get("skip"):
        suffix = f"  ({note})" if note else ""
        print(f"[SKIP] {rel}{suffix}")
        return True

    source = source_path.read_bytes()
    expect_error   = meta.get("expect_error", False)
    must_contain   = meta.get("must_contain", [])
    must_not_have  = meta.get("must_not_contain", [])
    max_ms         = meta.get("max_parse_ms")

    if expect_error and (must_contain or must_not_have):
        print(f"[NOTE] {rel}: expect_error=true; "
              f"skipping must_contain / must_not_contain assertions")

    t0 = time.perf_counter()
    tree = parser.parse(source)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    root = tree.root_node

    problems = []

    if not expect_error and root.has_error:
        problems.append("unexpected parse errors (has_error=True)")
        for err in find_error_nodes(root):
            snippet = source[err.start_byte:err.end_byte].decode("utf-8", "replace")
            problems.append(f"    {err.type} @ {err.start_point} .. {err.end_point}: {snippet!r}")
    if expect_error and not root.has_error:
        problems.append("expected a parse error but got none")

    # Node-type assertions only make sense on a successful parse.
    if not expect_error:
        types = collect_named_types(root)
        for needed in must_contain:
            if needed not in types:
                problems.append(f"missing required node type: {needed!r}")
        for forbidden in must_not_have:
            if forbidden in types:
                problems.append(f"forbidden node type present: {forbidden!r}")

    if max_ms is not None and elapsed_ms > max_ms:
        problems.append(f"parse took {elapsed_ms:.1f} ms > {max_ms} ms limit")

    ok = not problems
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {rel}  ({elapsed_ms:.1f} ms)")
    for p in problems:
        print(f"        {p}")

    if not ok and verbose:
        print(f"        tree: {root}")

    return ok


def perf_smoke(parser, language):
    """
    Parse a 500-line synthetic file to establish a baseline timing.
    Informational only — does not affect pass/fail.
    """
    if language == "lsl":
        lines = [f"integer var_{i} = {i};" for i in range(500)]
    else:
        lines = [f"local var_{i} = {i}" for i in range(500)]
    source = "\n".join(lines).encode("utf-8")

    t0 = time.perf_counter()
    tree = parser.parse(source)
    ms = (time.perf_counter() - t0) * 1000.0
    print(
        f"[PERF] {language}: 500 lines, {ms:.1f} ms, "
        f"has_error={tree.root_node.has_error}"
    )


def main():
    verbose = "-v" in sys.argv or "--verbose" in sys.argv

    ext = _lib_ext()
    lsl_dll  = ROOT / "lsl"  / f"lsl{ext}"
    slua_dll = ROOT / "slua" / f"slua{ext}"
    if not lsl_dll.exists() or not slua_dll.exists():
        print("ERROR: build the grammars first:")
        print("  Windows:  scripts\\generate-all.cmd")
        print("  Unix:     bash scripts/generate-all.sh")
        return 1

    try:
        lsl_lang  = load_language(lsl_dll,  "lsl")
        slua_lang = load_language(slua_dll, "slua")
    except OSError as e:
        print(f"ERROR: could not load a grammar DLL: {e}")
        return 1

    lsl_parser  = Parser(lsl_lang)
    slua_parser = Parser(slua_lang)

    groups = [
        ("lsl",  lsl_parser,  HERE / "lsl",  "*.lsl"),
        ("slua", slua_parser, HERE / "slua", "*.slua"),
    ]

    total = 0
    passed = 0
    failed_paths = []

    for name, parser, directory, pattern in groups:
        if not directory.exists():
            print(f"NOTE: no test directory for {name} ({directory})")
            continue
        print(f"\n=== {name} ===")
        for source_path in sorted(directory.glob(pattern)):
            total += 1
            if run_one_test(source_path, parser, verbose):
                passed += 1
            else:
                failed_paths.append(source_path)

    print("\n=== baseline perf ===")
    perf_smoke(lsl_parser, "lsl")
    perf_smoke(slua_parser, "slua")

    print(f"\n{passed}/{total} passed")
    if failed_paths:
        print("\nFailed:")
        for p in failed_paths:
            print(f"  {p.relative_to(HERE)}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())