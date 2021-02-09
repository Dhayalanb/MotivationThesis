#!/bin/sh
set -eux

cd ../fuzz_checker

name=$1
target=${name}/${name}
pipenv run python ./executor.py -b ../test/${target}.test -c ../test/${target}.sym -t ../test/output_angora/traces/ -o ../test/output/results/
