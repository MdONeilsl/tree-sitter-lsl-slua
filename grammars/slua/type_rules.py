from ..helpers import (
    rule_alias,
    rule_choice,
    rule_optional,
    rule_prec,
    rule_prec_left,
    rule_prec_right,
    rule_repeat,
    rule_repeat1,
    rule_seq,
    rule_string,
    rule_symbol,
)


def rules():
    return [
        ("Type", rule_symbol("Union")),

        ("Union", rule_prec_left(1, rule_seq(
            rule_symbol("Intersection"),
            rule_repeat(rule_seq(
                rule_string("|"),
                rule_symbol("Intersection"),
            )),
        ))),

        ("Intersection", rule_prec_left(2, rule_seq(
            rule_optional(rule_symbol("attributes")),
            rule_symbol("SimpleType"),
            rule_repeat(rule_seq(
                rule_string("&"),
                rule_symbol("SimpleType"),
            )),
        ))),

        ("SimpleType", rule_choice(
            rule_symbol("typeapp"),
            rule_symbol("VariadicTypePack"),
            rule_prec_right(1, rule_seq(
                rule_symbol("VariadicTypePack"),
                rule_string("?"),
            )),
            rule_alias(rule_symbol("identifier"), "type_identifier"),
            rule_symbol("builtin"),
            rule_symbol("TableType"),
            rule_symbol("FunctionType"),
            rule_symbol("typeof"),
            rule_symbol("typemember"),
            rule_symbol("tparen"),
            rule_symbol("string"),
            rule_prec(3, rule_seq(
                rule_choice(
                    rule_symbol("typeapp"),
                    rule_alias(rule_symbol("identifier"), "type_identifier"),
                    rule_symbol("builtin"),
                    rule_symbol("TableType"),
                    rule_symbol("FunctionType"),
                    rule_symbol("typeof"),
                    rule_symbol("typemember"),
                    rule_symbol("tparen"),
                    rule_symbol("string"),
                ),
                rule_string("?"),
            )),
        )),

        ("VariadicTypePack", rule_prec(3, rule_seq(
            rule_choice(
                rule_symbol("typeapp"),
                rule_symbol("typemember"),
                rule_alias(rule_symbol("identifier"), "type_identifier"),
            ),
            rule_string("..."),
        ))),

        ("typeof", rule_seq(
            rule_string("typeof"),
            rule_string("("),
            rule_symbol("exp"),
            rule_string(")"),
        )),

        ("builtin", rule_choice(
            rule_string("nil"),
            rule_string("boolean"),
            rule_string("number"),
            rule_string("string"),
            rule_string("thread"),
            rule_string("userdata"),
            rule_string("any"),
            rule_string("never"),
            rule_string("buffer"),
        )),

        ("type_reference", rule_choice(
            rule_symbol("type_reference_plain"),
            rule_symbol("typeapp"),
        )),

        ("type_reference_plain", rule_prec_right(1, rule_seq(
            rule_choice(
                rule_alias(rule_symbol("identifier"), "type_identifier"),
                rule_symbol("typemember"),
            ),
            rule_optional(rule_string("...")),
        ))),

        ("typeapp", rule_prec(1, rule_seq(
            rule_choice(
                rule_alias(rule_symbol("identifier"), "type_identifier"),
                rule_symbol("typemember"),
            ),
            rule_string("<"),
            rule_symbol("TypeList"),
            rule_string(">"),
        ))),

        ("TypeList", rule_seq(
            rule_choice(
                rule_symbol("Type"),
                rule_seq(rule_string("..."), rule_symbol("Type")),
            ),
            rule_repeat(rule_seq(
                rule_string(","),
                rule_choice(
                    rule_symbol("Type"),
                    rule_seq(rule_string("..."), rule_symbol("Type")),
                ),
            )),
            rule_optional(rule_string(",")),
        )),

        ("tparen", rule_seq(
            rule_string("("),
            rule_symbol("Type"),
            rule_string(")"),
        )),

        ("TableType", rule_seq(
            rule_string("{"),
            rule_optional(
                rule_seq(
                    rule_choice(
                        rule_symbol("TableProp"),
                        rule_symbol("TableIndexer"),
                        rule_symbol("Type"),
                    ),
                    rule_repeat(
                        rule_seq(
                            rule_choice(rule_string(","), rule_string(";")),
                            rule_choice(
                                rule_symbol("TableProp"),
                                rule_symbol("TableIndexer"),
                                rule_symbol("Type"),
                            )
                        )
                    ),
                    rule_optional(rule_choice(rule_string(","), rule_string(";")))
                )
            ),
            rule_string("}"),
        )),

        ("TableIndexer", rule_seq(
            rule_optional(rule_choice(rule_string("read"), rule_string("write"))),
            rule_string("["),
            rule_symbol("Type"),
            rule_string("]"),
            rule_string(":"),
            rule_symbol("Type"),
        )),

        ("TableProp", rule_seq(
            rule_optional(rule_choice(rule_string("read"), rule_string("write"))),
            rule_alias(rule_symbol("identifier"), "type_table_field"),
            rule_string(":"),
            rule_symbol("Type"),
        )),

        ("typemember", rule_seq(
            rule_alias(rule_symbol("identifier"), "type_identifier"),
            rule_repeat1(rule_seq(
                rule_string("."),
                rule_alias(rule_symbol("identifier"), "type_identifier"),
            )),
        )),

        ("FunctionType", rule_seq(
            rule_optional(rule_symbol("GenericTypeList")),
            rule_string("("),
            rule_optional(
                rule_seq(
                    rule_choice(
                        rule_seq(
                            rule_string("..."),
                            rule_optional(rule_choice(
                                rule_seq(rule_string(":"), rule_symbol("Type")),
                                rule_symbol("Type"),
                            )),
                        ),
                        rule_seq(
                            rule_alias(rule_symbol("builtin"), "parameter_name"),
                            rule_string(":"),
                            rule_symbol("Type"),
                        ),
                        rule_seq(
                            rule_optional(rule_seq(rule_alias(rule_symbol("identifier"), "parameter_name"), rule_string(":"))),
                            rule_symbol("Type")
                        ),
                    ),
                    rule_repeat(
                        rule_seq(
                            rule_string(","),
                            rule_choice(
                                rule_seq(
                                    rule_string("..."),
                                    rule_optional(rule_choice(
                                        rule_seq(rule_string(":"), rule_symbol("Type")),
                                        rule_symbol("Type"),
                                    )),
                                ),
                                rule_seq(
                                    rule_alias(rule_symbol("builtin"), "parameter_name"),
                                    rule_string(":"),
                                    rule_symbol("Type"),
                                ),
                                rule_seq(
                                    rule_optional(rule_seq(rule_alias(rule_symbol("identifier"), "parameter_name"), rule_string(":"))),
                                    rule_symbol("Type")
                                ),
                            )
                        )
                    ),
                    rule_optional(rule_string(","))
                )
            ),
            rule_string(")"),
            rule_string("->"),
            rule_choice(
                rule_symbol("Type"),
                rule_seq(rule_string("("), rule_optional(rule_symbol("TypeList")), rule_string(")")),
                rule_seq(rule_string("..."), rule_symbol("Type")),
            ),
        )),

        ("ReturnType", rule_choice(
            rule_symbol("Type"),
            rule_seq(rule_string("("), rule_optional(rule_symbol("TypeList")), rule_string(")")),
            rule_seq(rule_string("..."), rule_symbol("Type")),
        )),
    ]