# lsl/check_parser.py
"""
Load the LSL shared library built by `tree-sitter build` and parse a
small LSL script, then print the resulting syntax tree.

Pipeline validated here:
    grammar.json -> parser.c -> lsl.dll -> Python parse tree
"""

import ctypes
import pathlib
import warnings

from tree_sitter import Language, Parser


def language_from_shared_library(library_path: pathlib.Path, language_name: str) -> Language:
    """
    Load a Tree-sitter language from a native shared library.

    py-tree-sitter >= 0.22 removed the `Language(path, name)` constructor.
    The documented replacement is to load the library with ctypes, look up
    the `tree_sitter_<name>` symbol, and pass the pointer it returns to
    `Language()`.  In 0.26.x that integer-pointer path emits a
    DeprecationWarning; it is still the supported way to load a custom
    shared library, so the warning is suppressed locally.
    """
    library = ctypes.cdll.LoadLibrary(str(library_path))
    symbol = getattr(library, f"tree_sitter_{language_name}")
    symbol.restype = ctypes.c_void_p

    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="int argument support is deprecated",
            category=DeprecationWarning,
        )
        return Language(symbol())


def main() -> None:
    here = pathlib.Path(__file__).resolve().parent
    library_path = here / "lsl.dll"  # Linux: lsl.so / macOS: lsl.dylib

    if not library_path.exists():
        raise SystemExit(
            f"Shared library not found: {library_path}\n"
            "Build it first:  cd lsl  &&  ..\\tree-sitter.exe build --output lsl.dll ."
        )

    LSL = language_from_shared_library(library_path, "lsl")
    parser = Parser(LSL)

    sample = b"""
integer gCounter = 0;
float  gPI      = 3.14159;
vector gOrigin  = <0.0, 0.0, 0.0>;

default
{
    state_entry()
    {
        // Assignment and arithmetic
        gCounter = 5;
        gCounter = gCounter + 1;
        gCounter += 1;

        // Typecast, call, concatenation
        string msg = "Count: " + (string)gCounter;
        llSay(0, msg);

        // Vector / rotation / list literals
        vector   v = <1.0, 2.0, 3.0>;
        rotation r = <0.0, 0.0, 0.0, 1.0>;
        list     l = [1, 2.0, "three", v];

        // Comparison, logical, LSL precedence quirk:
        //   `||` binds tighter than `&&`
        integer isFalse = (TRUE && TRUE || FALSE && FALSE);

        if (isFalse)
        {
            llSay(0, "unexpected");
        }

        // Prefix and postfix
        integer n = 10;
        --n;
        n = -n;
        n = ~n;
        n = !n;
    }

    touch_start(integer total_number)
    {
        return;
    }
}
"""

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