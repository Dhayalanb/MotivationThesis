#!/bin/sh
set -eux
../tools/convert_filename.sh ./output_angora/traces/
../tools/convert_to_json.sh ./output_angora/traces/
rm -rf ./test/output/