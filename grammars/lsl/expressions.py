# grammars/lsl/expressions.py
from ..helpers import (
    rule_alias,
    rule_blank,
    rule_choice,
    rule_optional,
    rule_prec,
    rule_prec_left,
    rule_prec_right,
    rule_repeat,
    rule_seq,
    rule_string,
    rule_symbol,
)


def rules():
    return [
        # Hidden dispatcher: every alternative inside is a visible node, so
        # tools get full distinction without an extra wrapper level.
        ("_expression", rule_choice(
            rule_symbol("assignment_expression"),
            rule_symbol("binary_expression"),
            rule_symbol("unary_expression"),
            rule_symbol("postfix_expression"),
            rule_symbol("cast_expression"),
            rule_symbol("call_expression"),
            rule_symbol("index_expression"),
            rule_symbol("parenthesized_expression"),
            rule_symbol("vector_literal"),
            rule_symbol("rotation_literal"),
            rule_symbol("list_literal"),
            rule_symbol("identifier"),
            rule_symbol("number"),
            rule_symbol("string"),
        )),

        # LHS is aliased to `variable_name`; RHS is any expression.
        ("assignment_expression", rule_prec_right(0, rule_seq(
            rule_alias(rule_symbol("identifier"), "variable_name"),
            rule_choice(
                rule_string("="),
                rule_string("+="),
                rule_string("-="),
                rule_string("*="),
                rule_string("/="),
                rule_string("%="),
            ),
            rule_symbol("_expression"),
        ))),

        # LSL operator precedence — same table as the wiki; note that `||`
        # binds TIGHTER than `&&`, unlike C.
        ("binary_expression", rule_choice(
            rule_prec_left(1,  rule_seq(rule_symbol("_expression"), rule_string("&&"), rule_symbol("_expression"))),
            rule_prec_left(2,  rule_seq(rule_symbol("_expression"), rule_string("||"), rule_symbol("_expression"))),
            rule_prec_left(3,  rule_seq(rule_symbol("_expression"), rule_string("|"),  rule_symbol("_expression"))),
            rule_prec_left(4,  rule_seq(rule_symbol("_expression"), rule_string("^"),  rule_symbol("_expression"))),
            rule_prec_left(5,  rule_seq(rule_symbol("_expression"), rule_string("&"),  rule_symbol("_expression"))),
            rule_prec_left(6,  rule_seq(rule_symbol("_expression"), rule_choice(rule_string("=="), rule_string("!=")), rule_symbol("_expression"))),
            rule_prec_left(7,  rule_seq(rule_symbol("_expression"), rule_choice(rule_string("<"), rule_string("<="), rule_string(">"), rule_string(">=")), rule_symbol("_expression"))),
            rule_prec_left(8,  rule_seq(rule_symbol("_expression"), rule_choice(rule_string("<<"), rule_string(">>")), rule_symbol("_expression"))),
            rule_prec_left(9,  rule_seq(rule_symbol("_expression"), rule_string("+"),  rule_symbol("_expression"))),
            rule_prec_left(10, rule_seq(rule_symbol("_expression"), rule_string("-"),  rule_symbol("_expression"))),
            rule_prec_left(11, rule_seq(rule_symbol("_expression"), rule_choice(rule_string("*"), rule_string("/"), rule_string("%")), rule_symbol("_expression"))),
        )),

        ("unary_expression", rule_prec(12, rule_seq(
            rule_choice(
                rule_string("!"),
                rule_string("~"),
                rule_string("-"),
                rule_string("++"),
                rule_string("--"),
            ),
            rule_symbol("_expression"),
        ))),

        ("postfix_expression", rule_prec_left(15, rule_seq(
            rule_symbol("_expression"),
            rule_choice(rule_string("++"), rule_string("--")),
        ))),

        ("cast_expression", rule_prec(13, rule_seq(
            rule_string("("),
            rule_symbol("type"),
            rule_string(")"),
            rule_symbol("_expression"),
        ))),

        ("parenthesized_expression", rule_seq(
            rule_string("("),
            rule_symbol("_expression"),
            rule_string(")"),
        )),

        ("call_expression", rule_seq(
            rule_alias(rule_symbol("identifier"), "function_name"),
            rule_symbol("argument_list"),
        )),

        ("argument_list", rule_seq(
            rule_string("("),
            rule_optional(rule_seq(
                rule_symbol("_expression"),
                rule_repeat(rule_seq(rule_string(","), rule_symbol("_expression"))),
            )),
            rule_string(")"),
        )),

        ("index_expression", rule_prec(14, rule_seq(
            rule_symbol("_expression"),
            rule_string("["),
            rule_symbol("_expression"),
            rule_string("]"),
        ))),

        ("vector_literal", rule_seq(
            rule_string("<"),
            rule_symbol("_expression"),
            rule_string(","),
            rule_symbol("_expression"),
            rule_string(","),
            rule_symbol("_expression"),
            rule_string(">"),
        )),

        ("rotation_literal", rule_seq(
            rule_string("<"),
            rule_symbol("_expression"),
            rule_string(","),
            rule_symbol("_expression"),
            rule_string(","),
            rule_symbol("_expression"),
            rule_string(","),
            rule_symbol("_expression"),
            rule_string(">"),
        )),

        ("list_literal", rule_seq(
            rule_string("["),
            rule_optional(rule_seq(
                rule_symbol("_expression"),
                rule_repeat(rule_seq(rule_string(","), rule_symbol("_expression"))),
            )),
            rule_string("]"),
        )),
    ]