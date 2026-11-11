# grammars/lsl/type_rules.py
from ..helpers import rule_choice, rule_string


def rules():
    return [
        ("type", rule_choice(
            rule_string("integer"),
            rule_string("float"),
            rule_string("string"),
            rule_string("key"),
            rule_string("vector"),
            rule_string("rotation"),
            rule_string("list"),
        )),
    ]