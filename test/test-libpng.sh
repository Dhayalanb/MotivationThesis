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

target=libpng/contrib/libtests/readpng

rm -f ${target}.fast ${target}.static ${target}.taint ${target}.orc ${target}.sym
rm -rf libpng/static/
mkdir libpng/static
mkdir libpng/static/analysis/
mkdir libpng/static/analysis/subanalysis/
mkdir libpng/static/input_dir

export OUTPUT_STATIC_ANALYSIS_LOC_VAR=/FuzzerWithML/tests/libpng/static/
#export ANGORA_TAINT_RULE_LIST=${name}/zlib_abilist.txt
 
# export ANGORA_CUSTOM_FN_CONTEXT=0


cd libpng
# cp ./configure_old ./configure
# head -n 3446 ./configure  > configure_new
# tail -n +3488 configure >> configure_new
# mv ./configure ./configure_old
# cp configure_new configure
# chmod +x configure

unset CC
unset CXX
unset ANGORA_TAINT_RULE_LIST

make clean
#export ANGORA_TAINT_RULE_LIST=/FuzzerWithML/tests/libpng/ablist.txt
CC=/FuzzerWithML/bin/angora-clang ./configure --disable-shared 
USE_FAST=1  make -j 4 
cd contrib/libtests
#export ANGORA_TAINT_RULE_LIST=/FuzzerWithML/tests/libpng/contrib/libtests/ablist.txt
/FuzzerWithML/bin/angora-clang readpng.c -lm -lz ../../.libs/libpng16.a -o readpng.fast
cd ../../
make clean

export ANGORA_TAINT_RULE_LIST=/FuzzerWithML/tests/libpng/ablist.txt
USE_TRACK=1  make -j 4 
cd contrib/libtests
export ANGORA_TAINT_RULE_LIST=/FuzzerWithML/tests/libpng/contrib/libtests/ablist.txt
USE_TRACK=1 /FuzzerWithML/bin/angora-clang readpng.c -lm -lz ../../.libs/libpng16.a -o readpng.taint
cd ../../
make clean


export SYMCC_OUTPUT_DIR=/tmp
export ANGORA_TAINT_RULE_LIST=/FuzzerWithML/tests/libpng/ablist.txt
CC=/FuzzerWithML/bin/symcc ./configure --disable-shared 
make -j 4 
cd contrib/libtests
export ANGORA_TAINT_RULE_LIST=/FuzzerWithML/tests/libpng/contrib/libtests/ablist.txt
/FuzzerWithML/bin/symcc readpng.c -lm -lz ../../.libs/libpng16.a -o readpng.sym
cd ../../
make clean


export ANGORA_TAINT_RULE_LIST=/FuzzerWithML/tests/libpng/ablist.txt
CC=/FuzzerWithML/bin/angora-clang-oracle ./configure --disable-shared 
make -j 4 
cd contrib/libtests
export ANGORA_TAINT_RULE_LIST=/FuzzerWithML/tests/libpng/contrib/libtests/ablist.txt
/FuzzerWithML/bin/angora-clang-oracle readpng.c -lm -lz ../../.libs/libpng16.a -o readpng.orc
cd ../../
make clean


export ANGORA_TAINT_RULE_LIST=/FuzzerWithML/tests/libpng/ablist.txt
CC=/FuzzerWithML/bin/static-analysis-clang ./configure --disable-shared 
make -j 4 
cd contrib/libtests
export ANGORA_TAINT_RULE_LIST=/FuzzerWithML/tests/libpng/contrib/libtests/ablist.txt
/FuzzerWithML/bin/static-analysis-clang readpng.c -lm -lz ../../.libs/libpng16.a -o readpng.sym
cd ../../
make clean

echo "Compile Done.."

cd .. 
echo "Extracting CFG and conditions with distance by DEFAULT 4"
eval "python3 ../tools/extractCFG.py -f /FuzzerWithML/tests/libpng/static/ -d $depth"
# bash ../tools/convert_filename.sh /root/FuzzerWithML/tests/output/traces/
# bash ../tools/convert_to_json.sh /root/FuzzerWithML/tests/output/traces/

# args_file="./${name}/args"
# if [ ! -f ${args_file} ]; then
#     echo "Can't find args file in ${name}!"
# fi

args="@@"
echo $target
echo $name

cmd="timeout $timeout $envs $fuzzer -M 0 -A -i $input -o $output -j $num_jobs"
if [ $MODE = "llvm" ]; then
    cmd="$cmd -m llvm -t ${target}.taint ${sync_afl} -- ${target}.fast -m ./tmp/magic.mgc${args}"
elif [ $MODE = "pin" ]; then
    cmd="$cmd -m pin -t ${target}.pin ${sync_afl} -- ${target}.fast ${args}"
fi;

echo "run: ${cmd}"
eval $cmd

