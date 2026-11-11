# grammars/lsl/statements.py
from ..helpers import (
    rule_alias,
    rule_choice,
    rule_optional,
    rule_prec_right,
    rule_repeat,
    rule_seq,
    rule_string,
    rule_symbol,
)


def statement_alternatives():
    """All statement node types — used to build `_statement` and `_body`."""
    return [
        rule_symbol("variable_declaration"),
        rule_symbol("expression_statement"),
        rule_symbol("return_statement"),
        rule_symbol("if_statement"),
        rule_symbol("while_statement"),
        rule_symbol("do_while_statement"),
        rule_symbol("for_statement"),
        rule_symbol("state_transition"),
        rule_symbol("jump_statement"),
        rule_symbol("label_statement"),
        rule_symbol("lazy_list_assignment"),
        rule_symbol("break_statement"),
        rule_symbol("switch_statement"),
        rule_symbol("preproc_directive"),
        rule_string(";"),
    ]


def rules():
    return [
        ("_statement", rule_choice(*statement_alternatives())),

        # A body is a block or a single statement. Kept hidden: pure dispatch,
        # no extra semantic information. All its alternatives are visible.
        ("_body", rule_choice(
            rule_symbol("block"),
            rule_symbol("_statement"),
        )),

        # A block ALWAYS has braces in LSL, so it cannot match empty — safe as visible.
        ("block", rule_seq(
            rule_string("{"),
            rule_repeat(rule_symbol("_statement")),
            rule_string("}"),
        )),

        ("variable_declaration", rule_seq(
            rule_symbol("type"),
            rule_alias(rule_symbol("identifier"), "variable_name"),
            rule_optional(rule_seq(rule_string("="), rule_symbol("_expression"))),
            rule_string(";"),
        )),

        ("expression_statement", rule_seq(
            rule_symbol("_expression"),
            rule_string(";"),
        )),

        ("return_statement", rule_seq(
            rule_string("return"),
            rule_choice(
                rule_seq(rule_symbol("_expression"), rule_string(";")),
                rule_string(";"),
            ),
        )),

        # prec.right on the whole rule resolves the dangling-else case:
        # the `else` binds to the innermost `if`, as in LSL and C.
        ("if_statement", rule_prec_right(1, rule_seq(
            rule_string("if"),
            rule_string("("),
            rule_symbol("_expression"),
            rule_string(")"),
            rule_symbol("_body"),
            rule_optional(rule_seq(rule_string("else"), rule_symbol("_body"))),
        ))),

        ("while_statement", rule_seq(
            rule_string("while"),
            rule_string("("),
            rule_symbol("_expression"),
            rule_string(")"),
            rule_symbol("_body"),
        )),

        ("do_while_statement", rule_seq(
            rule_string("do"),
            rule_symbol("_body"),
            rule_string("while"),
            rule_string("("),
            rule_symbol("_expression"),
            rule_string(")"),
            rule_string(";"),
        )),

        ("for_statement", rule_seq(
            rule_string("for"),
            rule_string("("),
            rule_alias(rule_symbol("identifier"), "variable_name"),
            rule_string("="),
            rule_symbol("_expression"),
            rule_string(";"),
            rule_symbol("_expression"),
            rule_string(";"),
            rule_symbol("_expression"),
            rule_string(")"),
            rule_symbol("_body"),
        )),

        ("state_transition", rule_seq(
            rule_string("state"),
            rule_alias(rule_symbol("identifier"), "state_name"),
            rule_string(";"),
        )),

        ("jump_statement", rule_seq(
            rule_string("jump"),
            rule_alias(rule_symbol("identifier"), "label_name"),
            rule_string(";"),
        )),

        ("label_statement", rule_seq(
            rule_string("@"),
            rule_alias(rule_symbol("identifier"), "label_name"),
            rule_string(";"),
        )),

        # Firestorm: assign a list element by index.
        ("lazy_list_assignment", rule_seq(
            rule_alias(rule_symbol("identifier"), "variable_name"),
            rule_string("["),
            rule_symbol("_expression"),
            rule_string("]"),
            rule_string("="),
            rule_symbol("_expression"),
            rule_string(";"),
        )),

        ("break_statement", rule_seq(rule_string("break"), rule_string(";"))),

        ("switch_statement", rule_seq(
            rule_string("switch"),
            rule_string("("),
            rule_symbol("_expression"),
            rule_string(")"),
            rule_string("{"),
            rule_repeat(rule_choice(
                rule_symbol("case_clause"),
                rule_symbol("default_clause"),
            )),
            rule_string("}"),
        )),

        ("case_clause", rule_seq(
            rule_string("case"),
            rule_symbol("_expression"),
            rule_string(":"),
            rule_repeat(rule_symbol("_body")),
        )),

        ("default_clause", rule_seq(
            rule_string("default"),
            rule_string(":"),
            rule_repeat(rule_symbol("_body")),
        )),
    ]