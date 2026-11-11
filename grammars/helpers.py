# grammars/helpers.py
"""Primitive rule builders for Tree-sitter grammar.json format."""


def rule_string(value):
    return {"type": "STRING", "value": value}


def rule_pattern(value):
    return {"type": "PATTERN", "value": value}


def rule_seq(*members):
    return {"type": "SEQ", "members": list(members)}


def rule_choice(*members):
    return {"type": "CHOICE", "members": list(members)}


def rule_repeat(member):
    return {"type": "REPEAT", "content": member}


def rule_repeat1(member):
    return {"type": "REPEAT1", "content": member}


def rule_symbol(name):
    return {"type": "SYMBOL", "name": name}


def rule_field(name, content):
    return {"type": "FIELD", "name": name, "content": content}


def rule_blank():
    return {"type": "BLANK"}


def rule_optional(content):
    return rule_choice(content, rule_blank())


def rule_alias(content, value):
    """Rename a rule's node type in the tree without adding a nesting level."""
    return {"type": "ALIAS", "content": content, "named": True, "value": value}


def rule_prec(level, content):
    return {"type": "PREC", "value": level, "content": content}


def rule_prec_left(level, content):
    return {"type": "PREC_LEFT", "value": level, "content": content}


def rule_prec_right(level, content):
    return {"type": "PREC_RIGHT", "value": level, "content": content}