#!/bin/bash         

export PATH=$PATH:/home/islam/MyWork/Code/defects4j/framework/bin

path=$1
classes=$2
tool=$3

cd $path

mvn -Dtest="${classes}" test > output-${tool}.txt

