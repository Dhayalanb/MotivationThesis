cd ../fuzz_checker
pipenv run python ./executor.py -b ../experiments/binutils/bin/size -c ../experiments/sym/binutils/bin/size -t ../angora_results/size/output/traces/ -o ../angora_results/size/results/
