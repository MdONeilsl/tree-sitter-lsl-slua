# grammars/lsl/literals.py
from ..helpers import rule_pattern, rule_choice, rule_seq, rule_string


def rules():
    return [
        ("identifier", rule_pattern(r"[A-Za-z_][A-Za-z0-9_]*")),
        # LSL number literals follow C99:
        #   integers       42, 0x1A
        #   decimal floats 1.5, 1., .5, 1e10, 1.5e-3, .5e-6
        #   hex floats     0x1.8p3, 0x1.0C6F7Ap-21
        # Order matters only for same-length matches; tree-sitter takes the
        # longest match otherwise, so hex-float before hex-int and float
        # before int both work without ambiguity.
        ("number", rule_choice(
            rule_pattern(r"0[xX][0-9a-fA-F]*\.[0-9a-fA-F]*[pP][+-]?\d+"),
            rule_pattern(r"0[xX][0-9a-fA-F]+"),
            rule_pattern(r"\d+\.\d*([eE][+-]?\d+)?"),
            rule_pattern(r"\.\d+([eE][+-]?\d+)?"),
            rule_pattern(r"\d+([eE][+-]?\d+)?"),
        )),
        ("string",     rule_seq(
            rule_string('"'),
            rule_pattern(r'([^"\\]|\\.)*'),
            rule_string('"'),
        )),
        ("comment", rule_choice(
            rule_seq(rule_string("//"), rule_pattern(r"[^\n]*")),
            rule_seq(
                rule_string("/*"),
                rule_pattern(r"[^*]*\*+(?:[^/*][^*]*\*+)*"),
                rule_string("/"),
            ),
        )),
        # Preprocessor directives (C-style). The keyword is matched and the
        # rest of the line is captured as an opaque token — the parser does
        # not interpret directive contents; the preprocessor runs first.
        ("preproc_directive", rule_seq(
            rule_string("#"),
            rule_choice(
                rule_string("include"),
                rule_string("define"),
                rule_string("undef"),
                rule_string("ifdef"),
                rule_string("ifndef"),
                rule_string("if"),
                rule_string("elif"),
                rule_string("else"),
                rule_string("endif"),
                rule_string("warning"),
                rule_string("error"),
            ),
            rule_pattern(r"[^\n]*"),
        )),
    ]