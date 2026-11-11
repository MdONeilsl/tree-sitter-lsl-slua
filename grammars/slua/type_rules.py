# grammars/slua/type_rules.py
from ..helpers import (
    rule_alias,
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
        # Hidden dispatcher — the visible leaves are what matter.
        ("_type", rule_symbol("_type_union")),

        ("_type_union", rule_choice(
            rule_symbol("_type_intersection"),
            rule_prec_left(1, rule_seq(
                rule_symbol("_type_union"),
                rule_string("|"),
                rule_symbol("_type_intersection"),
            )),
        )),

        ("_type_intersection", rule_choice(
            rule_symbol("_type_optional"),
            rule_prec_left(2, rule_seq(
                rule_symbol("_type_intersection"),
                rule_string("&"),
                rule_symbol("_type_optional"),
            )),
        )),

        ("_type_optional", rule_choice(
            rule_symbol("_type_simple"),
            rule_prec(3, rule_seq(
                rule_symbol("_type_simple"),
                rule_string("?"),
            )),
        )),

        ("_type_simple", rule_choice(
            rule_symbol("_type_reference"),
            rule_symbol("_type_table"),
            rule_symbol("_type_function"),
            rule_symbol("_type_parenthesized"),
            rule_seq(rule_string("typeof"), rule_string("("), rule_symbol("_expression"), rule_string(")")),
            rule_seq(rule_string("..."), rule_symbol("_type")),
            rule_string("nil"),
            rule_string("true"),
            rule_string("false"),
        )),

        ("_type_reference", rule_choice(
            rule_symbol("_type_reference_plain"),
            rule_symbol("_type_reference_generic"),
        )),

        # `T` or `T...` (variadic type pack). The `prec.right` on the whole
        # rule prefers the shift of `...` over reducing to plain `T`.
        # Every identifier leaf is aliased to `type_identifier`.
        ("_type_reference_plain", rule_prec_right(1, rule_choice(
            rule_seq(rule_alias(rule_symbol("identifier"), "type_identifier"), rule_string("...")),
            rule_alias(rule_symbol("identifier"), "type_identifier"),
        ))),

        # `Array<T>`, `Pair<K, V>`. The base name is `type_identifier`;
        # each argument recursively reaches its own `type_identifier`.
        ("_type_reference_generic", rule_seq(
            rule_alias(rule_symbol("identifier"), "type_identifier"),
            rule_string("<"),
            rule_symbol("_type_list"),
            rule_string(">"),
        )),

        ("_type_list", rule_seq(
            rule_symbol("_type"),
            rule_repeat(rule_seq(rule_string(","), rule_symbol("_type"))),
        )),

        ("_type_parenthesized", rule_seq(
            rule_string("("),
            rule_symbol("_type"),
            rule_string(")"),
        )),

        ("_type_table", rule_choice(
            # Array type: `{ T }`
            rule_seq(rule_string("{"), rule_symbol("_type"), rule_string("}")),
            # Struct / indexer: `{ ... }` or `{}`
            rule_seq(
                rule_string("{"),
                rule_optional(rule_seq(
                    rule_symbol("type_table_prop"),
                    rule_repeat(rule_seq(
                        rule_choice(rule_string(","), rule_string(";")),
                        rule_symbol("type_table_prop"),
                    )),
                    rule_choice(rule_string(","), rule_string(";"), rule_optional(rule_string(","))),
                )),
                rule_string("}"),
            ),
        )),

        ("type_table_prop", rule_choice(
            # Computed key: `[K]: V` — K is a full type.
            rule_seq(rule_string("["), rule_symbol("_type"), rule_string("]"), rule_string(":"), rule_symbol("_type")),
            # Named key: `name: V` — name is a field of the struct type.
            rule_seq(rule_alias(rule_symbol("identifier"), "type_table_field"), rule_string(":"), rule_symbol("_type")),
        )),

        ("_type_function", rule_seq(
            rule_symbol("_type_function_params"),
            rule_string("->"),
            rule_symbol("_type_function_ret"),
        )),

        ("_type_function_params", rule_seq(
            rule_string("("),
            rule_optional(rule_symbol("_type_list")),
            rule_string(")"),
        )),

        ("_type_function_ret", rule_choice(
            rule_symbol("_type"),
            rule_seq(rule_string("("), rule_optional(rule_symbol("_type_list")), rule_string(")")),
        )),
    ]