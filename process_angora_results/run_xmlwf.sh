cd ../fuzz_checker
pipenv run python ./executor.py -j 8 -b ../experiments/libexpat/bin/xmlwf -c ../experiments/sym/libexpat/bin/xmlwf -t ../angora_results/xmlwf/output/traces/ -o ../angora_results/xmlwf/results/
