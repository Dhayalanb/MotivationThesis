

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

name=$1
timeout=$2
depth=$3 

name=$1
timeout=$2
depth=$3 

echo "Compile..."

target=${name}/${name}

# USE_PIN=1 ${bin_dir}/angora-clang ${target}.c -lz -o ${target}.pin
#LLVM_COMPILER=clang wllvm -O0 -g ${target}.c -lz -o ${target}
#extract-bc ${target}
#opt -load ../bin/unfold-branch-pass.so -unfold_branch_pass < ${target}.bc > ${target}2.bc
#opt -load ../bin/angora-llvm-pass.so -angora_llvm_pass < ${target}2.bc > ${target}3.bc
#opt -load ../bin/angora-llvm-pass.so -angora_llvm_pass -TrackMode < ${target}2.bc > ${target}4.bc
#USE_FAST=1 ${bin_dir}/angora-clang ${target}.bc -lz -o ${target}.fast
#USE_TRACK=1 ${bin_dir}/angora-clang ${target}.bc -lz -o ${target}.taint

mv file/src/file file/file.orc
echo "Compile Done.."

cd file
make clean
CC=/FuzzerWithML/bin/angora-clang ./configure --disable-shared
make
cp ./magic/magic.mgc /tmp/magic.mgc
cd ..
pwd
echo "Extracting CFG and conditions with distance by DEFAULT 4"
eval "python3 ../tools/extractCFG.py -f /FuzzerWithML/tests/file/static/ -d $depth"
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

