cmake_minimum_required(VERSION 3.16)

# ---------------------------------------------------------------------------
# Only call project() when this is the top-level build.
# FetchContent_MakeAvailable() and add_subdirectory() set CMAKE_SOURCE_DIR
# to the parent, so this block is skipped in those modes.
# ---------------------------------------------------------------------------
if(CMAKE_SOURCE_DIR STREQUAL CMAKE_CURRENT_SOURCE_DIR)
    project(tree-sitter-lsl-lsua VERSION 0.1.0 LANGUAGES C)
endif()

# ---------------------------------------------------------------------------
# Options
# ---------------------------------------------------------------------------
option(TS_LSL_LSUA_BUILD_LSL  "Build the LSL parser target"  ON)
option(TS_LSL_LSUA_BUILD_SLUA "Build the SLua parser target" ON)

# ---------------------------------------------------------------------------
# Tree-sitter runtime
#
# The runtime is a separate project (github.com/tree-sitter/tree-sitter).
# Consumers provide it via:
#   - vcpkg / Conan / apt / brew
#   - the tree-sitter_ROOT environment variable
#   - -Dtree-sitter_DIR=<prefix>/lib/cmake/tree-sitter
#   - a CMakePresets.json cacheVariables entry
#
# If it is not found, the grammar targets are still defined. Consumers
# link the runtime themselves. No auto-fetch, no hidden dependency.
# ---------------------------------------------------------------------------
find_package(tree-sitter QUIET)

if(NOT tree-sitter_FOUND)
    message(WARNING
        "tree-sitter runtime not found. "
        "tree-sitter::lsl / tree-sitter::slua will be built without it; "
        "consumers must link the runtime themselves. "
        "Install it via vcpkg, Conan, apt, brew, or from source, "
        "or set tree-sitter_ROOT / -Dtree-sitter_DIR.")
endif()

# ---------------------------------------------------------------------------
# Grammar target factory
# ---------------------------------------------------------------------------
function(ts_define_grammar name)
    set(target tree-sitter-${name})

    add_library(${target} STATIC "${CMAKE_CURRENT_SOURCE_DIR}/${name}/src/parser.c")

    if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/${name}/src/scanner.c")
        target_sources(${target} PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/${name}/src/scanner.c")
    endif()

    add_library(tree-sitter::${name} ALIAS ${target})

    target_include_directories(${target} PUBLIC
        "$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/${name}/include>"
        "$<INSTALL_INTERFACE:include/${name}>"
    )

    if(tree-sitter_FOUND)
        target_link_libraries(${target} PUBLIC tree-sitter::tree-sitter)
    endif()
endfunction()

# ---------------------------------------------------------------------------
# Define targets
# ---------------------------------------------------------------------------
if(TS_LSL_LSUA_BUILD_LSL)
    ts_define_grammar(lsl)
endif()

if(TS_LSL_LSUA_BUILD_SLUA)
    ts_define_grammar(slua)
endif()
