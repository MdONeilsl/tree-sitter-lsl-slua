/* slua/src/scanner.c
 *
 * External scanner for the SLua grammar.
 *
 * Three external tokens:
 *   - LONG_STRING_REST: the body of a long-bracket string or comment, from
 *     `[=*[` through `]=*]`, with matching `=` count on both sides.
 *   - TYPE_LT, TYPE_GT: the `<` and `>` that delimit a generic type argument
 *     list. Separate tokens so the parser can distinguish `Array<T>` from a
 *     comparison `a < b`; the grammar enables TYPE_LT/TYPE_GT only in type
 *     contexts.
 *
 * The scanner is stateless. `valid_symbols` carries all the information the
 * parser needs to communicate; one `>` is consumed per scan call, so `>>` in
 * `Array<Array<T>>` naturally produces two TYPE_GT tokens via two scanner
 * invocations — no queue, no zero-width tokens.
 */
#include <stdlib.h>
#include "tree_sitter/parser.h"

enum TokenType {
    LONG_STRING_REST,
    TYPE_LT,
    TYPE_GT,
};

static void skip(TSLexer *lexer) {
    lexer->advance(lexer, false);
}

static bool scan_long_string_rest(TSLexer *lexer) {
    int level = 0;
    while (lexer->lookahead == '=') {
        level++;
        skip(lexer);
    }

    if (lexer->lookahead != '[') return false;
    skip(lexer);

    for (;;) {
        if (lexer->eof(lexer)) return false;

        if (lexer->lookahead == ']') {
            skip(lexer);

            int close_level = 0;
            while (close_level < level && lexer->lookahead == '=') {
                close_level++;
                skip(lexer);
            }

            if (close_level == level && lexer->lookahead == ']') {
                skip(lexer);
                return true;
            }
        } else {
            skip(lexer);
        }
    }
}

bool tree_sitter_slua_external_scanner_scan(
    void *payload,
    TSLexer *lexer,
    const bool *valid_symbols
) {
    (void)payload;

    if (valid_symbols[LONG_STRING_REST]
        && (lexer->lookahead == '[' || lexer->lookahead == '=')) {
        if (scan_long_string_rest(lexer)) {
            lexer->result_symbol = LONG_STRING_REST;
            return true;
        }
    }

    if (valid_symbols[TYPE_LT] && lexer->lookahead == '<') {
        skip(lexer);
        lexer->result_symbol = TYPE_LT;
        return true;
    }

    if (valid_symbols[TYPE_GT] && lexer->lookahead == '>') {
        skip(lexer);
        lexer->result_symbol = TYPE_GT;
        return true;
    }

    return false;
}

void *tree_sitter_slua_external_scanner_create(void) { return NULL; }
void tree_sitter_slua_external_scanner_destroy(void *payload) { (void)payload; }

unsigned tree_sitter_slua_external_scanner_serialize(void *payload, char *buffer) {
    (void)payload;
    (void)buffer;
    return 0;
}

void tree_sitter_slua_external_scanner_deserialize(
    void *payload, const char *buffer, unsigned length)
{
    (void)payload;
    (void)buffer;
    (void)length;
}