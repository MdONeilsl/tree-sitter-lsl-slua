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


def rules():
    return [
        ("stat", rule_choice(
            rule_symbol("assign"),
            rule_symbol("expstmt"),
            rule_symbol("dostmt"),
            rule_symbol("whilestmt"),
            rule_symbol("repstmt"),
            rule_symbol("ifstmt"),
            rule_symbol("forstmt"),
            rule_symbol("fundef"),
            rule_symbol("lfuncdef"),
            rule_symbol("localstmt"),
            rule_symbol("conststmt"),
            rule_symbol("typedef"),
            rule_symbol("typefunc"),
            rule_symbol("declare"),
            rule_symbol("laststat"),
            rule_string(";"),
        )),

        ("assign", rule_seq(
            rule_symbol("varlist"),
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
            rule_symbol("explist"),
        )),

        ("varlist", rule_seq(
            rule_symbol("var"),
            rule_repeat(rule_seq(rule_string(","), rule_symbol("var"))),
        )),

        ("var", rule_choice(
            rule_alias(rule_symbol("identifier"), "variable_name"),
            rule_symbol("member"),
            rule_symbol("index"),
        )),

        ("expstmt", rule_symbol("exp")),

        ("dostmt", rule_seq(
            rule_string("do"),
            rule_symbol("block"),
            rule_string("end"),
        )),

        ("whilestmt", rule_seq(
            rule_string("while"),
            rule_symbol("exp"),
            rule_string("do"),
            rule_symbol("block"),
            rule_string("end"),
        )),

        ("repstmt", rule_seq(
            rule_string("repeat"),
            rule_symbol("block"),
            rule_string("until"),
            rule_symbol("exp"),
        )),

        ("ifstmt", rule_seq(
            rule_string("if"),
            rule_symbol("exp"),
            rule_string("then"),
            rule_symbol("block"),
            rule_repeat(rule_seq(
                rule_string("elseif"),
                rule_symbol("exp"),
                rule_string("then"),
                rule_symbol("block"),
            )),
            rule_optional(rule_seq(
                rule_string("else"),
                rule_symbol("block"),
            )),
            rule_string("end"),
        )),

        ("forstmt", rule_choice(
            rule_seq(
                rule_string("for"),
                rule_alias(rule_symbol("identifier"), "variable_name"),
                rule_string("="),
                rule_symbol("exp"),
                rule_string(","),
                rule_symbol("exp"),
                rule_optional(rule_seq(rule_string(","), rule_symbol("exp"))),
                rule_string("do"),
                rule_symbol("block"),
                rule_string("end"),
            ),
            rule_seq(
                rule_string("for"),
                rule_symbol("bindinglist"),
                rule_string("in"),
                rule_symbol("explist"),
                rule_string("do"),
                rule_symbol("block"),
                rule_string("end"),
            ),
        )),

        ("localstmt", rule_seq(
            rule_string("local"),
            rule_symbol("bindinglist"),
            rule_optional(rule_seq(
                rule_string("="),
                rule_symbol("explist"),
            )),
        )),

        ("conststmt", rule_choice(
            rule_seq(
                rule_string("const"),
                rule_symbol("bindinglist"),
                rule_string("="),
                rule_symbol("explist"),
            ),
            rule_seq(
                rule_string("const"),
                rule_string("function"),
                rule_alias(rule_symbol("identifier"), "function_name"),
                rule_symbol("funcbody"),
            ),
        )),

        ("typedef", rule_seq(
            rule_optional(rule_string("export")),
            rule_string("type"),
            rule_alias(rule_symbol("identifier"), "type_identifier"),
            rule_optional(rule_symbol("GenericTypeList")),
            rule_string("="),
            rule_symbol("Type"),
        )),

        ("binding", rule_seq(
            rule_alias(rule_symbol("identifier"), "variable_name"),
            rule_optional(rule_seq(
                rule_string(":"),
                rule_symbol("Type"),
            )),
        )),

        ("bindinglist", rule_seq(
            rule_symbol("binding"),
            rule_repeat(rule_seq(rule_string(","), rule_symbol("binding"))),
        )),

        ("laststat", rule_prec_right(1, rule_choice(
            rule_seq(
                rule_string("return"),
                rule_optional(rule_symbol("explist")),
            ),
            rule_string("break"),
            rule_string("continue"),
        ))),
    ]