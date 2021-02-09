#!/bin/sh
set -eux

cd ../fuzz_checker
pipenv run python ./create_raw_output.py -t ../test/output_angora/traces/ -s ../test/output/static/ -d ../test/output/results/ -o ../test/output/raw_data.csv
