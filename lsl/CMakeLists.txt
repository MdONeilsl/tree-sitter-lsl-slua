cmake_minimum_required(VERSION 3.16)

# This file exists so that a consumer who only wants LSL can do:
#     add_subdirectory(third_party/tree-sitter-lsl-slua/lsl)
# without pulling in SLua.

add_library(tree-sitter-lsl STATIC src/parser.c)
add_library(tree-sitter::lsl ALIAS tree-sitter-lsl)

target_include_directories(tree-sitter-lsl PUBLIC include)

if(TARGET tree-sitter::tree-sitter)
    target_link_libraries(tree-sitter-lsl PUBLIC tree-sitter::tree-sitter)
endif()