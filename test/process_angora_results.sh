#!/bin/sh
set -eux

cd ../fuzz_checker

name=$1
target=${name}/${name}
rm -rf ../test/output/
mkdir ../test/output
export LC_ALL=C.UTF-8
export LANG=C.UTF-8
pipenv run python ./executor.py -b ../test/${target}.orc -c ../test/${target}.sym -t ../test/output_angora/traces/ -o ../test/output/results/
