#!/bin/sh
set -eux

BUILD_TYPE="debug"
# BUILD_TYPE="release"
num_jobs=1
#sync_afl="--sync_afl"
sync_afl=""
LOG_TYPE=angora
MODE="llvm"
#LOG_TYPE=info

if [ ! -z ${RELEASE+x} ]; then
    BUILD_TYPE="release"
fi

if [ ! -z ${LLVM_MODE+x} ]; then
    MODE="llvm"
fi
if [ ! -z ${PIN_MODE+x} ]; then
    MODE="pin"
fi


envs="BUILD_TYPE=${BUILD_TYPE} LOG_TYPE=${LOG_TYPE}"

if [ "$#" -ne 1 ] || ! [ -d "$1" ]; then
    echo "Usage: $0 DIRECTORY" >&2
    exit 1
fi

rm -rf " ./output"
name=$1

echo "Compile..."

target=${name}/${name}

rm -f ${target}.fast
rm -f ${target}.static
rm -f ${target}.sym
mkdir -p "./output/static"
# export ANGORA_CUSTOM_FN_CONTEXT=0

bin_dir=../bin/
USE_FAST=1 ${bin_dir}/angora-clang ${target}.c -lz -o ${target}.test
ANGORA_OUTPUT_STATIC_ANALYSIS_LOC=./output/static/ USE_FAST=1 ${bin_dir}/static-analysis-clang ${target}.c -lz -o ${target}.static
rm -f ${target}.static
# USE_PIN=1 ${bin_dir}/angora-clang ${target}.c -lz -o ${target}.pin
#LLVM_COMPILER=clang wllvm -O0 -g ${target}.c -lz -o ${target}
#extract-bc ${target}
#opt -load ../bin/unfold-branch-pass.so -unfold_branch_pass < ${target}.bc > ${target}2.bc
#opt -load ../bin/angora-llvm-pass.so -angora_llvm_pass < ${target}2.bc > ${target}3.bc
#opt -load ../bin/angora-llvm-pass.so -angora_llvm_pass -TrackMode < ${target}2.bc > ${target}4.bc
#USE_FAST=1 ${bin_dir}/angora-clang ${target}.bc -lz -o ${target}.fast
#USE_TRACK=1 ${bin_dir}/angora-clang ${target}.bc -lz -o ${target}.taint
echo "Compile Done.."

echo "Compiling symblic version"

${bin_dir}/symcc ${target}.c -o ${target}.sym

echo "Symbolic version compiled"
