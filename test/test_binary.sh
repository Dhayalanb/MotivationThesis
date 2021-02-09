#!/bin/sh
set -eux

echo "Compiling and running for angora"
./run_angora $1
echo "Compiling for test framework"
./compile_for_framework $1
echo "Preprocessing angora output"
./preprocess_angora_results $1
echo "Running test framework"
./process_angora_results $1
echo "Creating output"
./postcess_angora_results $1
echo "Done"
echo "The results can be found in output/raw_data.csv"
