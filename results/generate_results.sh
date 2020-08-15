#!/bin/bash -x

for program in file djpeg jhead gif2png nm xmlwf 
do
    echo "Processing $program"
    cd ../fuzz_checker
    pipenv run python ./output_parser.py -i ../angora_results/$program/results/ -o ../results/$program/
done