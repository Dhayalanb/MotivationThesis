#!/bin/bash
for FILE in `ls $1/track_id_*`
do
../executor/target/release/helper $FILE > $FILE.json
done
