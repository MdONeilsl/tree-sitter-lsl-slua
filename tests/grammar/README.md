# Grammar test suite

Tests both grammars by parsing source files and asserting properties of
the tree.

## Running

    scripts\generate-all.cmd
    python tests\grammar\run_tests.py

Add `-v` to print the full s-expression tree for any failing test.

## Adding a test

Drop a `.lsl` or `.slua` file into `tests/grammar/lsl/` or
`tests/grammar/slua/`. By default, the runner asserts `has_error == False`.

To add assertions, create `<name>.json` alongside `<name>.lsl`:

    {
      "must_contain":     ["node_type_a", "node_type_b"],
      "must_not_contain": ["ERROR"],
      "max_parse_ms":     50,
      "note":             "why this test exists"
    }

## Assertions

| Key                | Meaning                                                      |
|--------------------|--------------------------------------------------------------|
| `skip`             | Do not run this test. Print `[SKIP]` with optional note.     |
| `expect_error`     | Invert the `has_error` assertion — the source should fail.   |
| `must_contain`     | Every named node type listed must appear in the tree.        |
| `must_not_contain` | None of these node types may appear.                         |
| `max_parse_ms`     | Fail if the parse takes longer than this.                    |
| `note`             | Free-form string shown with `[SKIP]` or on failure.          |

## Baseline perf

The runner also parses a synthetic 500-line file for each language and
prints the time. This is informational — use `max_parse_ms` on a real
test file if you want a hard timing assertion.