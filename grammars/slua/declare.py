# grammars/slua/declare.py
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
        ("declare_statement", rule_seq(
            rule_optional(rule_symbol("_attributes")),
            rule_string("declare"),
            rule_choice(
                # declare foo: Type
                rule_seq(
                    rule_alias(rule_symbol("identifier"), "declared_name"),
                    rule_string(":"),
                    rule_symbol("_type"),
                ),
                # declare function foo<T>(...): RetType
                rule_seq(
                    rule_string("function"),
                    rule_alias(rule_symbol("identifier"), "declared_name"),
                    rule_optional(rule_symbol("_type_params")),
                    rule_symbol("function_body_decl"),
                ),
                # declare class Foo [extends Base] members... end
                rule_seq(
                    rule_string("class"),
                    rule_alias(rule_symbol("identifier"), "declared_name"),
                    rule_optional(rule_seq(
                        rule_string("extends"),
                        rule_alias(rule_symbol("identifier"), "type_identifier"),
                    )),
                    rule_repeat(rule_symbol("_class_member")),
                    rule_string("end"),
                ),
            ),
        )),

        ("function_body_decl", rule_seq(
            rule_string("("),
            rule_optional(rule_symbol("_parameter_list")),
            rule_string(")"),
            rule_optional(rule_seq(rule_string(":"), rule_symbol("_type_function_ret"))),
        )),

        ("_class_member", rule_choice(
            rule_seq(rule_alias(rule_symbol("identifier"), "table_field_name"), rule_string(":"), rule_symbol("_type")),
            rule_seq(rule_string("["), rule_symbol("string"), rule_string("]"), rule_string(":"), rule_symbol("_type")),
            rule_seq(rule_string("["), rule_symbol("_type"), rule_string("]"), rule_string(":"), rule_symbol("_type")),
            rule_seq(rule_string("function"), rule_alias(rule_symbol("identifier"), "method_name"), rule_symbol("function_body_decl")),
        )),
    ]