# grammars/slua/literals.py
from ..helpers import rule_pattern, rule_choice, rule_seq, rule_string, rule_symbol, rule_repeat


def rules():
    return [
        ("identifier", rule_pattern(r"[A-Za-z_][A-Za-z0-9_]*")),

        ("number", rule_choice(
            rule_pattern(r"0[xX][0-9a-fA-F_]+"),
            rule_pattern(r"0[bB][01_]+"),
            rule_pattern(r"\d[\d_]*(\.[\d_]*)?([eE][+-]?\d+)?"),
            rule_pattern(r"\.\d[\d_]*([eE][+-]?\d+)?"),
        )),

        # String forms: quoted (single/double) or long-bracket. Long-bracket
        # leaves are produced by the external scanner (`long_string_rest`),
        # which matches the closing `]=*]` against the opening `[=*[`.
        ("string", rule_choice(
            rule_seq(rule_string('"'), rule_pattern(r'[^"\\]*(\\[\s\S][^"\\]*)*'), rule_string('"')),
            rule_seq(rule_string("'"), rule_pattern(r"[^'\\]*(\\[\s\S][^'\\]*)*"), rule_string("'")),
            rule_seq(rule_string("["), rule_symbol("long_string_rest")),
        )),

                ("interpolated_string", rule_seq(
            rule_string("`"),
            rule_repeat(rule_choice(
                rule_symbol("interpolation"),
                rule_symbol("string_content"),
            )),
            rule_string("`"),
        )),

        ("interpolation", rule_seq(
            rule_string("{"),
            rule_symbol("_expression"),
            rule_string("}"),
        )),

        ("string_content", rule_pattern(r"[^`{]+")),

        # Single-line and long-form comments. `--[[ ... ]]` and
        # `--[=[ ... ]=]` must be handled by the `long_string_rest` external
        # scanner: a regex cannot match the closing bracket level against
        # the opening one, and putting `[\s\S]*?` in a separate token makes
        # the lexer match to EOF, which is exactly the "comment does not
        # close" bug. The scanner is the same one used by `string`.
        #
        # Long comment is FIRST in the choice so the tie case
        # `--[[short]]` (valid as both single-line and long-form) resolves
        # to the long-form, which is what the semantics require. Single-line
        # is the fallback for `-- foo` and for malformed `--[` without a
        # matching closer.
        ("comment", rule_choice(
            rule_seq(rule_string("--["), rule_symbol("long_string_rest")),
            rule_seq(rule_string("--"), rule_pattern(r"[^\n]*")),
        )),
    ]