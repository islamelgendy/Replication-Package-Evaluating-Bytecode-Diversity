#!/bin/bash

project=$1
start=$2
end=$3

for i in $(seq $start $end) 
do
	sbatch run-hpc-reporting.sh $project $i
done


