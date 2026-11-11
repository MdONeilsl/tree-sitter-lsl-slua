# lsl/generate_lsl_grammar.py
import json
import pathlib


# ---------------------------------------------------------------------------
# Primitive rule builders
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Precedence helpers
# ---------------------------------------------------------------------------
def rule_prec(level, content):
    return {"type": "PREC", "value": level, "content": content}


def rule_prec_left(level, content):
    return {"type": "PREC_LEFT", "value": level, "content": content}


def rule_prec_right(level, content):
    return {"type": "PREC_RIGHT", "value": level, "content": content}


# ---------------------------------------------------------------------------
# Grammar
# ---------------------------------------------------------------------------
def build_grammar():
    rules_ordered = []

    # 1. Start rule — MUST be first.
    rules_ordered.append((
        "source_file",
        rule_repeat(
            rule_choice(
                rule_symbol("global_declaration"),
                rule_symbol("state_definition"),
            )
        )
    ))

    # 2. Comments
    rules_ordered.append((
        "_comment",
        rule_choice(
            rule_seq(rule_string("//"), rule_pattern(r"[^\n]*")),
            rule_seq(
                rule_string("/*"),
                rule_pattern(r"[^*]*\*+(?:[^/*][^*]*\*+)*"),
                rule_string("/"),
            ),
        )
    ))

    # 3. Global declarations
    rules_ordered.append((
        "global_declaration",
        rule_symbol("variable_declaration")
    ))

    # 4. States
    rules_ordered.append((
        "state_definition",
        rule_seq(
            rule_choice(
                rule_string("default"),
                rule_seq(rule_string("state"), rule_symbol("_identifier")),
            ),
            rule_string("{"),
            rule_repeat(rule_symbol("event_handler")),
            rule_string("}"),
        )
    ))

    # 5. Event handlers
    rules_ordered.append((
        "event_handler",
        rule_seq(
            rule_symbol("_identifier"),
            rule_symbol("parameter_list"),
            rule_symbol("block"),
        )
    ))

    rules_ordered.append((
        "parameter_list",
        rule_seq(
            rule_string("("),
            rule_choice(
                rule_blank(),
                rule_seq(
                    rule_symbol("_parameter"),
                    rule_repeat(rule_seq(rule_string(","), rule_symbol("_parameter"))),
                ),
            ),
            rule_string(")"),
        )
    ))

    rules_ordered.append((
        "_parameter",
        rule_seq(
            rule_symbol("type"),
            rule_symbol("_identifier"),
        )
    ))

    # 6. Blocks and statements
    rules_ordered.append((
        "block",
        rule_seq(
            rule_string("{"),
            rule_repeat(rule_symbol("_statement")),
            rule_string("}"),
        )
    ))

    rules_ordered.append((
        "_statement",
        rule_choice(
            rule_symbol("variable_declaration"),
            rule_symbol("expression_statement"),
            rule_symbol("return_statement"),
            rule_symbol("if_statement"),
            rule_symbol("while_statement"),
            rule_symbol("for_statement"),
        )
    ))

    rules_ordered.append((
        "variable_declaration",
        rule_seq(
            rule_symbol("type"),
            rule_symbol("_identifier"),
            rule_choice(
                rule_seq(rule_string("="), rule_symbol("_expression")),
                rule_blank(),
            ),
            rule_string(";"),
        )
    ))

    rules_ordered.append((
        "expression_statement",
        rule_seq(
            rule_symbol("_expression"),
            rule_string(";"),
        )
    ))

    rules_ordered.append((
        "return_statement",
        rule_seq(
            rule_string("return"),
            rule_choice(
                rule_seq(rule_symbol("_expression"), rule_string(";")),
                rule_string(";"),
            ),
        )
    ))

    rules_ordered.append((
        "if_statement",
        rule_seq(
            rule_string("if"),
            rule_string("("),
            rule_symbol("_expression"),
            rule_string(")"),
            rule_symbol("block"),
            rule_choice(
                rule_seq(rule_string("else"), rule_symbol("block")),
                rule_blank(),
            ),
        )
    ))

    rules_ordered.append((
        "while_statement",
        rule_seq(
            rule_string("while"),
            rule_string("("),
            rule_symbol("_expression"),
            rule_string(")"),
            rule_symbol("block"),
        )
    ))

    rules_ordered.append((
        "for_statement",
        rule_seq(
            rule_string("for"),
            rule_string("("),
            rule_symbol("_identifier"),
            rule_string("="),
            rule_symbol("_expression"),
            rule_string(";"),
            rule_symbol("_expression"),
            rule_string(";"),
            rule_symbol("_expression"),
            rule_string(")"),
            rule_symbol("block"),
        )
    ))

    # ------------------------------------------------------------------
    # 7. EXPRESSIONS — precedence-ordered
    # ------------------------------------------------------------------
    rules_ordered.append((
        "_expression",
        rule_choice(
            rule_symbol("assignment_expression"),
            rule_symbol("binary_expression"),
            rule_symbol("unary_expression"),
            rule_symbol("cast_expression"),
            rule_symbol("call_expression"),
            rule_symbol("parenthesized_expression"),
            rule_symbol("vector_literal"),
            rule_symbol("rotation_literal"),
            rule_symbol("list_literal"),
            rule_symbol("_identifier"),
            rule_symbol("number"),
            rule_symbol("string"),
        )
    ))

    # Assignment (lowest, right-associative) — level 0
    rules_ordered.append((
        "assignment_expression",
        rule_prec_right(
            0,
            rule_seq(
                rule_field("left", rule_symbol("_identifier")),
                rule_choice(
                    rule_string("="),
                    rule_string("+="),
                    rule_string("-="),
                    rule_string("*="),
                    rule_string("/="),
                    rule_string("%="),
                ),
                rule_field("right", rule_symbol("_expression")),
            ),
        )
    ))

    # Binary operators — levels 1 .. 10
    rules_ordered.append((
        "binary_expression",
        rule_choice(
            rule_prec_left(1, rule_seq(
                rule_symbol("_expression"), rule_string("&&"), rule_symbol("_expression"))),
            rule_prec_left(2, rule_seq(
                rule_symbol("_expression"), rule_string("||"), rule_symbol("_expression"))),
            rule_prec_left(3, rule_seq(
                rule_symbol("_expression"), rule_string("|"), rule_symbol("_expression"))),
            rule_prec_left(4, rule_seq(
                rule_symbol("_expression"), rule_string("^"), rule_symbol("_expression"))),
            rule_prec_left(5, rule_seq(
                rule_symbol("_expression"), rule_string("&"), rule_symbol("_expression"))),
            rule_prec_left(6, rule_seq(
                rule_symbol("_expression"), rule_choice(rule_string("=="), rule_string("!=")), rule_symbol("_expression"))),
            rule_prec_left(7, rule_seq(
                rule_symbol("_expression"), rule_choice(rule_string("<"), rule_string("<="), rule_string(">"), rule_string(">=")), rule_symbol("_expression"))),
            rule_prec_left(8, rule_seq(
                rule_symbol("_expression"), rule_choice(rule_string("<<"), rule_string(">>")), rule_symbol("_expression"))),
            rule_prec_left(9, rule_seq(
                rule_symbol("_expression"), rule_string("+"), rule_symbol("_expression"))),
            rule_prec_left(10, rule_seq(
                rule_symbol("_expression"), rule_string("-"), rule_symbol("_expression"))),
            rule_prec_left(11, rule_seq(
                rule_symbol("_expression"), rule_choice(rule_string("*"), rule_string("/"), rule_string("%")), rule_symbol("_expression"))),
        )
    ))

    # Unary operators — level 12
    rules_ordered.append((
        "unary_expression",
        rule_prec(
            12,
            rule_seq(
                rule_choice(
                    rule_string("!"),
                    rule_string("~"),
                    rule_string("-"),
                    rule_string("++"),
                    rule_string("--"),
                ),
                rule_symbol("_expression"),
            ),
        )
    ))

    # Typecast — level 13
    rules_ordered.append((
        "cast_expression",
        rule_prec(
            13,
            rule_seq(
                rule_string("("),
                rule_symbol("type"),
                rule_string(")"),
                rule_symbol("_expression"),
            ),
        )
    ))

    # Parenthesized expression
    rules_ordered.append((
        "parenthesized_expression",
        rule_seq(
            rule_string("("),
            rule_symbol("_expression"),
            rule_string(")"),
        )
    ))

    # Function call
    rules_ordered.append((
        "call_expression",
        rule_seq(
            rule_field("function", rule_symbol("_identifier")),
            rule_field("arguments", rule_symbol("argument_list")),
        )
    ))

    rules_ordered.append((
        "argument_list",
        rule_seq(
            rule_string("("),
            rule_choice(
                rule_blank(),
                rule_seq(
                    rule_symbol("_expression"),
                    rule_repeat(rule_seq(rule_string(","), rule_symbol("_expression"))),
                ),
            ),
            rule_string(")"),
        )
    ))

    # Vector and rotation literals — angle brackets
    rules_ordered.append((
        "vector_literal",
        rule_seq(
            rule_string("<"),
            rule_symbol("_expression"),
            rule_string(","),
            rule_symbol("_expression"),
            rule_string(","),
            rule_symbol("_expression"),
            rule_string(">"),
        )
    ))

    rules_ordered.append((
        "rotation_literal",
        rule_seq(
            rule_string("<"),
            rule_symbol("_expression"),
            rule_string(","),
            rule_symbol("_expression"),
            rule_string(","),
            rule_symbol("_expression"),
            rule_string(","),
            rule_symbol("_expression"),
            rule_string(">"),
        )
    ))

    # List literal — square brackets
    rules_ordered.append((
        "list_literal",
        rule_seq(
            rule_string("["),
            rule_choice(
                rule_blank(),
                rule_seq(
                    rule_symbol("_expression"),
                    rule_repeat(rule_seq(rule_string(","), rule_symbol("_expression"))),
                ),
            ),
            rule_string("]"),
        )
    ))

    # ------------------------------------------------------------------
    # 8. Atoms
    # ------------------------------------------------------------------
    rules_ordered.append((
        "number",
        rule_pattern(r"\d+(\.\d+)?")
    ))

    rules_ordered.append((
        "string",
        rule_seq(
            rule_string('"'),
            rule_pattern(r'[^"]*'),
            rule_string('"'),
        )
    ))

    # ------------------------------------------------------------------
    # 9. Types
    # ------------------------------------------------------------------
    rules_ordered.append((
        "type",
        rule_choice(
            rule_string("integer"),
            rule_string("float"),
            rule_string("string"),
            rule_string("key"),
            rule_string("vector"),
            rule_string("rotation"),
            rule_string("list"),
        )
    ))

    # ------------------------------------------------------------------
    # 10. Identifier token
    # ------------------------------------------------------------------
    rules_ordered.append((
        "_identifier",
        rule_pattern(r"[A-Za-z_][A-Za-z0-9_]*")
    ))

    rules = dict(rules_ordered)

    grammar = {
        "name": "lsl",
        "word": "_identifier",
        "rules": rules,
        "extras": [
            rule_pattern(r"\s"),
            rule_symbol("_comment"),
        ],
        "conflicts": [],
        "externals": [],
        "inline": [],
    }

    return grammar


def main():
    grammar = build_grammar()

    start_rule = next(iter(grammar["rules"]))
    print(f"Start rule (first key in 'rules'): {start_rule!r}")
    if start_rule != "source_file":
        raise SystemExit(
            "ERROR: the first rule is not 'source_file'. "
            "Tree-sitter will reject the grammar."
        )

    out_path = pathlib.Path(__file__).parent / "grammar.json"
    out_path.write_text(json.dumps(grammar, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()