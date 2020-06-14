#!/bin/bash
for FILE in `ls $1/track_id:*`
do
../executor/target/release/helper $FILE > $FILE.json
done
