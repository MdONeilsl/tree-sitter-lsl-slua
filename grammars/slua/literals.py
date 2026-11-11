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
                rule_symbol("_interpolation"),
                rule_pattern(r"[^`{]+"),
            )),
            rule_string("`"),
        )),

        # Interpolation body: `{ expr }`. Hidden dispatch — the inner
        # expression is what carries the roles.
        ("_interpolation", rule_seq(
            rule_string("{"),
            rule_symbol("_expression"),
            rule_string("}"),
        )),

        ("comment", rule_choice(
            rule_seq(rule_string("--"), rule_pattern(r"[^\n]*")),
            rule_seq(
                rule_string("--[["),
                rule_pattern(r"[\s\S]*?"),
                rule_string("]]"),
            ),
        )),
    ]