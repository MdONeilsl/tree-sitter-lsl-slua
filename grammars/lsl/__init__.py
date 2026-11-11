# grammars/lsl/__init__.py
"""Assemble the LSL grammar from its sub-modules."""

from ..helpers import rule_pattern, rule_symbol
from . import literals, type_rules, structure, statements, expressions


def build_grammar() -> dict:
    rules_ordered = []
    rules_ordered.extend(structure.rules())   # source_file MUST be first
    rules_ordered.extend(statements.rules())
    rules_ordered.extend(expressions.rules())
    rules_ordered.extend(type_rules.rules())
    rules_ordered.extend(literals.rules())

    seen = set()
    for name, _ in rules_ordered:
        if name in seen:
            raise RuntimeError(f"duplicate rule definition: {name}")
        seen.add(name)

    return {
        "name": "lsl",
        "word": "identifier",
        "rules": dict(rules_ordered),
        "extras": [rule_pattern(r"\s"), rule_symbol("comment")],
        # GLR fallback: at `identifier • [`, the parser must try both
        # "reduce identifier to _expression, then [ opens an index" and
        # "shift [ into lazy_list_assignment". Only the token after `]`
        # distinguishes them. This conflict was present before the
        # refactor; dropping it during the split broke the build.
        "conflicts": [
            ["lazy_list_assignment", "_expression"],
        ],
        "externals": [],
        "inline": [],
    }