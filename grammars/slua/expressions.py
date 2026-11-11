# grammars/slua/expressions.py
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


def _member_object():
    """Left-hand side of a `.` / `:` chain. Bare identifier gets the
    `member_object_name` alias; complex expressions keep their own type."""
    return rule_choice(
        rule_alias(rule_symbol("identifier"), "member_object_name"),
        rule_symbol("member_access_expression"),
        rule_symbol("method_call_expression"),
        rule_symbol("call_expression"),
        rule_symbol("index_expression"),
        rule_symbol("parenthesized_expression"),
    )


def _call_target():
    """Left-hand side of `(...)`. A bare identifier gets `function_name`;
    complex expressions keep their own type."""
    return rule_choice(
        rule_alias(rule_symbol("identifier"), "function_name"),
        rule_symbol("member_access_expression"),
        rule_symbol("method_call_expression"),
        rule_symbol("call_expression"),
        rule_symbol("index_expression"),
        rule_symbol("parenthesized_expression"),
    )


def rules():
    return [
        # Hidden dispatcher — all alternatives are visible nodes.
        ("_expression", rule_choice(
            rule_symbol("binary_expression"),
            rule_symbol("unary_expression"),
            rule_symbol("if_then_else_expression"),
            rule_symbol("type_assertion"),
            rule_symbol("_suffixed_expression"),
            rule_symbol("function_definition"),
            rule_symbol("table_constructor"),
            rule_symbol("number"),
            rule_symbol("string"),
            rule_symbol("interpolated_string"),
            rule_string("nil"),
            rule_string("true"),
            rule_string("false"),
            rule_string("..."),
        )),

        ("_expression_list", rule_seq(
            rule_symbol("_expression"),
            rule_repeat(rule_seq(rule_string(","), rule_symbol("_expression"))),
        )),

        ("binary_expression", rule_choice(
            rule_prec_left(1, rule_seq(rule_symbol("_expression"), rule_string("or"), rule_symbol("_expression"))),
            rule_prec_left(2, rule_seq(rule_symbol("_expression"), rule_string("and"), rule_symbol("_expression"))),
            rule_prec_left(3, rule_seq(
                rule_symbol("_expression"),
                rule_choice(
                    rule_string("<"), rule_string(">"),
                    rule_string("<="), rule_string(">="),
                    rule_string("~="), rule_string("=="),
                ),
                rule_symbol("_expression"),
            )),
            rule_prec_right(4, rule_seq(rule_symbol("_expression"), rule_string(".."), rule_symbol("_expression"))),
            rule_prec_left(5, rule_seq(rule_symbol("_expression"), rule_choice(rule_string("+"), rule_string("-")), rule_symbol("_expression"))),
            rule_prec_left(6, rule_seq(
                rule_symbol("_expression"),
                rule_choice(rule_string("*"), rule_string("/"), rule_string("//"), rule_string("%")),
                rule_symbol("_expression"),
            )),
        )),

        ("unary_expression", rule_prec(7, rule_seq(
            rule_choice(rule_string("not"), rule_string("#"), rule_string("-")),
            rule_symbol("_expression"),
        ))),

        ("if_then_else_expression", rule_seq(
            rule_string("if"),
            rule_symbol("_expression"),
            rule_string("then"),
            rule_symbol("_expression"),
            rule_repeat(rule_seq(
                rule_string("elseif"),
                rule_symbol("_expression"),
                rule_string("then"),
                rule_symbol("_expression"),
            )),
            rule_string("else"),
            rule_symbol("_expression"),
        )),

                # `expr :: Type` — type assertion. In Luau the left side is any
        # expression; the atom forms (`"hi" :: string`, `42 :: number`,
        # `true :: boolean`) are common in typed code and must be
        # accepted, not just suffixed expressions.
        ("type_assertion", rule_seq(
            rule_choice(
                rule_symbol("_suffixed_expression"),
                rule_symbol("number"),
                rule_symbol("string"),
                rule_symbol("interpolated_string"),
                rule_string("true"),
                rule_string("false"),
                rule_string("nil"),
                rule_string("..."),
            ),
            rule_string("::"),
            rule_symbol("_type"),
        )),

        # Hidden dispatcher for the member / call / index / atom chain.
        ("_suffixed_expression", rule_choice(
            rule_symbol("identifier"),
            rule_symbol("member_access_expression"),
            rule_symbol("method_call_expression"),
            rule_symbol("call_expression"),
            rule_symbol("index_expression"),
            rule_symbol("parenthesized_expression"),
        )),

        # `a.b` — member read. `prec.left(1)` prefers the shift of `.`
        # over reducing `a` to plain identifier; that is what makes the
        # alias on the left fire.
        ("member_access_expression", rule_prec_left(1, rule_seq(
            _member_object(),
            rule_string("."),
            rule_alias(rule_symbol("identifier"), "member_name"),
        ))),

        # `a:b(...)` — method dispatch.
        ("method_call_expression", rule_prec_left(1, rule_seq(
            _member_object(),
            rule_string(":"),
            rule_alias(rule_symbol("identifier"), "method_name"),
            rule_symbol("argument_list"),
        ))),

        # `a(...)` — plain call. `a` becomes `function_name` unless it is
        # itself a member/method/index, in which case it keeps that type.
        ("call_expression", rule_prec_left(1, rule_seq(
            _call_target(),
            rule_symbol("argument_list"),
        ))),

        # `a[i]` — index. LHS keeps its own type; the alias only fires
        # for a bare identifier on the far left of a longer chain.
        ("index_expression", rule_prec_left(14, rule_seq(
            rule_symbol("_suffixed_expression"),
            rule_string("["),
            rule_symbol("_expression"),
            rule_string("]"),
        ))),

        ("parenthesized_expression", rule_seq(
            rule_string("("),
            rule_symbol("_expression"),
            rule_string(")"),
        )),

        ("argument_list", rule_seq(
            rule_string("("),
            rule_optional(rule_symbol("_expression_list")),
            rule_string(")"),
        )),

        ("function_definition", rule_seq(
            rule_optional(rule_symbol("_attributes")),
            rule_string("function"),
            rule_optional(rule_symbol("_type_params")),
            rule_symbol("function_body"),
        )),

        # Table constructor. `{ x = 1 }` aliases `x` as `table_field_name`;
        # `{ [complexExpr] = 1 }` treats the bracket as a full expression
        # and every sub-part carries its own alias.
        ("table_constructor", rule_seq(
            rule_string("{"),
            rule_optional(rule_symbol("_field_list")),
            rule_string("}"),
        )),

        ("_field_list", rule_seq(
            rule_symbol("_field"),
            rule_repeat(rule_seq(
                rule_choice(rule_string(","), rule_string(";")),
                rule_symbol("_field"),
            )),
            rule_choice(rule_string(","), rule_string(";"), rule_optional(rule_string(","))),
        )),

        ("_field", rule_choice(
            rule_seq(rule_string("["), rule_symbol("_expression"), rule_string("]"), rule_string("="), rule_symbol("_expression")),
            rule_seq(rule_alias(rule_symbol("identifier"), "table_field_name"), rule_string("="), rule_symbol("_expression")),
            rule_symbol("_expression"),
        )),
    ]