cmake_minimum_required(VERSION 3.16)
project(tree-sitter-consumer LANGUAGES C)

# Bring in the packaged grammars via add_subdirectory.
add_subdirectory("${CMAKE_CURRENT_SOURCE_DIR}/../../dist"
                 "${CMAKE_CURRENT_BINARY_DIR}/tree-sitter-lsl-lsua")

add_executable(consumer main.c)
target_link_libraries(consumer PRIVATE
    tree-sitter::lsl
    tree-sitter::slua
)

# Optional: if the runtime is available, link it as well so that future
# test executables can use ts_parser_new() and friends.
if(TARGET tree-sitter::tree-sitter)
    target_link_libraries(consumer PRIVATE tree-sitter::tree-sitter)
endif()
