#!/bin/bash -x

for program in file djpeg jhead gif2png nm xmlwf tcpdump 
do
    echo "Processing $program"
    cd ../fuzz_checker
    pipenv run python ./create_raw_output.py -t ../angora_results/$program/output/traces/ -s ../results/static/$program/ -d ../angora_results/$program/results/ -d ../angora_results/$program/results_run2/ -d ../angora_results/$program/results_run3/ -d ../angora_results/$program/results_run4/ -d ../angora_results/$program/results_run5/ -o ../results/$program/raw_data.csv
done
