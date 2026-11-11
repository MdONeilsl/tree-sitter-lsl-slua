/* lsl/include/lsl.h
 *
 * Public API for the LSL grammar produced by tree-sitter-lsl-lsua.
 *
 * Consumers link one of:
 *   - the static library produced by CMake from src/parser.c, or
 *   - the pre-built shared library lsl.dll / lsl.so / lsl.dylib
 * and call tree_sitter_lsl() to obtain the language, which they then hand
 * to the tree-sitter runtime via ts_parser_set_language().
 */
#ifndef TREE_SITTER_LSL_H_
#define TREE_SITTER_LSL_H_

#ifdef __cplusplus
extern "C" {
#endif

/* Opaque type, defined by the tree-sitter runtime (tree_sitter/api.h).
 * Declaring it here keeps this header self-contained. */
typedef struct TSLanguage TSLanguage;

/* Returns the LSL language definition.
 *
 * The returned pointer is owned by the library, remains valid for the
 * lifetime of the process, and must not be freed. Calling this function
 * multiple times returns the same pointer. */
const TSLanguage *tree_sitter_lsl(void);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* TREE_SITTER_LSL_H_ */
