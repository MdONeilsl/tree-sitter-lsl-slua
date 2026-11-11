# grammars/slua/__init__.py
"""Assemble the SLua grammar from its sub-modules."""

from ..helpers import rule_pattern, rule_symbol
from . import (
    literals,
    type_rules,
    attributes,
    declare,
    structure,
    statements,
    expressions,
)


def build_grammar() -> dict:
    rules_ordered = []
    rules_ordered.extend(structure.rules())   # source_file MUST be first
    rules_ordered.extend(statements.rules())
    rules_ordered.extend(expressions.rules())
    rules_ordered.extend(type_rules.rules())
    rules_ordered.extend(attributes.rules())
    rules_ordered.extend(declare.rules())
    rules_ordered.extend(literals.rules())

    seen = set()
    for name, _ in rules_ordered:
        if name in seen:
            raise RuntimeError(f"duplicate rule definition: {name}")
        seen.add(name)

    return {
        "name": "slua",
        "word": "identifier",
        "rules": dict(rules_ordered),
        "extras": [rule_pattern(r"\s"), rule_symbol("comment")],
        # These two carry over unchanged from the pre-refactor generator.
        # `expression_statement` vs `if_then_else_expression`: at
        # `if c then a • else`, only later context distinguishes the
        # statement-form `if ... end` from the expression-form
        # `if ... then ... else ...`. GLR resolves.
        # `_type_list` vs `_type_parenthesized`: at `(T • )`, only the
        # following `->` distinguishes parameter list from parenthesized.
        "conflicts": [
            ["expression_statement", "if_then_else_expression"],
            ["_type_list", "_type_parenthesized"],
        ],
        "externals": [rule_symbol("long_string_rest")],
        "inline": [],
    }