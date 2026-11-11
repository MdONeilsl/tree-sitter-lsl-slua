# slua/generate_slua_grammar.py
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
    """Inline optional: may match empty, but is not a named rule."""
    return rule_choice(content, rule_blank())


def rule_prec(level, content):
    return {"type": "PREC", "value": level, "content": content}


def rule_prec_left(level, content):
    return {"type": "PREC_LEFT", "value": level, "content": content}


def rule_prec_right(level, content):
    return {"type": "PREC_RIGHT", "value": level, "content": content}


def build_grammar():
    rules = []

    # ------------------------------------------------------------------
    # Start rule (may match empty — it is the start rule)
    # ------------------------------------------------------------------
    rules.append((
        "source_file",
        rule_repeat(rule_symbol("_statement"))
    ))

    # ------------------------------------------------------------------
    # Comments
    # ------------------------------------------------------------------
    rules.append((
        "_comment",
        rule_choice(
            rule_seq(rule_string("--"), rule_pattern(r"[^\n]*")),
            rule_seq(
                rule_string("--[["),
                rule_pattern(r"[\s\S]*?"),
                rule_string("]]"),
            ),
        )
    ))

    # ------------------------------------------------------------------
    # Statements
    # ------------------------------------------------------------------
    rules.append((
        "_statement",
        rule_choice(
            rule_symbol("local_declaration"),
            rule_symbol("local_function_declaration"),
            rule_symbol("function_declaration"),
            rule_symbol("if_statement"),
            rule_symbol("while_statement"),
            rule_symbol("repeat_statement"),
            rule_symbol("for_statement"),
            rule_symbol("do_statement"),
            rule_symbol("return_statement"),
            rule_symbol("break_statement"),
            rule_symbol("continue_statement"),
            rule_symbol("assignment_statement"),
            rule_symbol("expression_statement"),
            rule_string(";"),
        )
    ))

    rules.append((
        "local_declaration",
        rule_seq(
            rule_string("local"),
            rule_symbol("_binding_list"),
            rule_choice(
                rule_seq(rule_string("="), rule_symbol("_expression_list")),
                rule_blank(),
            ),
        )
    ))

    rules.append((
        "_binding_list",
        rule_seq(
            rule_symbol("_binding"),
            rule_repeat(rule_seq(rule_string(","), rule_symbol("_binding"))),
        )
    ))

    rules.append((
        "_binding",
        rule_seq(
            rule_symbol("_identifier"),
            rule_choice(
                rule_seq(rule_string(":"), rule_symbol("_type")),
                rule_blank(),
            ),
        )
    ))

    rules.append((
        "local_function_declaration",
        rule_seq(
            rule_string("local"),
            rule_string("function"),
            rule_symbol("_identifier"),
            rule_symbol("function_body"),
        )
    ))

    rules.append((
        "function_declaration",
        rule_seq(
            rule_string("function"),
            rule_symbol("_function_name"),
            rule_symbol("function_body"),
        )
    ))

    rules.append((
        "_function_name",
        rule_seq(
            rule_symbol("_identifier"),
            rule_repeat(
                rule_choice(
                    rule_seq(rule_string("."), rule_symbol("_identifier")),
                    rule_seq(rule_string(":"), rule_symbol("_identifier")),
                )
            ),
        )
    ))

    rules.append((
        "function_body",
        rule_seq(
            rule_string("("),
            rule_choice(
                rule_blank(),
                rule_symbol("_parameter_list"),
            ),
            rule_string(")"),
            rule_choice(
                rule_seq(rule_string(":"), rule_symbol("_type")),
                rule_blank(),
            ),
            rule_optional(rule_symbol("_block")),
            rule_string("end"),
        )
    ))

    rules.append((
        "_parameter_list",
        rule_seq(
            rule_symbol("_parameter"),
            rule_repeat(rule_seq(rule_string(","), rule_symbol("_parameter"))),
            rule_choice(
                rule_seq(rule_string(","), rule_string("...")),
                rule_blank(),
            ),
        )
    ))

    rules.append((
        "_parameter",
        rule_seq(
            rule_symbol("_identifier"),
            rule_choice(
                rule_seq(rule_string(":"), rule_symbol("_type")),
                rule_blank(),
            ),
        )
    ))

    rules.append((
        "if_statement",
        rule_seq(
            rule_string("if"),
            rule_symbol("_expression"),
            rule_string("then"),
            rule_optional(rule_symbol("_block")),
            rule_repeat(
                rule_seq(
                    rule_string("elseif"),
                    rule_symbol("_expression"),
                    rule_string("then"),
                    rule_optional(rule_symbol("_block")),
                )
            ),
            rule_choice(
                rule_seq(rule_string("else"), rule_optional(rule_symbol("_block"))),
                rule_blank(),
            ),
            rule_string("end"),
        )
    ))

    rules.append((
        "while_statement",
        rule_seq(
            rule_string("while"),
            rule_symbol("_expression"),
            rule_string("do"),
            rule_optional(rule_symbol("_block")),
            rule_string("end"),
        )
    ))

    rules.append((
        "repeat_statement",
        rule_seq(
            rule_string("repeat"),
            rule_optional(rule_symbol("_block")),
            rule_string("until"),
            rule_symbol("_expression"),
        )
    ))

    rules.append((
        "for_statement",
        rule_seq(
            rule_string("for"),
            rule_symbol("_identifier"),
            rule_choice(
                rule_seq(
                    rule_string("="),
                    rule_symbol("_expression"),
                    rule_string(","),
                    rule_symbol("_expression"),
                    rule_choice(
                        rule_seq(rule_string(","), rule_symbol("_expression")),
                        rule_blank(),
                    ),
                ),
                rule_seq(
                    rule_repeat(
                        rule_seq(rule_string(","), rule_symbol("_identifier"))
                    ),
                    rule_string("in"),
                    rule_symbol("_expression_list"),
                ),
            ),
            rule_string("do"),
            rule_optional(rule_symbol("_block")),
            rule_string("end"),
        )
    ))

    rules.append((
        "do_statement",
        rule_seq(
            rule_string("do"),
            rule_optional(rule_symbol("_block")),
            rule_string("end"),
        )
    ))

    rules.append((
        "return_statement",
        rule_prec_right(
            1,
            rule_seq(
                rule_string("return"),
                rule_optional(rule_symbol("_expression_list")),
            ),
        )
    ))

    rules.append((
        "break_statement",
        rule_string("break")
    ))

    rules.append((
        "continue_statement",
        rule_string("continue")
    ))

    rules.append((
        "assignment_statement",
        rule_seq(
            rule_symbol("_suffixed_expression"),
            rule_choice(
                rule_string("="),
                rule_string("+="),
                rule_string("-="),
                rule_string("*="),
                rule_string("/="),
                rule_string("//="),
                rule_string("%="),
                rule_string("^="),
                rule_string("..="),
            ),
            rule_symbol("_expression_list"),
        )
    ))

    rules.append((
        "expression_statement",
        rule_symbol("_expression")
    ))

    # ------------------------------------------------------------------
    # Block (hidden, must NOT match empty: use repeat1)
    # ------------------------------------------------------------------
    rules.append((
        "_block",
        rule_repeat1(rule_symbol("_statement"))
    ))

    # ------------------------------------------------------------------
    # Expressions
    # ------------------------------------------------------------------
    rules.append((
        "_expression",
        rule_choice(
            rule_symbol("binary_expression"),
            rule_symbol("unary_expression"),
            rule_symbol("if_then_else_expression"),
            rule_symbol("_suffixed_expression"),
            rule_symbol("function_definition"),
            rule_symbol("table_constructor"),
            rule_symbol("number"),
            rule_symbol("string"),
            rule_symbol("interpolated_string"),
            rule_string("nil"),
            rule_string("true"),
            rule_string("false"),
            rule_string("..."),
        )
    ))

    rules.append((
        "_expression_list",
        rule_seq(
            rule_symbol("_expression"),
            rule_repeat(rule_seq(rule_string(","), rule_symbol("_expression"))),
        )
    ))

    rules.append((
        "binary_expression",
        rule_choice(
            rule_prec_left(1, rule_seq(
                rule_symbol("_expression"), rule_string("or"), rule_symbol("_expression"))),
            rule_prec_left(2, rule_seq(
                rule_symbol("_expression"), rule_string("and"), rule_symbol("_expression"))),
            rule_prec_left(3, rule_seq(
                rule_symbol("_expression"),
                rule_choice(
                    rule_string("<"), rule_string(">"),
                    rule_string("<="), rule_string(">="),
                    rule_string("~="), rule_string("=="),
                ),
                rule_symbol("_expression"))),
            rule_prec_right(4, rule_seq(
                rule_symbol("_expression"), rule_string(".."), rule_symbol("_expression"))),
            rule_prec_left(5, rule_seq(
                rule_symbol("_expression"),
                rule_choice(rule_string("+"), rule_string("-")),
                rule_symbol("_expression"))),
            rule_prec_left(6, rule_seq(
                rule_symbol("_expression"),
                rule_choice(
                    rule_string("*"), rule_string("/"),
                    rule_string("//"), rule_string("%"),
                ),
                rule_symbol("_expression"))),
        )
    ))

    rules.append((
        "unary_expression",
        rule_prec(
            7,
            rule_seq(
                rule_choice(rule_string("not"), rule_string("#"), rule_string("-")),
                rule_symbol("_expression"),
            ),
        )
    ))

    rules.append((
        "if_then_else_expression",
        rule_seq(
            rule_string("if"),
            rule_symbol("_expression"),
            rule_string("then"),
            rule_symbol("_expression"),
            rule_string("else"),
            rule_symbol("_expression"),
        )
    ))

    rules.append((
        "_suffixed_expression",
        rule_choice(
            rule_symbol("_identifier"),
            rule_symbol("parenthesized_expression"),
            rule_prec_left(1, rule_seq(
                rule_symbol("_suffixed_expression"),
                rule_symbol("_suffix"),
            )),
        )
    ))

    rules.append((
        "_suffix",
        rule_choice(
            rule_seq(rule_string("."), rule_symbol("_identifier")),
            rule_seq(rule_string("["), rule_symbol("_expression"), rule_string("]")),
            rule_seq(rule_string(":"), rule_symbol("_identifier"), rule_symbol("argument_list")),
            rule_symbol("argument_list"),
        )
    ))

    rules.append((
        "parenthesized_expression",
        rule_seq(rule_string("("), rule_symbol("_expression"), rule_string(")"))
    ))

    rules.append((
        "argument_list",
        rule_seq(
            rule_string("("),
            rule_choice(
                rule_blank(),
                rule_symbol("_expression_list"),
            ),
            rule_string(")"),
        )
    ))

    rules.append((
        "function_definition",
        rule_seq(rule_string("function"), rule_symbol("function_body"))
    ))

    rules.append((
        "table_constructor",
        rule_seq(
            rule_string("{"),
            rule_choice(
                rule_blank(),
                rule_symbol("_field_list"),
            ),
            rule_string("}"),
        )
    ))

    rules.append((
        "_field_list",
        rule_seq(
            rule_symbol("_field"),
            rule_repeat(rule_seq(rule_choice(rule_string(","), rule_string(";")), rule_symbol("_field"))),
            rule_choice(rule_string(","), rule_string(";"), rule_blank()),
        )
    ))

    rules.append((
        "_field",
        rule_choice(
            rule_seq(rule_string("["), rule_symbol("_expression"), rule_string("]"), rule_string("="), rule_symbol("_expression")),
            rule_seq(rule_symbol("_identifier"), rule_string("="), rule_symbol("_expression")),
            rule_symbol("_expression"),
        )
    ))

    # ------------------------------------------------------------------
    # Atoms
    # ------------------------------------------------------------------
    rules.append((
        "number",
        rule_choice(
            rule_pattern(r"0[xX][0-9a-fA-F]+"),
            rule_pattern(r"\d+(\.\d+)?([eE][+-]?\d+)?"),
            rule_pattern(r"\.\d+([eE][+-]?\d+)?"),
        )
    ))

    rules.append((
        "string",
        rule_choice(
            rule_seq(rule_string('"'), rule_pattern(r'[^"\\]*(\\[\s\S][^"\\]*)*'), rule_string('"')),
            rule_seq(rule_string("'"), rule_pattern(r"[^'\\]*(\\[\s\S][^'\\]*)*"), rule_string("'")),
            rule_seq(rule_string("[["), rule_pattern(r"[\s\S]*?"), rule_string("]]")),
        )
    ))

    rules.append((
        "interpolated_string",
        rule_seq(
            rule_string("`"),
            rule_repeat(
                rule_choice(
                    rule_symbol("_interpolation"),
                    rule_pattern(r"[^`{]+"),
                )
            ),
            rule_string("`"),
        )
    ))

    rules.append((
        "_interpolation",
        rule_seq(rule_string("{"), rule_symbol("_expression"), rule_string("}"))
    ))

    # ------------------------------------------------------------------
    # Minimal Luau types
    # ------------------------------------------------------------------
    rules.append((
        "_type",
        rule_choice(
            rule_symbol("_identifier"),
            rule_string("nil"),
            rule_seq(rule_string("typeof"), rule_string("("), rule_symbol("_expression"), rule_string(")")),
            rule_seq(rule_string("("), rule_symbol("_type"), rule_string(")")),
            rule_seq(
                rule_string("{"),
                rule_repeat(
                    rule_seq(rule_symbol("_identifier"), rule_string(":"), rule_symbol("_type"), rule_string(","))
                ),
                rule_string("}"),
            ),
            rule_seq(rule_string("("), rule_choice(rule_blank(), rule_symbol("_type")), rule_string(")"), rule_string("->"), rule_symbol("_type")),
        )
    ))

    # ------------------------------------------------------------------
    # Identifier
    # ------------------------------------------------------------------
    rules.append((
        "_identifier",
        rule_pattern(r"[A-Za-z_][A-Za-z0-9_]*")
    ))

    # ------------------------------------------------------------------
    # Assemble
    #
    # `conflicts` is a list of lists of RULE NAME STRINGS — not symbol
    # objects. The JSON schema for a Tree-sitter grammar specifies
    # `conflicts: Vec<Vec<String>>` and `inline: Vec<String>`.
    # ------------------------------------------------------------------
    rules_dict = dict(rules)

    grammar = {
        "name": "slua",
        "word": "_identifier",
        "rules": rules_dict,
        "extras": [
            rule_pattern(r"\s"),
            rule_symbol("_comment"),
        ],
        "conflicts": [
            ["expression_statement", "if_then_else_expression"],
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