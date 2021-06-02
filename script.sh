#!/bin/bash

for i in 100 1000 5000 10000 20000
do
  echo "Running simulation for ${i} corrupted entries"
  python3 covid.py $i >> results
done

exit 0
