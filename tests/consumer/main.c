/* tests/consumer/main.c
 *
 * Proves the packaged grammar libraries are usable at compile time
 * WITHOUT the tree-sitter runtime.  It calls the two exported symbols
 * and confirms they return non-NULL.
 *
 * This is the smoke test.  To exercise actual parsing, a second test
 * executable that links the runtime is required (see tests/consumer/
 * parse_main.c if you add one).
 */

#include <stdio.h>

/* Public headers shipped in the package.
 * Both declare `typedef struct TSLanguage TSLanguage;` — that
 * redeclaration is legal in C11 and MSVC accepts it, but we use the
 * struct tag directly below anyway to keep the file maximally portable. */
#include "lsl.h"
#include "slua.h"

int main(void)
{
    const struct TSLanguage *lsl  = tree_sitter_lsl();
    const struct TSLanguage *slua = tree_sitter_slua();

    printf("tree_sitter_lsl()  = %p\n", (const void *)lsl);
    printf("tree_sitter_slua() = %p\n", (const void *)slua);

    return (lsl != NULL && slua != NULL) ? 0 : 1;
}
