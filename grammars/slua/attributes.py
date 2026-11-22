from ..helpers import rule_alias, rule_choice, rule_optional, rule_repeat, rule_repeat1, rule_seq, rule_string, rule_symbol


def rules():
    return [
        ("attribute", rule_choice(
            rule_seq(
                rule_string("@"),
                rule_alias(rule_symbol("identifier"), "attribute_name"),
            ),
            rule_seq(
                rule_string("@"),
                rule_string("["),
                rule_optional(rule_seq(
                    rule_symbol("parattr"),
                    rule_repeat(rule_seq(rule_string(","), rule_symbol("parattr"))),
                    rule_optional(rule_string(",")),
                )),
                rule_string("]"),
            ),
        )),
        ("parattr", rule_seq(
            rule_alias(rule_symbol("identifier"), "attribute_name"),
            rule_optional(rule_symbol("pars")),
        )),
        ("pars", rule_choice(
            rule_seq(
                rule_string("("),
                rule_optional(rule_seq(
                    rule_choice(
                        rule_seq(
                            rule_alias(rule_symbol("identifier"), "table_field_name"),
                            rule_string("="),
                            rule_symbol("literal"),
                        ),
                        rule_symbol("literal"),
                    ),
                    rule_repeat(rule_seq(
                        rule_string(","),
                        rule_choice(
                            rule_seq(
                                rule_alias(rule_symbol("identifier"), "table_field_name"),
                                rule_string("="),
                                rule_symbol("literal"),
                            ),
                            rule_symbol("literal"),
                        ),
                    )),
                    rule_optional(rule_string(",")),
                )),
                rule_string(")"),
            ),
            rule_symbol("littable"),
            rule_symbol("string"),
        )),
        ("literal", rule_choice(
            rule_string("nil"),
            rule_string("false"),
            rule_string("true"),
            rule_symbol("number"),
            rule_symbol("string"),
            rule_symbol("littable"),
        )),
        ("littable", rule_seq(
            rule_string("{"),
            rule_optional(rule_seq(
                rule_symbol("litfield"),
                rule_repeat(rule_seq(
                    rule_choice(rule_string(","), rule_string(";")),
                    rule_symbol("litfield"),
                )),
                rule_choice(rule_string(","), rule_string(";"), rule_optional(rule_string(","))),
            )),
            rule_string("}"),
        )),
        ("litfield", rule_choice(
            rule_seq(
                rule_alias(rule_symbol("identifier"), "table_field_name"),
                rule_string("="),
                rule_symbol("literal"),
            ),
            rule_symbol("literal"),
        )),
        ("attributes", rule_repeat1(rule_symbol("attribute"))),
    ]