#!/bin/sh
set -eux



BUILD_TYPE="debug"
# BUILD_TYPE="release"
num_jobs=1
#sync_afl="--sync_afl"
sync_afl=""
LOG_TYPE=angora
MODE="pin"
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


# envs="BUILD_TYPE=${BUILD_TYPE} LOG_TYPE=${LOG_TYPE}"
envs=""
fuzzer="../angora_fuzzer"
input="./input"
output="./output"

if [ "$#" -ne 3 ] || ! [ -d "$1" ]; then
    echo "Usage: $0 DIRECTORY TIMEOUT DEPTH" >&2
    exit 1
fi

rm -rf $output
name=$1
timeout=$2
depth=$3 

echo "Compile..."

target=${name}/${name}

rm -f ${target}.fast ${target}.static ${target}.taint ${target}.orc ${target}.sym
rm -rf file/static/
mkdir file/static
mkdir file/static/analysis/
mkdir file/static/analysis/subanalysis/
mkdir file/static/input_dir

export OUTPUT_STATIC_ANALYSIS_LOC_VAR=/FuzzerWithML/tests/file/static/
#export ANGORA_TAINT_RULE_LIST=${name}/zlib_abilist.txt
 
# export ANGORA_CUSTOM_FN_CONTEXT=0

bin_dir=../bin/
cd ${name}
export 
# ANGORA_USE_ASAN=1 USE_FAST=1  make -j 4 
# mv ./src/file file.fast 
# make clean

export ANGORA_TAINT_RULE_LIST=/FuzzerWithML/tests/file.txt
unset CC
unset CXX

CONFIG_FILE=/FuzzerWithML/tests/file/configure
if test -f "$CONFIG_FILE"; then
    echo "$CONFIG_FILE exists."
    rm ./configure
fi

autoreconf -i
head -n 3920 ./configure  > configure_new
tail -n +3962 configure >> configure_new
mv ./configure ./configure_old
cp configure_new configure
chmod +x configure


#make clean
CC=/FuzzerWithML/bin/angora-clang ./configure --disable-shared
ANGORA_USE_ASAN=1 USE_FAST=1  make -j 4 
mv ./src/file file.fast 
make clean

USE_TRACK=1 make -j 4 
mv ./src/file file.taint 
make clean

export SYMCC_OUTPUT_DIR=/tmp
CC=/FuzzerWithML/bin/symcc ./configure --disable-shared --without-docbook  
make -j 4 
mv ./src/file file.sym
make clean

CC=/FuzzerWithML/bin/static-analysis-clang  ./configure --disable-shared --without-docbook  
make -j 4 
mv ./src/file file.static
make clean

CC=/FuzzerWithML/bin/angora-clang-oracle ./configure --disable-shared --without-docbook  
make -j 4 
mv ./src/file file.orc

