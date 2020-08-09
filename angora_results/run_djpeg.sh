cd ../fuzz_checker
pipenv run python ./executor.py -b ../experiments/libjpeg/bin/djpeg -c ../experiments/sym/libjpeg/bin/djepg -t ../includes/Angora/experiments/djpeg/output/traces/ -o ../angora_results/djpeg/results/
