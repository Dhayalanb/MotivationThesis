#!/bin/sh
set -eux
echo core | sudo tee /proc/sys/kernel/core_pattern

#Update env
BIN_PATH=$(readlink -f "$0")
ROOT_DIR=$(dirname $(dirname $BIN_PATH))
export PATH=${HOME}/clang+llvm/bin:$PATH
export LD_LIBRARY_PATH=${HOME}/clang+llvm/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}
export CC=clang
export CXX=clang++
PREFIX=${PREFIX:-${ROOT_DIR}/bin/}


echo "Compiling and running for angora"
./run_angora.sh $1
echo "Compiling for test framework"
./compile_for_framework.sh $1
echo "Preprocessing angora output"
./preprocess_angora_results.sh $1
echo "Running test framework"
./process_angora_results.sh $1
echo "Creating output"
./postprocess_angora_results.sh $1
echo "Done"
echo "The results can be found in output/raw_data.csv"
