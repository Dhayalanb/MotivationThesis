cmake_minimum_required(VERSION 3.4)

project(angora_llvm_mode VERSION 1.2.2 LANGUAGES C CXX ASM)

include_directories(include)

set(ANGORA_BIN_DIR ".")
set(ANGORA_LIB_DIR "lib")
set(ANGORA_PASS_DIR "pass")

add_subdirectory(compiler)
add_subdirectory(pass)
add_subdirectory(libcxx)
