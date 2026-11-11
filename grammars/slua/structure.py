# grammars/slua/structure.py
from ..helpers import (
    rule_alias,
    rule_choice,
    rule_optional,
    rule_repeat,
    rule_repeat1,
    rule_seq,
    rule_string,
    rule_symbol,
)


def rules():
    return [
        # source_file MUST be first rule — the start rule.
        ("source_file", rule_repeat(rule_symbol("_statement"))),

        # Block: must match at least one statement, so `repeat1`. Call sites
        # wrap in `rule_optional(block)` — an empty `function f() end` has
        # no `block` child, which is correct: there is nothing to highlight.
        ("block", rule_repeat1(rule_symbol("_statement"))),

        # -- Functions ---------------------------------------------------
        ("function_declaration", rule_seq(
            rule_optional(rule_symbol("_attributes")),
            rule_string("function"),
            rule_symbol("_function_name"),
            rule_optional(rule_symbol("_type_params")),
            rule_symbol("function_body"),
        )),

        ("local_function_declaration", rule_seq(
            rule_optional(rule_symbol("_attributes")),
            rule_string("local"),
            rule_string("function"),
            rule_alias(rule_symbol("identifier"), "function_name"),
            rule_optional(rule_symbol("_type_params")),
            rule_symbol("function_body"),
        )),

        # `a.b.c`, `a:b`, `a.b:c`. Each identifier is aliased by role.
        ("_function_name", rule_seq(
            rule_alias(rule_symbol("identifier"), "function_name"),
            rule_repeat(rule_choice(
                rule_seq(rule_string("."), rule_alias(rule_symbol("identifier"), "member_name")),
                rule_seq(rule_string(":"), rule_alias(rule_symbol("identifier"), "method_name")),
            )),
        )),

        ("_type_params", rule_seq(
            rule_string("<"),
            rule_symbol("_type_param"),
            rule_repeat(rule_seq(rule_string(","), rule_symbol("_type_param"))),
            rule_string(">"),
        )),

        # `T`, `T...` (variadic type pack), or `T = Default`.
        ("_type_param", rule_seq(
            rule_alias(rule_symbol("identifier"), "type_param_name"),
            rule_optional(rule_string("...")),
            rule_optional(rule_seq(rule_string("="), rule_symbol("_type"))),
        )),

        ("function_body", rule_seq(
            rule_string("("),
            rule_optional(rule_symbol("_parameter_list")),
            rule_string(")"),
            rule_optional(rule_seq(rule_string(":"), rule_symbol("_type_function_ret"))),
            rule_optional(rule_symbol("block")),
            rule_string("end"),
        )),

        ("_parameter_list", rule_choice(
            rule_seq(
                rule_symbol("parameter"),
                rule_repeat(rule_seq(rule_string(","), rule_symbol("parameter"))),
                rule_optional(rule_seq(
                    rule_string(","), rule_string("..."),
                    rule_optional(rule_seq(rule_string(":"), rule_symbol("_type"))),
                )),
            ),
            rule_seq(
                rule_string("..."),
                rule_optional(rule_seq(rule_string(":"), rule_symbol("_type"))),
            ),
        )),

        ("parameter", rule_seq(
            rule_alias(rule_symbol("identifier"), "parameter_name"),
            rule_optional(rule_seq(rule_string(":"), rule_symbol("_type"))),
        )),
    ]