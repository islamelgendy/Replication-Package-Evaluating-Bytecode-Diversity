#!/bin/bash         

path=$1
class=$2
method=$3

cd $path

# echo $path
# echo $class
# echo $method

mkdir -p output-details

mvn clean -Dtest="${class}#${method}" test > output-${class}-${method}.txt

# mvn site

mv output-${class}-${method}.txt ./output-details

