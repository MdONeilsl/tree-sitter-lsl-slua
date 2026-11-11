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


def rule_optional(content):
    return rule_choice(content, rule_blank())


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

    # 1. Start rule — MUST be first in `rules`.
    rules_ordered.append((
        "source_file",
        rule_repeat(
            rule_choice(
                rule_symbol("global_declaration"),
                rule_symbol("state_definition"),
                rule_symbol("preproc_directive"),
            )
        )
    ))

    # 2. Comments
    rules_ordered.append((
        "comment",
        rule_choice(
            rule_seq(rule_string("//"), rule_pattern(r"[^\n]*")),
            rule_seq(
                rule_string("/*"),
                rule_pattern(r"[^*]*\*+(?:[^/*][^*]*\*+)*"),
                rule_string("/"),
            ),
        )
    ))

    # 3. Preprocessor directives — a proper node (NOT an extra), so they
    #    appear in the tree and can be styled by highlighters.
    rules_ordered.append((
        "preproc_directive",
        rule_seq(
            rule_string("#"),
            rule_choice(
                rule_string("include"),
                rule_string("define"),
                rule_string("undef"),
                rule_string("ifdef"),
                rule_string("ifndef"),
                rule_string("if"),
                rule_string("elif"),
                rule_string("else"),
                rule_string("endif"),
                rule_string("warning"),
                rule_string("error"),
            ),
            rule_pattern(r"[^\n]*"),
        )
    ))

    # 4. Global declarations
    rules_ordered.append((
        "global_declaration",
        rule_symbol("variable_declaration")
    ))

    # 5. States
    rules_ordered.append((
        "state_definition",
        rule_seq(
            rule_choice(
                rule_string("default"),
                rule_seq(rule_string("state"), rule_symbol("identifier")),
            ),
            rule_string("{"),
            rule_repeat(rule_choice(
                rule_symbol("event_handler"),
                rule_symbol("preproc_directive"),
            )),
            rule_string("}"),
        )
    ))

    # 6. Event handlers
    rules_ordered.append((
        "event_handler",
        rule_seq(
            rule_symbol("identifier"),
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
            rule_symbol("identifier"),
        )
    ))

    # 7. Blocks and statements
    rules_ordered.append((
        "block",
        rule_seq(
            rule_string("{"),
            rule_repeat(rule_symbol("_statement")),
            rule_string("}"),
        )
    ))

    rules_ordered.append((
        "_body",
        rule_choice(
            rule_symbol("block"),
            rule_symbol("_statement"),
        )
    ))

    rules_ordered.append((
        "_statement",
        rule_choice(
            rule_symbol("variable_declaration"),
            rule_symbol("expression_statement"),
            rule_symbol("return_statement"),
            rule_symbol("if_statement"),
            rule_symbol("switch_statement"),
            rule_symbol("while_statement"),
            rule_symbol("do_while_statement"),
            rule_symbol("for_statement"),
            rule_symbol("state_transition"),
            rule_symbol("jump_statement"),
            rule_symbol("label_statement"),
            rule_symbol("lazy_list_assignment"),
            rule_symbol("break_statement"),
            rule_symbol("preproc_directive"),
            rule_string(";"),
        )
    ))

    rules_ordered.append((
        "variable_declaration",
        rule_seq(
            rule_symbol("type"),
            rule_symbol("identifier"),
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
        rule_prec_right(
            1,
            rule_seq(
                rule_string("if"),
                rule_string("("),
                rule_symbol("_expression"),
                rule_string(")"),
                rule_symbol("_body"),
                rule_choice(
                    rule_seq(rule_string("else"), rule_symbol("_body")),
                    rule_blank(),
                ),
            ),
        )
    ))

    # switch (expr) { case ... default ... }
    rules_ordered.append((
        "switch_statement",
        rule_seq(
            rule_string("switch"),
            rule_string("("),
            rule_symbol("_expression"),
            rule_string(")"),
            rule_string("{"),
            rule_repeat(rule_symbol("_switch_clause")),
            rule_string("}"),
        )
    ))

    rules_ordered.append((
        "_switch_clause",
        rule_choice(
            rule_symbol("case_clause"),
            rule_symbol("default_clause"),
        )
    ))

    # case expr : body  — body is zero or more statements/blocks, ending
    # naturally when the next token is `case`, `default`, or `}`.
    rules_ordered.append((
        "case_clause",
        rule_seq(
            rule_string("case"),
            rule_symbol("_expression"),
            rule_string(":"),
            rule_repeat(rule_symbol("_body")),
        )
    ))

    rules_ordered.append((
        "default_clause",
        rule_seq(
            rule_string("default"),
            rule_string(":"),
            rule_repeat(rule_symbol("_body")),
        )
    ))

    rules_ordered.append((
        "break_statement",
        rule_seq(rule_string("break"), rule_string(";"))
    ))

    rules_ordered.append((
        "while_statement",
        rule_seq(
            rule_string("while"),
            rule_string("("),
            rule_symbol("_expression"),
            rule_string(")"),
            rule_symbol("_body"),
        )
    ))

    rules_ordered.append((
        "do_while_statement",
        rule_seq(
            rule_string("do"),
            rule_symbol("_body"),
            rule_string("while"),
            rule_string("("),
            rule_symbol("_expression"),
            rule_string(")"),
            rule_string(";"),
        )
    ))

    rules_ordered.append((
        "for_statement",
        rule_seq(
            rule_string("for"),
            rule_string("("),
            rule_symbol("identifier"),
            rule_string("="),
            rule_symbol("_expression"),
            rule_string(";"),
            rule_symbol("_expression"),
            rule_string(";"),
            rule_symbol("_expression"),
            rule_string(")"),
            rule_symbol("_body"),
        )
    ))

    rules_ordered.append((
        "state_transition",
        rule_seq(
            rule_string("state"),
            rule_symbol("identifier"),
            rule_string(";"),
        )
    ))

    rules_ordered.append((
        "jump_statement",
        rule_seq(
            rule_string("jump"),
            rule_symbol("identifier"),
            rule_string(";"),
        )
    ))

    rules_ordered.append((
        "label_statement",
        rule_seq(
            rule_string("@"),
            rule_symbol("identifier"),
            rule_string(";"),
        )
    ))

    # Lazy list assignment: identifier[index] = value;
    rules_ordered.append((
        "lazy_list_assignment",
        rule_seq(
            rule_symbol("identifier"),
            rule_string("["),
            rule_symbol("_expression"),
            rule_string("]"),
            rule_string("="),
            rule_symbol("_expression"),
            rule_string(";"),
        )
    ))

    # 8. Expressions
    rules_ordered.append((
        "_expression",
        rule_choice(
            rule_symbol("assignment_expression"),
            rule_symbol("binary_expression"),
            rule_symbol("unary_expression"),
            rule_symbol("postfix_expression"),
            rule_symbol("cast_expression"),
            rule_symbol("call_expression"),
            rule_symbol("index_expression"),
            rule_symbol("parenthesized_expression"),
            rule_symbol("vector_literal"),
            rule_symbol("rotation_literal"),
            rule_symbol("list_literal"),
            rule_symbol("identifier"),
            rule_symbol("number"),
            rule_symbol("string"),
        )
    ))

    rules_ordered.append((
        "assignment_expression",
        rule_prec_right(
            0,
            rule_seq(
                rule_field("left", rule_symbol("identifier")),
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
                rule_symbol("_expression"),
                rule_choice(rule_string("=="), rule_string("!=")),
                rule_symbol("_expression"))),
            rule_prec_left(7, rule_seq(
                rule_symbol("_expression"),
                rule_choice(rule_string("<"), rule_string("<="), rule_string(">"), rule_string(">=")),
                rule_symbol("_expression"))),
            rule_prec_left(8, rule_seq(
                rule_symbol("_expression"),
                rule_choice(rule_string("<<"), rule_string(">>")),
                rule_symbol("_expression"))),
            rule_prec_left(9, rule_seq(
                rule_symbol("_expression"), rule_string("+"), rule_symbol("_expression"))),
            rule_prec_left(10, rule_seq(
                rule_symbol("_expression"), rule_string("-"), rule_symbol("_expression"))),
            rule_prec_left(11, rule_seq(
                rule_symbol("_expression"),
                rule_choice(rule_string("*"), rule_string("/"), rule_string("%")),
                rule_symbol("_expression"))),
        )
    ))

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

    rules_ordered.append((
        "postfix_expression",
        rule_prec_left(
            15,
            rule_seq(
                rule_symbol("_expression"),
                rule_choice(rule_string("++"), rule_string("--")),
            ),
        )
    ))

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

    rules_ordered.append((
        "parenthesized_expression",
        rule_seq(
            rule_string("("),
            rule_symbol("_expression"),
            rule_string(")"),
        )
    ))

    rules_ordered.append((
        "call_expression",
        rule_seq(
            rule_field("function", rule_symbol("identifier")),
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

    rules_ordered.append((
        "index_expression",
        rule_prec(
            14,
            rule_seq(
                rule_symbol("_expression"),
                rule_string("["),
                rule_symbol("_expression"),
                rule_string("]"),
            ),
        )
    ))

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

    # 9. Atoms
    rules_ordered.append((
        "number",
        rule_pattern(r"\d+(\.\d+)?")
    ))

    rules_ordered.append((
        "string",
        rule_seq(
            rule_string('"'),
            rule_pattern(r'([^"\\]|\\.)*'),
            rule_string('"'),
        )
    ))

    # 10. Types
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

    # 11. Identifier token — visible
    rules_ordered.append((
        "identifier",
        rule_pattern(r"[A-Za-z_][A-Za-z0-9_]*")
    ))

    rules = dict(rules_ordered)

    grammar = {
        "name": "lsl",
        "word": "identifier",
        "rules": rules,
        "extras": [
            rule_pattern(r"\s"),
            rule_symbol("comment"),
        ],
        "conflicts": [
            ["lazy_list_assignment", "_expression"],
        ],
        "externals": [],
        "inline": [],
    }

    return grammar


def main():
    grammar = build_grammar()

    start_rule = next(iter(grammar["rules"]))
    print(f"Start rule (first key in 'rules'): {start_rule!r}")
    if start_rule != "source_file":
        raise SystemExit("ERROR: first rule is not 'source_file'")

    out_path = pathlib.Path(__file__).parent / "grammar.json"
    out_path.write_text(json.dumps(grammar, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
    