# grammars/lsl/literals.py
from ..helpers import rule_pattern, rule_choice, rule_seq, rule_string


def rules():
    return [
        ("identifier", rule_pattern(r"[A-Za-z_][A-Za-z0-9_]*")),
        ("number",     rule_pattern(r"\d+(\.\d+)?")),
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