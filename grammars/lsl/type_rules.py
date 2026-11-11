# grammars/lsl/type_rules.py
from ..helpers import rule_choice, rule_string


def rules():
    return [
        # `quaternion` is the LSO-era synonym for `rotation`. Both are
        # accepted by LSO scripts; `rotation` is preferred in Mono.
        ("type", rule_choice(
            rule_string("integer"),
            rule_string("float"),
            rule_string("string"),
            rule_string("key"),
            rule_string("vector"),
            rule_string("rotation"),
            rule_string("quaternion"),
            rule_string("list"),
        )),
    ]