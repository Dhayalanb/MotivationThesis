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
rm -rf static/
mkdir static
mkdir static/analysis/
mkdir static/analysis/subanalysis/
mkdir static/input_dir

export OUTPUT_STATIC_ANALYSIS_LOC_VAR=/FuzzerWithML/tests/static
 
# export ANGORA_CUSTOM_FN_CONTEXT=0

bin_dir=../bin/
cd ${name}



CC=../${bin_dir}/angora-clang CXX=../${bin_dir}/angora-clang++ ./configure --disable-shared

ANGORA_USE_ASAN=1 USE_FAST=1  make -j 4 
mv djpeg  djpeg.fast 
make clean

USE_TRACK=1 make -j 4 
mv djpeg  djpeg.taint 
make clean


CC=../${bin_dir}/angora-clang-oracle  CXX=../${bin_dir}/angora-clang-oracle++ ./configure --disable-shared
make -j 4 
mv djpeg  djpeg.orc
make clean

CC=../${bin_dir}/static-analysis-clang CXX=../${bin_dir}/static-analysis-clang++ ./configure --disable-shared
make -j 4 
mv djpeg  djpeg.static
make clean

CC=../${bin_dir}/symcc CXX=../${bin_dir}/sym++ ./configure --disable-shared
make -j 4 
mv djpeg  djpeg.sym 
make clean



# USE_PIN=1 ${bin_dir}/angora-clang ${target}.c -lz -o ${target}.pin
#LLVM_COMPILER=clang wllvm -O0 -g ${target}.c -lz -o ${target}
#extract-bc ${target}
#opt -load ../bin/unfold-branch-pass.so -unfold_branch_pass < ${target}.bc > ${target}2.bc
#opt -load ../bin/angora-llvm-pass.so -angora_llvm_pass < ${target}2.bc > ${target}3.bc
#opt -load ../bin/angora-llvm-pass.so -angora_llvm_pass -TrackMode < ${target}2.bc > ${target}4.bc
#USE_FAST=1 ${bin_dir}/angora-clang ${target}.bc -lz -o ${target}.fast
#USE_TRACK=1 ${bin_dir}/angora-clang ${target}.bc -lz -o ${target}.taint
echo "Compile Done.."
cd ..



echo "Extracting CFG and conditions with distance by DEFAULT 4"
eval "python3 ../tools/extractCFG.py -f /FuzzerWithML/tests/static/ -d $depth"
# bash ../tools/convert_filename.sh /root/FuzzerWithML/tests/output/traces/
# bash ../tools/convert_to_json.sh /root/FuzzerWithML/tests/output/traces/

# args_file="./${name}/args"
# if [ ! -f ${args_file} ]; then
#     echo "Can't find args file in ${name}!"
# fi

target_="./libjpeg/djpeg"
args="@@"
echo $target
echo $name

cmd="timeout $timeout $envs $fuzzer -M 0 -A -i $input -o $output -j $num_jobs"
if [ $MODE = "llvm" ]; then
    cmd="$cmd -m llvm -t ${target_}.taint ${sync_afl} -- ${target_}.fast ${args}"
elif [ $MODE = "pin" ]; then
    cmd="$cmd -m pin -t ${target}.pin ${sync_afl} -- ${target}.fast ${args}"
fi;

echo "run: ${cmd}"
eval $cmd
