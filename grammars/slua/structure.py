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
        ("source_file", rule_repeat(rule_symbol("stat"))),

        ("block", rule_repeat1(rule_symbol("stat"))),

        ("fundef", rule_seq(
            rule_optional(rule_symbol("attributes")),
            rule_string("function"),
            rule_symbol("funcname"),
            rule_optional(rule_symbol("GenericTypeList")),
            rule_symbol("funcbody"),
        )),

        ("lfuncdef", rule_seq(
            rule_optional(rule_symbol("attributes")),
            rule_string("local"),
            rule_string("function"),
            rule_alias(rule_symbol("identifier"), "function_name"),
            rule_optional(rule_symbol("GenericTypeList")),
            rule_symbol("funcbody"),
        )),

        ("funcname", rule_seq(
            rule_alias(rule_symbol("identifier"), "function_name"),
            rule_repeat(rule_choice(
                rule_seq(rule_string("."), rule_alias(rule_symbol("identifier"), "member_name")),
                rule_seq(rule_string(":"), rule_alias(rule_symbol("identifier"), "method_name")),
            )),
        )),

        ("GenericTypeList", rule_seq(
            rule_string("<"),
            rule_symbol("gtparam"),
            rule_repeat(rule_seq(rule_string(","), rule_symbol("gtparam"))),
            rule_string(">"),
        )),

        ("gtparam", rule_seq(
            rule_alias(rule_symbol("identifier"), "type_param_name"),
            rule_optional(rule_string("...")),
            rule_optional(rule_seq(
                rule_string("="),
                rule_choice(
                    rule_symbol("Type"),
                    rule_seq(rule_string("("), rule_optional(rule_symbol("TypeList")), rule_string(")")),
                    rule_seq(rule_string("..."), rule_symbol("Type")),
                    rule_seq(rule_alias(rule_symbol("identifier"), "type_identifier"), rule_string("...")),
                ),
            )),
        )),

        ("funcbody", rule_seq(
            rule_string("("),
            rule_optional(rule_symbol("parlist")),
            rule_string(")"),
            rule_optional(rule_seq(rule_string(":"), rule_symbol("ReturnType"))),
            rule_optional(rule_symbol("block")),
            rule_string("end"),
        )),

        ("parlist", rule_choice(
            rule_seq(
                rule_symbol("binding"),
                rule_repeat(rule_seq(rule_string(","), rule_symbol("binding"))),
                rule_optional(rule_seq(
                    rule_string(","), rule_string("..."),
                    rule_optional(rule_seq(rule_string(":"), rule_symbol("Type"))),
                )),
            ),
            rule_seq(
                rule_string("..."),
                rule_optional(rule_seq(rule_string(":"), rule_symbol("Type"))),
            ),
        )),
    ]