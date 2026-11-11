# slua/check_parser.py
"""
Load slua.dll and parse a representative SLua script.
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
        warnings.filterwarnings("ignore", message="int argument support is deprecated", category=DeprecationWarning)
        return Language(symbol())


def main():
    here = pathlib.Path(__file__).resolve().parent
    library_path = here / "slua.dll"

    if not library_path.exists():
        raise SystemExit(f"Shared library not found: {library_path}\nBuild it first with scripts\\generate-all.cmd")

    SLUA = language_from_shared_library(library_path, "slua")
    parser = Parser(SLUA)

    sample = b"""
local count: number = 0

function state_entry()
    ll.Say(0, "Hello, SLua!")
    count = count + 1
end

function touch_start(total_number: number)
    if count > 0 then
        ll.Say(0, "Touched!")
    elseif count == 0 then
        ll.Say(0, "First touch")
    else
        ll.Say(0, "Never reached")
    end

    for i = 1, 10 do
        ll.Say(0, tostring(i))
    end

    local t = { x = 1, y = 2, [3] = "three" }
    for k, v in t do
        ll.Say(0, tostring(k) .. " = " .. tostring(v))
    end

    local x = 0
    while x < 5 do
        x += 1
        if x == 3 then
            continue
        end
    end
end
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