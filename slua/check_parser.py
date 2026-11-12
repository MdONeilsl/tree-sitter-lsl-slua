# slua/check_parser.py
import ctypes
import pathlib
import warnings
import sys

from tree_sitter import Language, Parser



def _lib_ext() -> str:
    if sys.platform == "win32":   return ".dll"
    if sys.platform == "darwin":  return ".dylib"
    return ".so"


def language_from_shared_library(library_path, language_name):
    library = ctypes.cdll.LoadLibrary(str(library_path))
    symbol = getattr(library, f"tree_sitter_{language_name}")
    symbol.restype = ctypes.c_void_p
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="int argument support is deprecated", category=DeprecationWarning)
        return Language(symbol())


def main():
    here = pathlib.Path(__file__).resolve().parent
    library_path = here / f"lsl{_lib_ext()}"

    if not library_path.exists():
        raise SystemExit(
            f"Shared library not found: {library_path}\n"
            "Build it first:\n"
            "  Windows:  scripts\\generate-all.cmd\n"
            "  Unix:     bash scripts/generate-all.sh"
        )

    SLUA = language_from_shared_library(library_path, "slua")
    parser = Parser(SLUA)

    sample_text = """
-- Long strings, all bracket levels
local a = [[plain long string]]
local b = [=[contains ]] inside]=]
local c = [==[contains ]=] inside]==]

-- const declaration
const PI = 3.14159
const LIMIT: number = 100

-- Type declarations
type Point = { x: number, y: number }
export type Predicate<T> = (T) -> boolean

-- Generic function
function identity<T>(v: T): T
    return v
end

-- Function attributes (name only)
@native
function fast(n: number): number
    return n * 2
end

@checked
function validated(n: number): number
    return n
end

-- Declare statements
declare version: string
declare function warn<T...>(...: T...)
"""

    sample = sample_text.encode("utf-8")

    tree = parser.parse(sample)
    root = tree.root_node

    print(f"Root node type : {root.type}")
    print(f"Has error?     : {root.has_error}")
    print()
    print(root)

    if root.has_error:
        print()
        print("=== ERROR / MISSING NODES ===")
        stack = [root]
        while stack:
            node = stack.pop()
            if node.type == "ERROR" or node.is_missing:
                snippet = sample[node.start_byte:node.end_byte].decode("utf-8", "replace")
                print(f"  {node.type} @ {node.start_point} .. {node.end_point}: {snippet!r}")
            stack.extend(node.children)


if __name__ == "__main__":
    main()