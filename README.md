# tree-sitter-lsl-slua

Tree-sitter grammars for **LSL** (Linden Scripting Language) and **SLua**
(Luau for Second Life).

This package gives your program the ability to turn LSL and SLua source code
into syntax trees, which you can then use for highlighting, linting, code
navigation, refactoring tools, or anything else that needs to understand the
structure of a script.

The package contains **only the grammars**. A separate library — the
**tree-sitter runtime** — does the actual parsing. You install the runtime
once; this package plugs into it.

---

## Table of contents

1. [What you get](#what-you-get)
2. [What you need first: the tree-sitter runtime](#what-you-need-first-the-tree-sitter-runtime)
3. [Getting the grammars](#getting-the-grammars)
4. [Using the grammars](#using-the-grammars)
5. [Working with parse trees](#working-with-parse-trees)
6. [Building a syntax highlighter](#building-a-syntax-highlighter)
7. [Troubleshooting](#troubleshooting)
8. [Licensing](#licensing)

---

## What you get

Two tree-sitter language definitions:

- **`lsl`** — Linden Scripting Language
- **`slua`** — Luau for Second Life

Each language is provided in two forms, so you can choose whichever fits your
project:

| Form | File | Use when |
|---|---|---|
| **Source** | `<grammar>/src/parser.c` | You compile it into your program. No shared library involved. |
| **Shared library** | `<grammar>/lsl.dll` (Windows), `.so` (Linux), `.dylib` (macOS) | You load the grammar at runtime, e.g. from a plugin host or script engine. |

Both forms expose the same C function:

```c
const TSLanguage *tree_sitter_lsl(void);   /* for LSL */
const TSLanguage *tree_sitter_slua(void);  /* for SLua */
```

You hand the returned pointer to the tree-sitter runtime, and from that moment
on it can parse LSL and SLua.

---

## What you need first: the tree-sitter runtime

The **tree-sitter runtime** is a separate C library maintained by the
tree-sitter project at <https://github.com/tree-sitter/tree-sitter>. It
provides the actual parsing engine. Without it, the grammars in this package
do nothing.

**You must install the runtime once.** It is not bundled here. That is
deliberate — it means you can upgrade it independently, and you will not end
up with two conflicting copies in the same program if another library also
uses tree-sitter.

### Installing the runtime

Pick whichever matches your environment:

| Environment | Command |
|---|---|
| vcpkg | `vcpkg install tree-sitter` |
| Conan | `conan install tree-sitter/0.25.0` |
| Debian / Ubuntu | `sudo apt install libtree-sitter-dev` |
| Fedora | `sudo dnf install tree-sitter-devel` |
| macOS (Homebrew) | `brew install tree-sitter` |
| From source | `cmake -B build && cmake --build build && cmake --install build` in the runtime repository |

The package expects a runtime **≥ 0.27**. Newer versions are fine; the parser
tables are forward-compatible across minor versions.

### If CMake cannot find the runtime

When you use this package through CMake, it will search for the runtime
automatically. If the runtime is installed somewhere unusual, tell CMake
where it is by one of these three methods (any one is enough):

- **Environment variable:** `set tree-sitter_ROOT=C:\path\to\tree-sitter`
- **CMake flag:** `-Dtree-sitter_DIR=C:/path/to/tree-sitter/lib/cmake/tree-sitter`
- **CMakePresets.json:**
  ```json
  {
    "version": 6,
    "configurePresets": [{
      "name": "default",
      "binaryDir": "build",
      "cacheVariables": {
        "CMAKE_PREFIX_PATH": "C:/vcpkg/installed/x64-windows"
      }
    }]
  }
  ```

If none of these is set and the runtime is not in a standard location, CMake
will print a warning but continue — you will just have to link the runtime
yourself (see [Using the grammars](#using-the-grammars)).

---

## Getting the grammars

Three ways, depending on how you want to bring the code into your project.
They are not exclusive.

### Option 1 — CMake FetchContent

Best if your project already uses CMake. Add this to your `CMakeLists.txt`:

```cmake
include(FetchContent)

FetchContent_Declare(tree-sitter-lsl-lsua
    GIT_REPOSITORY https://github.com/MdONeilsl/tree-sitter-lsl-lsua.git
    GIT_TAG        v0.1.0)
FetchContent_MakeAvailable(tree-sitter-lsl-lsua)

target_link_libraries(my_target PRIVATE
    tree-sitter::lsl
    tree-sitter::slua)
```

CMake fetches, configures, and links the grammars automatically. If you only
need one grammar, use `FetchContent_MakeAvailable` with the same repository
and set `-DTS_LSL_LSUA_BUILD_SLUA=OFF` (or the other way around).

### Option 2 — Download a release archive and drop it in

Best if you do not use CMake, or want a fixed version without network access.

1. Download the archive for your platform from
   <https://github.com/MdONeilsl/tree-sitter-lsl-slua/releasess>
   (e.g. `tree-sitter-lsl-lsua-windows-x64.zip`).
2. Extract it. You get a single top-level folder:
   ```
   tree-sitter-lsl-lsua-windows-x64/
       CMakeLists.txt
       lsl/
       slua/
       README.md
       LICENSE
       THIRD_PARTY_NOTICES.md
   ```
3. Copy that folder anywhere inside your project — typically
   `third_party/tree-sitter-lsl-lsua/`.
4. If you use CMake:
   ```cmake
   add_subdirectory(third_party/tree-sitter-lsl-lsua)
   target_link_libraries(my_target PRIVATE tree-sitter::lsl)
   ```
   If you do not use CMake, see Option 3.

### Option 3 — Use the C sources directly

Best if you do not use CMake at all.

1. Add `<grammar>/src/parser.c` to your build.
2. Add `<grammar>/src` to your include path (so `parser.c` finds
   `tree_sitter/parser.h`).
3. Add `<grammar>/include` to your include path (so your code finds
   `<grammar>.h`).
4. Add the tree-sitter runtime's include directory and link its library.

For example, with a hand-written Makefile or MSBuild:

```
sources:    lsl/src/parser.c  my_code.c
includes:   lsl/src  lsl/include  <tree-sitter-runtime>/include
libraries:  tree-sitter   (or libtree-sitter.a, tree-sitter.lib, …)
```

---

## Using the grammars

Whichever option you used to get the grammars, the code looks the same.

### Parsing a script

```c
#include <tree_sitter/api.h>   /* from the tree-sitter runtime */
#include "lsl.h"               /* from this package                  */

TSParser *parser = ts_parser_new();
ts_parser_set_language(parser, tree_sitter_lsl());

const char *source = "default { state_entry() { llSay(0, \"hi\"); } }";
TSTree *tree = ts_parser_parse_string(parser, NULL, source, strlen(source));

TSNode root = ts_tree_root_node(tree);
/* … use `root` … */

ts_tree_delete(tree);
ts_parser_delete(parser);
```

### Parsing SLua

Identical, but include `slua.h` and call `tree_sitter_slua()`:

```c
#include "slua.h"

ts_parser_set_language(parser, tree_sitter_slua());
```

### Loading the grammar at runtime instead of linking

If you would rather load the grammar from `<grammar>.dll` at runtime — for
example, from a plugin host that does not want to link any grammar
statically — use the standard platform loader.

**Windows:**

```c
#include <windows.h>
#include <tree_sitter/api.h>

HMODULE h = LoadLibraryW(L"lsl.dll");
if (!h) { /* handle error */ }

const TSLanguage *(*get_lang)(void) =
    (const TSLanguage *(*)(void))GetProcAddress(h, "tree_sitter_lsl");
if (!get_lang) { /* handle error */ }

ts_parser_set_language(parser, get_lang());
/* keep `h` loaded for as long as the parser is in use */
```

**Linux / macOS:**

```c
#include <dlfcn.h>
#include <tree_sitter/api.h>

void *h = dlopen("./lsl.so", RTLD_NOW | RTLD_LOCAL);
if (!h) { /* handle error */ }

const TSLanguage *(*get_lang)(void) =
    (const TSLanguage *(*)(void))dlsym(h, "tree_sitter_lsl");
if (!get_lang) { /* handle error */ }

ts_parser_set_language(parser, get_lang());
```

The exported symbol is a plain C function returning a plain C pointer. There
is no C++ name mangling, no wrapper layer, and no ABI marshalling. It works
from any language with `dlopen` / `LoadLibrary` / FFI support.

**Important:** the tree-sitter runtime must still be linked into *your*
process. The `.dll` provides only the grammar; the runtime does the parsing.

---

## Working with parse trees

Once you have a `TSTree`, every node in it carries both **its kind** and
**its position in the source**. This is what makes the tree useful for
highlighting, refactoring, and navigation tools.

### The fields on a `TSNode`

| Field | Meaning |
|---|---|
| `ts_node_type(node)` | Node kind (`"identifier"`, `"string"`, `"call_expression"`, …) |
| `ts_node_start_byte`, `ts_node_end_byte` | Byte offsets into the source |
| `ts_node_start_point`, `ts_node_end_point` | Row and **byte** column, zero-based |
| `ts_node_is_named(node)` | True for grammar nodes; false for anonymous tokens like `"("` |
| `ts_node_has_error(node)` | True if this subtree contains a parse error |

### Walking a tree

```c
void walk(TSNode node, int depth) {
    for (int i = 0; i < depth; i++) putchar(' ');
    TSPoint start = ts_node_start_point(node);
    printf("%s  [%u:%u]\n", ts_node_type(node), start.row, start.column);

    uint32_t count = ts_node_child_count(node);
    for (uint32_t i = 0; i < count; i++)
        walk(ts_node_child(node, i), depth + 1);
}

walk(root, 0);
```

### Incremental re-parsing

When the user edits a document, you do not need to re-parse from scratch.
Notify the tree of the edit, then re-parse only what changed:

```c
TSInputEdit edit = {
    .start_byte = ...,
    .old_end_byte = ...,
    .new_end_byte = ...,
    .start_point = ...,
    .old_end_point = ...,
    .new_end_point = ...,
};
ts_tree_edit(tree, &edit);

TSTree *new_tree = ts_parser_parse_string(parser, tree, new_source, new_length);
ts_tree_delete(tree);
tree = new_tree;
```

tree-sitter reuses the unchanged subtrees, so the cost is proportional to
the size of the edit, not the size of the file.

### Threading

- **`TSLanguage`** (returned by `tree_sitter_lsl()` / `tree_sitter_slua()`)
  is immutable. You can share one instance across any number of threads.
- **`TSParser`** is *not* thread-safe. Create one per thread that parses.

---

## Building a syntax highlighter

If you are writing a highlighter, editor plugin, or any tool that colors
tokens, the workflow is:

1. **Parse the whole document once** (not line by line — LSL and SLua are not
   line-oriented languages).
2. **Walk the tree once** and produce a flat list of records, one per token:
   ```
   (row, start_column, end_column, kind)
   ```
   Include both named and anonymous nodes, because `"+"`, `"("`, and string
   quotes matter for highlighting too.
3. **In your paint pass**, for each visible row, find the records whose
   `row` matches, and draw the appropriate style on the corresponding
   `[start_column, end_column)` range.

Sort the records by `(row, start_column)` and use binary search if the
document is large.

### About columns

`ts_node_start_point().column` is a **UTF-8 byte** column, not a character
column. For source that is pure ASCII — which describes essentially all
LSL and SLua scripts — the two are identical. If your source may contain
non-ASCII characters (UTF-8 strings, comments with emoji or CJK), convert:

```c
/* byte column -> character column */
size_t char_col = 0;
for (const char *p = line_start; p < line_start + byte_column; ) {
    unsigned char c = (unsigned char)*p;
    if      ((c & 0x80) == 0x00) p += 1;
    else if ((c & 0xE0) == 0xC0) p += 2;
    else if ((c & 0xF0) == 0xE0) p += 3;
    else                         p += 4;
    char_col++;
}
```

If your text API indexes by UTF-16 code units (as many GUI toolkits do),
you need one more conversion from code points to UTF-16 units, because
astral-plane characters (emoji, rare CJK) count as two units.

### Making the tree show up

`ts_node_string(root)` returns a compact s-expression, which is useful when
debugging grammar rules:

```c
char *sexp = ts_node_string(root);
printf("%s\n", sexp);
free(sexp);
```

That s-expression deliberately omits positions. To see positions, use
`ts_node_start_point()` and `ts_node_end_point()` on each node — see the
walk example above.

### Role node types

Both grammars alias identifiers by their semantic role. A consumer can
distinguish, for example, a variable name from a function name by
`ts_node_type` alone:

| LSL | SLua |
|---|---|
| `event_name` | `attribute_name` |
| `function_name` | `declared_name` |
| `label_name` | `function_name` |
| `parameter_name` | `member_name` |
| `state_name` | `member_object_name` |
| `variable_name` | `method_name` |
| | `parameter_name` |
| | `table_field_name` |
| | `type_identifier` |
| | `type_param_name` |
| | `variable_name` |

Any identifier not covered by a role remains a plain `identifier`.

---

## Troubleshooting

**I get `unresolved external symbol ts_parser_new` (or the linker equivalent).**
You built the grammar but did not link the tree-sitter runtime. Add its
library to your link step (`tree-sitter`, `libtree-sitter.a`,
`tree-sitter.lib`, whichever your installation provides).

**`LoadLibrary` / `dlopen` returns NULL.**
- The `.dll` / `.so` is not on the loader's search path. On Windows, place it
  next to the executable or add its folder to `PATH`. On Linux, use an
  absolute path or set `LD_LIBRARY_PATH`. On macOS, `DYLD_LIBRARY_PATH`.
- Architecture mismatch — an x64 process cannot load an x86 DLL.
- A dependency of the DLL is missing. Run
  [Dependencies](https://github.com/lucasg/Dependencies) (Windows) or
  `ldd` (Linux) on the file.

**`ts_parser_set_language()` returns `false`.**
Runtime version is older than the grammar. Upgrade the runtime to 0.27 or
newer.

**Parse tree has `ERROR` nodes.**
The grammar can parse the language, but some construct in your source is not
yet covered. Please open an issue with a minimal reproduction. LSL has more
than 400 built-in functions and several syntax quirks (`||` binds tighter
than `&&`, for example) that are added incrementally.

**CMake cannot find `tree-sitter`.**
See [If CMake cannot find the runtime](#if-cmake-cannot-find-the-runtime)
above.

**I only want one grammar, not both.**
With FetchContent: `-DTS_LSL_LSUA_BUILD_SLUA=OFF` (or the reverse). With a
release archive: keep only the `lsl/` or `slua/` folder and `add_subdirectory`
that one.

---

## Licensing

- The code in this package (grammar definitions, headers, CMake files) is
  **MIT-licensed**. See `LICENSE`.
- `<grammar>/src/tree_sitter/parser.h` is a verbatim copy of the tree-sitter
  runtime's header, also MIT-licensed. Its notice is in
  `THIRD_PARTY_NOTICES.md`, which is included in every release archive.
- The **tree-sitter runtime** is MIT-licensed but is **not** bundled with
  this package. Install it separately as described above.

You may redistribute this package and link it into commercial or
open-source software without restriction. If you choose to also ship the
tree-sitter runtime binary alongside your application, you may do so under
the MIT license — just include the tree-sitter permission notice in your own
third-party notices.

---

*Second Life, SL, and inSL are trademarks of Linden Research, Inc. tree-sitter-lsl-slua
 is not affiliated with or sponsored by Linden Research.*
