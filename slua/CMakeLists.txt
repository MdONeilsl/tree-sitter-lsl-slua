cmake_minimum_required(VERSION 3.16)

# This file exists so that a consumer who only wants SLua can do:
#     add_subdirectory(third_party/tree-sitter-lsl-slua/slua)
# without pulling in LSL.

add_library(tree-sitter-slua STATIC
    src/parser.c
    src/scanner.c
)
add_library(tree-sitter::slua ALIAS tree-sitter-slua)

target_include_directories(tree-sitter-slua PUBLIC include)

if(TARGET tree-sitter::tree-sitter)
    target_link_libraries(tree-sitter-slua PUBLIC tree-sitter::tree-sitter)
endif()