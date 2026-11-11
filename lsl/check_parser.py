# lsl/check_parser.py
import ctypes
import pathlib
import warnings

from tree_sitter import Language, Parser


def language_from_shared_library(library_path, language_name):
    library = ctypes.cdll.LoadLibrary(str(library_path))
    symbol = getattr(library, f"tree_sitter_{language_name}")
    symbol.restype = ctypes.c_void_p
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="int argument support is deprecated", category=DeprecationWarning)
        return Language(symbol())


def main():
    here = pathlib.Path(__file__).resolve().parent
    library_path = here / "lsl.dll"

    if not library_path.exists():
        raise SystemExit(f"Shared library not found: {library_path}")

    LSL = language_from_shared_library(library_path, "lsl")
    parser = Parser(LSL)

    sample_text = r"""
#define CHANNEL 12345
#define OS(a) llOwnerSay(#a)

integer gCounter = 0;
list    gMyList  = [];

default
{
    state_entry()
    {
        #ifdef DEBUG
            llOwnerSay("debug mode");
        #else
            llOwnerSay("release mode");
        #endif

        #include "helpers.lsl"

        // Switch / case (Firestorm preprocessor)
        integer i = 2;
        switch (i)
        {
            case 1:
            {
                OS("one");
            }
            case 2:
            {
                OS("two");
                // fallthrough
            }
            case 3:
            {
                OS("three");
                break;
            }
            default:
            {
                OS("default");
            }
        }

        // Lazy list assignment
        gMyList[0] = 42;
        gMyList[1] = "hello";

        // Lazy list reading is standard index_expression
        integer n = gMyList[0];
    }
}
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