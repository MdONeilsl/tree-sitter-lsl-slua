# grammars/slua/statements.py
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
    return [
        rule_symbol("local_declaration"),
        rule_symbol("const_declaration"),
        rule_symbol("local_function_declaration"),
        rule_symbol("function_declaration"),
        rule_symbol("type_declaration"),
        rule_symbol("export_type_declaration"),
        rule_symbol("type_function_declaration"),
        rule_symbol("declare_statement"),
        rule_symbol("if_statement"),
        rule_symbol("while_statement"),
        rule_symbol("repeat_statement"),
        rule_symbol("for_statement"),
        rule_symbol("do_statement"),
        rule_symbol("return_statement"),
        rule_symbol("break_statement"),
        rule_symbol("continue_statement"),
        rule_symbol("assignment_statement"),
        rule_symbol("expression_statement"),
        rule_string(";"),
    ]


def rules():
    return [
        ("_statement", rule_choice(*statement_alternatives())),

        # -- Locals ------------------------------------------------------
        ("local_declaration", rule_seq(
            rule_string("local"),
            rule_symbol("_binding_list"),
            rule_optional(rule_seq(rule_string("="), rule_symbol("_expression_list"))),
        )),

        ("const_declaration", rule_seq(
            rule_string("const"),
            rule_symbol("_binding_list"),
            rule_optional(rule_seq(rule_string("="), rule_symbol("_expression_list"))),
        )),

        ("_binding_list", rule_seq(
            rule_symbol("_binding"),
            rule_repeat(rule_seq(rule_string(","), rule_symbol("_binding"))),
        )),

        # binding: NAME [: Type] [<const>|<close>]
        ("_binding", rule_seq(
            rule_alias(rule_symbol("identifier"), "variable_name"),
            rule_optional(rule_seq(rule_string(":"), rule_symbol("_type"))),
            rule_optional(rule_seq(
                rule_string("<"),
                rule_choice(rule_string("const"), rule_string("close")),
                rule_string(">"),
            )),
        )),

        # -- Type declarations -------------------------------------------
        ("type_declaration", rule_seq(
            rule_string("type"),
            rule_alias(rule_symbol("identifier"), "type_identifier"),
            rule_optional(rule_symbol("_type_params")),
            rule_string("="),
            rule_symbol("_type"),
        )),

        ("export_type_declaration", rule_seq(
            rule_string("export"),
            rule_string("type"),
            rule_alias(rule_symbol("identifier"), "type_identifier"),
            rule_optional(rule_symbol("_type_params")),
            rule_string("="),
            rule_symbol("_type"),
        )),

        ("type_function_declaration", rule_seq(
            rule_optional(rule_string("export")),
            rule_string("type"),
            rule_string("function"),
            rule_alias(rule_symbol("identifier"), "function_name"),
            rule_symbol("function_body"),
        )),

        # -- Control flow ------------------------------------------------
        ("if_statement", rule_seq(
            rule_string("if"),
            rule_symbol("_expression"),
            rule_string("then"),
            rule_optional(rule_symbol("block")),
            rule_repeat(rule_seq(
                rule_string("elseif"),
                rule_symbol("_expression"),
                rule_string("then"),
                rule_optional(rule_symbol("block")),
            )),
            rule_optional(rule_seq(rule_string("else"), rule_optional(rule_symbol("block")))),
            rule_string("end"),
        )),

        ("while_statement", rule_seq(
            rule_string("while"),
            rule_symbol("_expression"),
            rule_string("do"),
            rule_optional(rule_symbol("block")),
            rule_string("end"),
        )),

        ("repeat_statement", rule_seq(
            rule_string("repeat"),
            rule_optional(rule_symbol("block")),
            rule_string("until"),
            rule_symbol("_expression"),
        )),

        ("for_statement", rule_seq(
            rule_string("for"),
            rule_alias(rule_symbol("identifier"), "variable_name"),
            rule_choice(
                rule_seq(
                    rule_string("="),
                    rule_symbol("_expression"),
                    rule_string(","),
                    rule_symbol("_expression"),
                    rule_optional(rule_seq(rule_string(","), rule_symbol("_expression"))),
                ),
                rule_seq(
                    rule_repeat(rule_seq(
                        rule_string(","),
                        rule_alias(rule_symbol("identifier"), "variable_name"),
                    )),
                    rule_string("in"),
                    rule_symbol("_expression_list"),
                ),
            ),
            rule_string("do"),
            rule_optional(rule_symbol("block")),
            rule_string("end"),
        )),

        ("do_statement", rule_seq(
            rule_string("do"),
            rule_optional(rule_symbol("block")),
            rule_string("end"),
        )),

        ("return_statement", rule_prec_right(1, rule_seq(
            rule_string("return"),
            rule_optional(rule_symbol("_expression_list")),
        ))),

        ("break_statement", rule_string("break")),
        ("continue_statement", rule_string("continue")),

        # -- Assignment --------------------------------------------------
        # LHS is a list of assignment targets (name, member access, or index).
        # The alias(identifier, "variable_name") at target positions gives
        # `x = 1` a distinct `variable_name` node; `a.b = 1` and `a[i] = 1`
        # carry the whole member/index node (their own sub-aliases apply).
        ("assignment_statement", rule_seq(
            rule_symbol("_assignment_target_list"),
            rule_choice(
                rule_string("="),
                rule_string("+="),
                rule_string("-="),
                rule_string("*="),
                rule_string("/="),
                rule_string("//="),
                rule_string("%="),
                rule_string("^="),
                rule_string("..="),
            ),
            rule_symbol("_expression_list"),
        )),

        ("_assignment_target_list", rule_seq(
            rule_symbol("_assignment_target"),
            rule_repeat(rule_seq(rule_string(","), rule_symbol("_assignment_target"))),
        )),

        ("_assignment_target", rule_choice(
            rule_alias(rule_symbol("identifier"), "variable_name"),
            rule_symbol("member_access_expression"),
            rule_symbol("index_expression"),
        )),

        ("expression_statement", rule_symbol("_expression")),
    ]