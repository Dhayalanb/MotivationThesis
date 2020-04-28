#!/bin/bash
BIN_PATH=$(readlink -f "$0")
ROOT_DIR=$(dirname $(dirname $BIN_PATH))
export PATH=${HOME}/clang+llvm/bin:$PATH
export LD_LIBRARY_PATH=${HOME}/clang+llvm/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}
export CC=clang
export CXX=clang++
PREFIX=${PREFIX:-${ROOT_DIR}/bin/}

cd compiler
rm -rf build
mkdir -p build
cd build
cmake -DCMAKE_INSTALL_PREFIX=${PREFIX} -DCMAKE_BUILD_TYPE=Release ..
make # VERBOSE=1 
make install # VERBOSE=1