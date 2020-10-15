FILE_NAME=${(%):-%x}
BIN_PATH="$( cd "$( dirname "$FILE_NAME" )" >/dev/null 2>&1 && pwd )"
ROOT_DIR=$(dirname $BIN_PATH)
export PATH=${HOME}/clang+llvm/bin:$PATH
export LD_LIBRARY_PATH=${HOME}/clang+llvm/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}
export CC=${ROOT_DIR}/bin/static-analysis-clang
export CXX=${ROOT_DIR}/bin/static-analysis-clang++
