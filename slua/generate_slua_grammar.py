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
    # Start rule
    # ------------------------------------------------------------------
    rules.append((
        "source_file",
        rule_repeat(rule_symbol("_statement"))
    ))

    # ------------------------------------------------------------------
    # Comments
    # ------------------------------------------------------------------
    rules.append((
        "comment",
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
            rule_symbol("const_declaration"),
            rule_symbol("local_function_declaration"),
            rule_symbol("function_declaration"),
            rule_symbol("type_declaration"),
            rule_symbol("export_type_declaration"),
            rule_symbol("type_function_declaration"),
            rule_symbol("declare_statement"),
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

    # ---- Local declarations -----------------------------------------
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

    # SLua `const` declaration
    rules.append((
        "const_declaration",
        rule_seq(
            rule_string("const"),
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

    # binding: name [: type] [<const> | <close>]
    rules.append((
        "_binding",
        rule_seq(
            rule_symbol("identifier"),
            rule_optional(rule_seq(rule_string(":"), rule_symbol("_type"))),
            rule_optional(rule_seq(
                rule_string("<"),
                rule_choice(rule_string("const"), rule_string("close")),
                rule_string(">"),
            )),
        )
    ))

    # ---- Function declarations --------------------------------------
    rules.append((
        "local_function_declaration",
        rule_seq(
            rule_optional(rule_symbol("_attributes")),
            rule_string("local"),
            rule_string("function"),
            rule_symbol("identifier"),
            rule_optional(rule_symbol("_type_params")),
            rule_symbol("function_body"),
        )
    ))

    rules.append((
        "function_declaration",
        rule_seq(
            rule_optional(rule_symbol("_attributes")),
            rule_string("function"),
            rule_symbol("_function_name"),
            rule_optional(rule_symbol("_type_params")),
            rule_symbol("function_body"),
        )
    ))

    rules.append((
        "_function_name",
        rule_seq(
            rule_symbol("identifier"),
            rule_repeat(
                rule_choice(
                    rule_seq(rule_string("."), rule_symbol("identifier")),
                    rule_seq(rule_string(":"), rule_symbol("identifier")),
                )
            ),
        )
    ))

    rules.append((
        "function_body",
        rule_seq(
            rule_string("("),
            rule_optional(rule_symbol("_parameter_list")),
            rule_string(")"),
            rule_optional(rule_seq(rule_string(":"), rule_symbol("_type_function_ret"))),
            rule_optional(rule_symbol("_block")),
            rule_string("end"),
        )
    ))

    rules.append((
        "_parameter_list",
        rule_choice(
            rule_seq(
                rule_symbol("_parameter"),
                rule_repeat(rule_seq(rule_string(","), rule_symbol("_parameter"))),
                rule_optional(rule_seq(
                    rule_string(","), rule_string("..."),
                    rule_optional(rule_seq(rule_string(":"), rule_symbol("_type"))),
                )),
            ),
            rule_seq(
                rule_string("..."),
                rule_optional(rule_seq(rule_string(":"), rule_symbol("_type"))),
            ),
        )
    ))

    rules.append((
        "_parameter",
        rule_seq(
            rule_symbol("identifier"),
            rule_optional(rule_seq(rule_string(":"), rule_symbol("_type"))),
        )
    ))

    # ---- Type declarations ------------------------------------------
    rules.append((
        "type_declaration",
        rule_seq(
            rule_string("type"),
            rule_symbol("identifier"),
            rule_optional(rule_symbol("_type_params")),
            rule_string("="),
            rule_symbol("_type"),
        )
    ))

    rules.append((
        "export_type_declaration",
        rule_seq(
            rule_string("export"),
            rule_string("type"),
            rule_symbol("identifier"),
            rule_optional(rule_symbol("_type_params")),
            rule_string("="),
            rule_symbol("_type"),
        )
    ))

    rules.append((
        "type_function_declaration",
        rule_seq(
            rule_optional(rule_string("export")),
            rule_string("type"),
            rule_string("function"),
            rule_symbol("identifier"),
            rule_symbol("function_body"),
        )
    ))

    rules.append((
        "_type_params",
        rule_seq(
            rule_string("<"),
            rule_symbol("_type_param"),
            rule_repeat(rule_seq(rule_string(","), rule_symbol("_type_param"))),
            rule_string(">"),
        )
    ))

    # Type parameter: NAME ['...'] ['=' Type]
    rules.append((
        "_type_param",
        rule_seq(
            rule_symbol("identifier"),
            rule_optional(rule_string("...")),
            rule_optional(rule_seq(rule_string("="), rule_symbol("_type"))),
        )
    ))

    # ---- Declare statements -----------------------------------------
    rules.append((
        "declare_statement",
        rule_seq(
            rule_optional(rule_symbol("_attributes")),
            rule_string("declare"),
            rule_choice(
                rule_seq(
                    rule_symbol("identifier"),
                    rule_string(":"),
                    rule_symbol("_type"),
                ),
                rule_seq(
                    rule_string("function"),
                    rule_symbol("identifier"),
                    rule_optional(rule_symbol("_type_params")),
                    rule_symbol("function_body_decl"),
                ),
            ),
        )
    ))

    rules.append((
        "function_body_decl",
        rule_seq(
            rule_string("("),
            rule_optional(rule_symbol("_parameter_list")),
            rule_string(")"),
            rule_optional(rule_seq(rule_string(":"), rule_symbol("_type_function_ret"))),
        )
    ))

    # ---- Attributes: only @name -------------------------------------
    rules.append((
        "_attributes",
        rule_repeat1(rule_symbol("_attribute"))
    ))

    rules.append((
        "_attribute",
        rule_seq(rule_string("@"), rule_symbol("identifier"))
    ))

    # ---- Control flow ----------------------------------------------
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
            rule_optional(rule_seq(rule_string("else"), rule_optional(rule_symbol("_block")))),
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
            rule_symbol("identifier"),
            rule_choice(
                rule_seq(
                    rule_string("="),
                    rule_symbol("_expression"),
                    rule_string(","),
                    rule_symbol("_expression"),
                    rule_optional(rule_seq(rule_string(","), rule_symbol("_expression"))),
                ),
                rule_seq(
                    rule_repeat(rule_seq(rule_string(","), rule_symbol("identifier"))),
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
            rule_symbol("_suffixed_expression_list"),
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
        "_suffixed_expression_list",
        rule_seq(
            rule_symbol("_suffixed_expression"),
            rule_repeat(rule_seq(rule_string(","), rule_symbol("_suffixed_expression"))),
        )
    ))

    rules.append((
        "expression_statement",
        rule_symbol("_expression")
    ))

    # ------------------------------------------------------------------
    # Block
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
            rule_symbol("type_assertion"),
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
            rule_repeat(
                rule_seq(
                    rule_string("elseif"),
                    rule_symbol("_expression"),
                    rule_string("then"),
                    rule_symbol("_expression"),
                )
            ),
            rule_string("else"),
            rule_symbol("_expression"),
        )
    ))

    rules.append((
        "type_assertion",
        rule_seq(
            rule_symbol("_suffixed_expression"),
            rule_string("::"),
            rule_symbol("_type"),
        )
    ))

    rules.append((
        "_suffixed_expression",
        rule_choice(
            rule_symbol("identifier"),
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
            rule_seq(rule_string("."), rule_symbol("identifier")),
            rule_seq(rule_string("["), rule_symbol("_expression"), rule_string("]")),
            rule_seq(rule_string(":"), rule_symbol("identifier"), rule_symbol("argument_list")),
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
            rule_optional(rule_symbol("_expression_list")),
            rule_string(")"),
        )
    ))

    rules.append((
        "function_definition",
        rule_seq(
            rule_optional(rule_symbol("_attributes")),
            rule_string("function"),
            rule_optional(rule_symbol("_type_params")),
            rule_symbol("function_body"),
        )
    ))

    rules.append((
        "table_constructor",
        rule_seq(
            rule_string("{"),
            rule_optional(rule_symbol("_field_list")),
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
            rule_seq(rule_symbol("identifier"), rule_string("="), rule_symbol("_expression")),
            rule_symbol("_expression"),
        )
    ))

    # ------------------------------------------------------------------
    # Atoms
    # ------------------------------------------------------------------
    rules.append((
        "number",
        rule_choice(
            rule_pattern(r"0[xX][0-9a-fA-F_]+"),
            rule_pattern(r"0[bB][01_]+"),
            rule_pattern(r"\d[\d_]*(\.[\d_]*)?([eE][+-]?\d+)?"),
            rule_pattern(r"\.\d[\d_]*([eE][+-]?\d+)?"),
        )
    ))

    rules.append((
        "string",
        rule_choice(
            rule_seq(rule_string('"'), rule_pattern(r'[^"\\]*(\\[\s\S][^"\\]*)*'), rule_string('"')),
            rule_seq(rule_string("'"), rule_pattern(r"[^'\\]*(\\[\s\S][^'\\]*)*"), rule_string("'")),
            # Long-bracket string: parser consumes the opening '[', the
            # scanner matches the rest (level-0 `[...]]`, level-1 `=[...]=]`, etc.)
            rule_seq(rule_string("["), rule_symbol("long_string_rest")),
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
    # Types
    # ------------------------------------------------------------------
    rules.append((
        "_type",
        rule_symbol("_type_union")
    ))

    rules.append((
        "_type_union",
        rule_choice(
            rule_symbol("_type_intersection"),
            rule_prec_left(1, rule_seq(
                rule_symbol("_type_union"),
                rule_string("|"),
                rule_symbol("_type_intersection"),
            )),
        )
    ))

    rules.append((
        "_type_intersection",
        rule_choice(
            rule_symbol("_type_optional"),
            rule_prec_left(2, rule_seq(
                rule_symbol("_type_intersection"),
                rule_string("&"),
                rule_symbol("_type_optional"),
            )),
        )
    ))

    rules.append((
        "_type_optional",
        rule_choice(
            rule_symbol("_type_simple"),
            rule_prec(3, rule_seq(
                rule_symbol("_type_simple"),
                rule_string("?"),
            )),
        )
    ))

    rules.append((
        "_type_simple",
        rule_choice(
            rule_symbol("_type_reference"),
            rule_symbol("_type_table"),
            rule_symbol("_type_function"),
            rule_symbol("_type_parenthesized"),
            rule_seq(rule_string("typeof"), rule_string("("), rule_symbol("_expression"), rule_string(")")),
            rule_seq(rule_string("..."), rule_symbol("_type")),
            rule_string("nil"),
            rule_string("true"),
            rule_string("false"),
        )
    ))

    rules.append((
        "_type_reference",
        rule_choice(
            rule_symbol("_type_reference_plain"),
            rule_symbol("_type_reference_generic"),
        )
    ))

    # At `identifier • '...'`, prefer shift: `T...` is the type-pack
    # suffix; `T ...U` (two juxtaposed types) is not valid Luau.
    rules.append((
        "_type_reference_plain",
        rule_prec_right(
            1,
            rule_choice(
                rule_seq(rule_symbol("identifier"), rule_string("...")),
                rule_symbol("identifier"),
            ),
        )
    ))

    rules.append((
        "_type_reference_generic",
        rule_seq(
            rule_symbol("identifier"),
            rule_string("<"),
            rule_symbol("_type_list"),
            rule_string(">"),
        )
    ))

    rules.append((
        "_type_list",
        rule_seq(
            rule_symbol("_type"),
            rule_repeat(rule_seq(rule_string(","), rule_symbol("_type"))),
        )
    ))

    rules.append((
        "_type_parenthesized",
        rule_seq(rule_string("("), rule_symbol("_type"), rule_string(")"))
    ))

    rules.append((
        "_type_table",
        rule_choice(
            rule_seq(rule_string("{"), rule_symbol("_type"), rule_string("}")),
            rule_seq(
                rule_string("{"),
                rule_optional(rule_seq(
                    rule_symbol("_type_table_prop"),
                    rule_repeat(rule_seq(
                        rule_choice(rule_string(","), rule_string(";")),
                        rule_symbol("_type_table_prop"),
                    )),
                    rule_choice(rule_string(","), rule_string(";"), rule_blank()),
                )),
                rule_string("}"),
            ),
        )
    ))

    rules.append((
        "_type_table_prop",
        rule_choice(
            rule_seq(rule_string("["), rule_symbol("_type"), rule_string("]"), rule_string(":"), rule_symbol("_type")),
            rule_seq(rule_symbol("identifier"), rule_string(":"), rule_symbol("_type")),
        )
    ))

    rules.append((
        "_type_function",
        rule_seq(
            rule_symbol("_type_function_params"),
            rule_string("->"),
            rule_symbol("_type_function_ret"),
        )
    ))

    rules.append((
        "_type_function_params",
        rule_seq(
            rule_string("("),
            rule_optional(rule_symbol("_type_list")),
            rule_string(")"),
        )
    ))

    rules.append((
        "_type_function_ret",
        rule_choice(
            rule_symbol("_type"),
            rule_seq(
                rule_string("("),
                rule_optional(rule_symbol("_type_list")),
                rule_string(")"),
            ),
        )
    ))

    # ------------------------------------------------------------------
    # Identifier
    # ------------------------------------------------------------------
    rules.append((
        "identifier",
        rule_pattern(r"[A-Za-z_][A-Za-z0-9_]*")
    ))

    # ------------------------------------------------------------------
    # Assemble
    # ------------------------------------------------------------------
    rules_dict = dict(rules)

    grammar = {
        "name": "slua",
        "word": "identifier",
        "rules": rules_dict,
        "extras": [
            rule_pattern(r"\s"),
            rule_symbol("comment"),
        ],
        "conflicts": [
            ["expression_statement", "if_then_else_expression"],
            ["_type_list", "_type_parenthesized"],
        ],
        "externals": [
            rule_symbol("long_string_rest"),
        ],
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