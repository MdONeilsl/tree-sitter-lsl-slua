# grammars/slua/attributes.py
from ..helpers import rule_alias, rule_repeat1, rule_seq, rule_string, rule_symbol


def rules():
    return [
        # `@name` only — Luau attributes take no arguments.
        ("attribute", rule_seq(
            rule_string("@"),
            rule_alias(rule_symbol("identifier"), "attribute_name"),
        )),
        ("_attributes", rule_repeat1(rule_symbol("attribute"))),
    ]