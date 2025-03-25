#!/bin/bash         

path=$1

cd $path

# echo $path
# echo $class
# echo $method

mkdir -p output-details

mvn clean test > output-all.txt

mv output-all.txt ./output-details

