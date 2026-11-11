# slua/generate_slua_grammar.py
import json
import pathlib
import sys

# Make the `grammars` package importable from the repository root.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from grammars.slua import build_grammar  # noqa: E402


def main():
    grammar = build_grammar()

    start_rule = next(iter(grammar["rules"]))
    print(f"Start rule (first key in 'rules'): {start_rule!r}")
    if start_rule != "source_file":
        raise SystemExit("ERROR: first rule is not 'source_file'")

    out_path = pathlib.Path(__file__).parent / "grammar.json"
    out_path.write_text(json.dumps(grammar, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()