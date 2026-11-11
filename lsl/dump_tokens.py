# lsl/dump_tokens.py
"""
Walk the LSL parse tree and print every node with its position

Each row is:
    <type>  L<start_row>:C<start_col>-L<end_row>:C<end_col>  [<is_named>]  <snippet>
"""

import ctypes
import pathlib
import warnings

from tree_sitter import Language, Parser


def language_from_shared_library(library_path, language_name):
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


def walk(node, source, depth=0):
    """Depth-first walk that prints position for every node."""
    snippet = source[node.start_byte:node.end_byte].decode("utf-8", "replace")
    if len(snippet) > 40:
        snippet = snippet[:37] + "..."

    flag = "named" if node.is_named else "ANON "
    if node.is_missing:
        flag = "MISSING"

    print(
        f"{'  ' * depth}{node.type:<24}"
        f"L{node.start_point[0]}:C{node.start_point[1]}"
        f"-L{node.end_point[0]}:C{node.end_point[1]}  "
        f"[{flag}]  {snippet!r}"
    )
    for child in node.children:
        walk(child, source, depth + 1)


def main():
    here = pathlib.Path(__file__).resolve().parent
    library_path = here / "lsl.dll"
    LSL = language_from_shared_library(library_path, "lsl")
    parser = Parser(LSL)

    source = b"""integer gCounter = 0;

default
{
    state_entry()
    {
        gCounter = 5 + 3;
    }
}
"""

    tree = parser.parse(source)
    walk(tree.root_node, source)


if __name__ == "__main__":
    main()
    