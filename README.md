# MasterThesisCS2020
Contains all code used for the Master Thesis for the MSc Computer Science at the Vrije Universiteit Amsterdam.

In this thesis we created a framework to test the effectiveness of mutation strategies of fuzzers on a dataset of traces.
We used snippets of code from https://github.com/AngoraFuzzer/Angora.

## Building
Build all parts of the project by running:
```
./build/build.sh
```

Make sure you have the following programs:
- python3 
- pipenv
- cargo/rust
- C compiler

## Initialize the submodules

Clone the repository including the git submodules by running:

```
git submodule init
git submodule update
```
The submodules are located in the `includes` directory.

For the Angora submodule use the ``store-traces`` branch.

For the SymCC submodule use the ``partial-symbolic`` branch.

## Collecting traces

Follow the steps from the Angora repository to compile target binaries and run them against the Angora fuzzer.
The traces will be stored in the output directory in a directory called `traces`.

Convert these traces to json by using the `tools/convert_to_json.sh FILENAME`.

## Running the framework
In order to run the framework, compile the target binary three times:
- With the 'oracle' pass inserted into the compiler (See also `build/source_fuzzer.sh`)
- With the SymCC as compiler (See also `build/source_symcc.sh`)
- With the static analysis pass inserted into the compiler (See also `build/source_static_analysis.sh`)

The location of the static analysis results can be changed with the `ANGORA_OUTPUT_STATIC_ANALYSIS_LOC` variable.

Run the framework by running `pipenv run python ./executor.py -b ORACLE_BINARY_LOCATION -c SYMCC_BINARY_LOCATION -t TRACES_LOCATION -o OUTPUT_LOCATION` inside the `fuzz_checker` folder.

Inside the `fuzz_checker/defs.py` all environmental constants are available including the number of cores.

Once this run is done, the raw results can be processed into a csv file using the command:

```pipenv run python ./create_raw_output.py -t TRACES_LOCATION -s STATIC_FILES_LOCATION -d FUZZ_CHECKER_RESULTS_LOCATION  -o OUTPUT_NAME```

The results from multiple runs can be added together by adding multiple `-d` arguments. For example when you want to take the average of several runs. The average time is calculated and if one of the found results was flipped, all of them are.

## Data Analysis

The data analysis can be found in the `analysis` folder.
