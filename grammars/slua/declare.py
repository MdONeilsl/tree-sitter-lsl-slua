from ..helpers import (
    rule_alias,
    rule_choice,
    rule_optional,
    rule_repeat,
    rule_seq,
    rule_string,
    rule_symbol,
)


def rules():
    return [
        ("declare", rule_choice(
            rule_symbol("declfunc"),
            rule_symbol("decltype"),
            rule_symbol("exttype"),
            rule_symbol("declvar"),
            rule_symbol("declclass"),
        )),

        ("declclass", rule_seq(
            rule_string("declare"),
            rule_string("class"),
            rule_alias(rule_symbol("identifier"), "class_identifier"),
            rule_optional(rule_seq(
                rule_string("extends"),
                rule_symbol("type_reference"),
            )),
            rule_repeat(rule_choice(
                rule_symbol("declfunc"),
                rule_symbol("extfunc"),
                rule_symbol("fielddecl"),
                rule_string(";"),
            )),
            rule_string("end"),
        )),

        ("typefunc", rule_seq(
            rule_string("type"),
            rule_string("function"),
            rule_alias(rule_symbol("identifier"), "function_name"),
            rule_optional(rule_symbol("GenericTypeList")),
            rule_symbol("funcbody"),
        )),

        ("declfunc", rule_seq(
            rule_optional(rule_symbol("attributes")),
            rule_string("declare"),
            rule_optional(rule_string("extern")),
            rule_string("function"),
            rule_alias(rule_symbol("identifier"), "function_name"),
            rule_optional(rule_symbol("GenericTypeList")),
            rule_string("("),
            rule_optional(rule_symbol("parlist")),
            rule_string(")"),
            rule_optional(rule_seq(rule_string(":"), rule_symbol("ReturnType"))),
        )),

        ("decltype", rule_seq(
            rule_string("declare"),
            rule_string("type"),
            rule_alias(rule_symbol("identifier"), "type_identifier"),
            rule_optional(rule_symbol("GenericTypeList")),
            rule_string("="),
            rule_symbol("Type"),
        )),

        ("exttype", rule_seq(
            rule_string("declare"),
            rule_string("extern"),
            rule_string("type"),
            rule_alias(rule_symbol("identifier"), "type_identifier"),
            rule_string("with"),
            rule_repeat(rule_choice(
                rule_symbol("declfunc"),
                rule_symbol("extfunc"),
                rule_symbol("fielddecl"),
                rule_string(";"),
            )),
            rule_string("end"),
        )),

        ("extfunc", rule_seq(
            rule_optional(rule_symbol("attributes")),
            rule_string("function"),
            rule_alias(rule_symbol("identifier"), "function_name"),
            rule_optional(rule_symbol("GenericTypeList")),
            rule_string("("),
            rule_optional(rule_symbol("parlist")),
            rule_string(")"),
            rule_optional(rule_seq(rule_string(":"), rule_symbol("ReturnType"))),
        )),

        ("declvar", rule_seq(
            rule_optional(rule_symbol("attributes")),
            rule_string("declare"),
            rule_alias(rule_symbol("identifier"), "variable_name"),
            rule_string(":"),
            rule_symbol("Type"),
        )),

        ("fielddecl", rule_seq(
            rule_optional(rule_symbol("attributes")),
            rule_optional(rule_choice(rule_string("read"), rule_string("write"))),
            rule_alias(rule_symbol("identifier"), "type_table_field"),
            rule_string(":"),
            rule_symbol("Type"),
        )),
    ]