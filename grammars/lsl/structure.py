# grammars/lsl/structure.py
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
        # source_file MUST be the first rule — Tree-sitter uses it as the start rule.
        ("source_file", rule_repeat(rule_choice(
            rule_symbol("global_declaration"),
            rule_symbol("state_definition"),
            rule_symbol("preproc_directive"),
        ))),

        # A global declaration is a variable declared at script scope.
        # The wrapper node distinguishes it from a local declaration.
        ("global_declaration", rule_symbol("variable_declaration")),

        ("state_definition", rule_seq(
            rule_choice(
                rule_string("default"),
                rule_seq(
                    rule_string("state"),
                    rule_alias(rule_symbol("identifier"), "state_name"),
                ),
            ),
            rule_string("{"),
            rule_repeat(rule_choice(
                rule_symbol("event_handler"),
                rule_symbol("preproc_directive"),
            )),
            rule_string("}"),
        )),

        ("event_handler", rule_seq(
            rule_alias(rule_symbol("identifier"), "event_name"),
            rule_symbol("parameter_list"),
            rule_symbol("block"),
        )),

        ("parameter_list", rule_seq(
            rule_string("("),
            rule_optional(rule_seq(
                rule_symbol("parameter"),
                rule_repeat(rule_seq(rule_string(","), rule_symbol("parameter"))),
            )),
            rule_string(")"),
        )),

        ("parameter", rule_seq(
            rule_symbol("type"),
            rule_alias(rule_symbol("identifier"), "parameter_name"),
        )),
    ]