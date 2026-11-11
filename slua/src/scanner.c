/* slua/src/scanner.c
 *
 * External scanner for the SLua grammar.
 *
 * The grammar consumes the first '[' of a long-bracket string as an
 * anonymous token (see the `string` rule). The scanner is therefore
 * positioned just after that first '['. Its job is to consume the rest
 * of the long-bracket string — `[ ... ]]` for level 0, `=[ ... ]=]` for
 * level 1, and so on — matching the number of '=' characters between
 * the opener and the closer.
 */
#include "tree_sitter/parser.h"

enum TokenType {
    LONG_STRING_REST,
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

    if (!valid_symbols[LONG_STRING_REST]) return false;

    if (lexer->lookahead == '[' || lexer->lookahead == '=') {
        if (scan_long_string_rest(lexer)) {
            lexer->result_symbol = LONG_STRING_REST;
            return true;
        }
    }
    return false;
}

void *tree_sitter_slua_external_scanner_create(void) { return NULL; }
void tree_sitter_slua_external_scanner_destroy(void *payload) { (void)payload; }
unsigned tree_sitter_slua_external_scanner_serialize(void *payload, char *buffer) {
    (void)payload; (void)buffer; return 0;
}
void tree_sitter_slua_external_scanner_deserialize(void *payload, const char *buffer, unsigned length) {
    (void)payload; (void)buffer; (void)length;
}
