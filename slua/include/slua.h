/* slua/include/slua.h
 *
 * Public API for the SLua grammar produced by tree-sitter-lsl-lsua.
 */
#ifndef TREE_SITTER_SLUA_H_
#define TREE_SITTER_SLUA_H_

#ifdef __cplusplus
extern "C" {
#endif

typedef struct TSLanguage TSLanguage;

/* Returns the SLua language definition.
 *
 * The returned pointer is owned by the library, remains valid for the
 * lifetime of the process, and must not be freed. */
const TSLanguage *tree_sitter_slua(void);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* TREE_SITTER_SLUA_H_ */