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
    return rule_choice(
        rule_alias(rule_symbol("identifier"), "member_object_name"),
        rule_symbol("member"),
        rule_symbol("functioncall"),
        rule_symbol("index"),
        rule_symbol("paren"),
    )


def _call_target():
    return rule_choice(
        rule_alias(rule_symbol("identifier"), "function_name"),
        rule_symbol("member"),
        rule_symbol("functioncall"),
        rule_symbol("index"),
        rule_symbol("paren"),
    )


def _funcargs():
    return rule_choice(
        rule_symbol("args"),
        rule_symbol("tableconstructor"),
        rule_symbol("string"),
        rule_symbol("stringinterp"),
    )


def rules():
    return [
        ("exp", rule_choice(
            rule_symbol("binexp"),
            rule_symbol("unexp"),
            rule_symbol("ifelseexp"),
            rule_symbol("tassert"),
            rule_symbol("prefixexp"),
            rule_symbol("funcdef"),
            rule_symbol("tableconstructor"),
            rule_symbol("number"),
            rule_symbol("string"),
            rule_symbol("stringinterp"),
            rule_alias(rule_string("nil"), "nil"),
            rule_alias(rule_string("true"), "true"),
            rule_alias(rule_string("false"), "false"),
            rule_alias(rule_string("..."), "..."),
        )),

        ("explist", rule_seq(
            rule_symbol("exp"),
            rule_repeat(rule_seq(rule_string(","), rule_symbol("exp"))),
        )),

        ("binexp", rule_choice(
            rule_prec_left(1, rule_seq(rule_symbol("exp"), rule_string("or"), rule_symbol("exp"))),
            rule_prec_left(2, rule_seq(rule_symbol("exp"), rule_string("and"), rule_symbol("exp"))),
            rule_prec_left(3, rule_seq(
                rule_symbol("exp"),
                rule_choice(
                    rule_string("<"), rule_string(">"),
                    rule_string("<="), rule_string(">="),
                    rule_string("~="), rule_string("=="),
                ),
                rule_symbol("exp"),
            )),
            rule_prec_right(4, rule_seq(rule_symbol("exp"), rule_string(".."), rule_symbol("exp"))),
            rule_prec_left(5, rule_seq(rule_symbol("exp"), rule_choice(rule_string("+"), rule_string("-")), rule_symbol("exp"))),
            rule_prec_left(6, rule_seq(
                rule_symbol("exp"),
                rule_choice(rule_string("*"), rule_string("/"), rule_string("//"), rule_string("%")),
                rule_symbol("exp"),
            )),
            rule_prec_right(7, rule_seq(rule_symbol("exp"), rule_string("^"), rule_symbol("exp"))),
        )),

        ("unexp", rule_prec(8, rule_seq(
            rule_choice(rule_string("not"), rule_string("#"), rule_string("-")),
            rule_symbol("exp"),
        ))),

        ("ifelseexp", rule_seq(
            rule_string("if"),
            rule_symbol("exp"),
            rule_string("then"),
            rule_symbol("exp"),
            rule_repeat(rule_seq(
                rule_string("elseif"),
                rule_symbol("exp"),
                rule_string("then"),
                rule_symbol("exp"),
            )),
            rule_string("else"),
            rule_symbol("exp"),
        )),

        ("tassert", rule_seq(
            rule_choice(
                rule_symbol("prefixexp"),
                rule_symbol("number"),
                rule_symbol("string"),
                rule_symbol("stringinterp"),
                rule_string("true"),
                rule_string("false"),
                rule_string("nil"),
                rule_string("..."),
            ),
            rule_string("::"),
            rule_symbol("Type"),
        )),

        ("prefixexp", rule_choice(
            rule_symbol("identifier"),
            rule_symbol("member"),
            rule_symbol("functioncall"),
            rule_symbol("index"),
            rule_symbol("paren"),
            rule_symbol("nonnull"),
        )),

        ("member", rule_prec_left(1, rule_seq(
            _member_object(),
            rule_string("."),
            rule_alias(rule_symbol("identifier"), "member_name"),
        ))),

        ("functioncall", rule_prec_left(1, rule_choice(
            rule_seq(_call_target(), _funcargs()),
            rule_seq(
                _member_object(),
                rule_string(":"),
                rule_alias(rule_symbol("identifier"), "method_name"),
                _funcargs(),
            ),
        ))),

                ("index", rule_prec_left(14, rule_seq(
            rule_choice(
                rule_alias(rule_symbol("identifier"), "variable_name"),
                rule_symbol("member"),
                rule_symbol("functioncall"),
                rule_symbol("index"),
                rule_symbol("paren"),
                rule_symbol("nonnull"),
            ),
            rule_string("["),
            rule_symbol("exp"),
            rule_string("]"),
        ))),

        ("paren", rule_seq(
            rule_string("("),
            rule_symbol("exp"),
            rule_string(")"),
        )),

        ("args", rule_seq(
            rule_string("("),
            rule_optional(rule_symbol("explist")),
            rule_string(")"),
        )),

        ("nonnull", rule_prec_left(15, rule_seq(
            rule_symbol("prefixexp"),
            rule_string("!"),
        ))),

        ("funcdef", rule_seq(
            rule_optional(rule_symbol("attributes")),
            rule_string("function"),
            rule_optional(rule_symbol("GenericTypeList")),
            rule_symbol("funcbody"),
        )),

        ("tableconstructor", rule_seq(
            rule_string("{"),
            rule_optional(rule_symbol("fieldlist")),
            rule_string("}"),
        )),

        ("fieldlist", rule_seq(
            rule_symbol("field"),
            rule_repeat(rule_seq(
                rule_choice(rule_string(","), rule_string(";")),
                rule_symbol("field"),
            )),
            rule_choice(rule_string(","), rule_string(";"), rule_optional(rule_string(","))),
        )),

        ("field", rule_choice(
            rule_seq(rule_string("["), rule_symbol("exp"), rule_string("]"), rule_string("="), rule_symbol("exp")),
            rule_seq(rule_alias(rule_symbol("identifier"), "table_field_name"), rule_string("="), rule_symbol("exp")),
            rule_symbol("exp"),
        )),
    ]